#!/usr/bin/env python3
import json, os, uuid, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
from pathlib import Path

CONFIG = json.loads((Path.home()/'.openclaw'/'openclaw.json').read_text())
YES = CONFIG['models']['providers']['yescode-gpt']
OPENAI_BASE = YES['baseUrl'].rstrip('/')
OPENAI_KEY = YES['apiKey']
DEFAULT_MODEL = os.environ.get('CLAUDE_YESCODE_MODEL', 'gpt-5.4')
PORT = int(os.environ.get('CLAUDE_YESCODE_BRIDGE_PORT', '8765'))


def json_resp(handler, code, obj):
    data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def openai_chat(payload):
    req = Request(
        OPENAI_BASE + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_KEY}',
        },
        method='POST'
    )
    with urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))


def flatten_content(content):
    if isinstance(content, str):
        return content
    out = []
    for block in content or []:
        if isinstance(block, dict):
            if block.get('type') == 'text':
                out.append(block.get('text', ''))
            elif block.get('type') == 'tool_result':
                c = block.get('content', '')
                if isinstance(c, list):
                    out.append(flatten_content(c))
                else:
                    out.append(str(c))
            elif 'text' in block:
                out.append(str(block.get('text', '')))
    return '\n'.join(x for x in out if x)


def anthropic_to_openai(body):
    msgs = []
    system = body.get('system')
    if isinstance(system, str) and system:
        msgs.append({'role': 'system', 'content': system})
    elif isinstance(system, list):
        sys_text = flatten_content(system)
        if sys_text:
            msgs.append({'role': 'system', 'content': sys_text})

    tools = []
    tool_map = {}
    for t in body.get('tools', []) or []:
        name = t.get('name')
        if not name:
            continue
        schema = t.get('input_schema') or {'type': 'object', 'properties': {}}
        tool_map[name] = t
        tools.append({
            'type': 'function',
            'function': {
                'name': name,
                'description': t.get('description', ''),
                'parameters': schema,
            }
        })

    for m in body.get('messages', []):
        role = m.get('role', 'user')
        content = m.get('content', '')
        if role == 'assistant' and isinstance(content, list):
            text_parts = []
            tool_calls = []
            for block in content:
                if block.get('type') == 'text':
                    if block.get('text'):
                        text_parts.append(block['text'])
                elif block.get('type') == 'tool_use':
                    raw_id = block.get('id', 'fc_' + uuid.uuid4().hex[:24])
                    tool_calls.append({
                        'id': ('fc_' + raw_id[5:]) if raw_id.startswith('call_') else (raw_id if raw_id.startswith('fc_') else 'fc_' + raw_id),
                        'type': 'function',
                        'function': {
                            'name': block.get('name', ''),
                            'arguments': json.dumps(block.get('input', {}), ensure_ascii=False)
                        }
                    })
            msg = {'role': 'assistant'}
            if text_parts:
                msg['content'] = '\n'.join(text_parts)
            if tool_calls:
                msg['tool_calls'] = tool_calls
            msgs.append(msg)
        elif role == 'user' and isinstance(content, list):
            tool_results = [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_result']
            other_text = [b for b in content if not (isinstance(b, dict) and b.get('type') == 'tool_result')]
            text = flatten_content(other_text)
            if text:
                msgs.append({'role': 'user', 'content': text})
            for tr in tool_results:
                raw_id = tr.get('tool_use_id', 'fc_' + uuid.uuid4().hex[:24])
                tool_call_id = ('fc_' + raw_id[5:]) if isinstance(raw_id, str) and raw_id.startswith('call_') else (raw_id if isinstance(raw_id, str) and raw_id.startswith('fc_') else 'fc_' + str(raw_id))
                msgs.append({
                    'role': 'tool',
                    'tool_call_id': tool_call_id,
                    'content': flatten_content(tr.get('content', ''))
                })
        else:
            msgs.append({'role': role, 'content': flatten_content(content) if isinstance(content, list) else content})

    payload = {
        'model': body.get('model') or DEFAULT_MODEL,
        'messages': msgs,
        'stream': False,
    }
    if body.get('max_tokens') is not None:
        payload['max_tokens'] = body['max_tokens']
    if tools:
        payload['tools'] = tools
        tc = body.get('tool_choice')
        if isinstance(tc, dict) and tc.get('type') == 'tool' and tc.get('name'):
            payload['tool_choice'] = {'type': 'function', 'function': {'name': tc['name']}}
        elif tc == 'any':
            payload['tool_choice'] = 'auto'
        elif tc == 'auto':
            payload['tool_choice'] = 'auto'
    return payload


def openai_to_anthropic(resp, requested_model):
    choice = (resp.get('choices') or [{}])[0]
    msg = choice.get('message') or {}
    content = []
    if msg.get('content'):
        content.append({'type': 'text', 'text': msg['content']})
    for tc in msg.get('tool_calls') or []:
        args = tc.get('function', {}).get('arguments', '{}')
        try:
            parsed = json.loads(args) if isinstance(args, str) else args
        except Exception:
            parsed = {'raw_arguments': args}
        raw_id = tc.get('id', 'fc_' + uuid.uuid4().hex[:24])
        tool_id = ('fc_' + raw_id[5:]) if isinstance(raw_id, str) and raw_id.startswith('call_') else (raw_id if isinstance(raw_id, str) and raw_id.startswith('fc_') else 'fc_' + str(raw_id))
        content.append({
            'type': 'tool_use',
            'id': tool_id,
            'name': tc.get('function', {}).get('name', ''),
            'input': parsed,
        })
    if not content:
        content = [{'type': 'text', 'text': ''}]
    return {
        'id': 'msg_' + uuid.uuid4().hex,
        'type': 'message',
        'role': 'assistant',
        'model': requested_model,
        'content': content,
        'stop_reason': 'tool_use' if any(c.get('type') == 'tool_use' for c in content) else 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': resp.get('usage', {}).get('prompt_tokens', 0),
            'output_tokens': resp.get('usage', {}).get('completion_tokens', 0),
        }
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ['/health', '/v1/health']:
            return json_resp(self, 200, {'ok': True, 'provider': 'yescode-gpt', 'model': DEFAULT_MODEL})
        if path == '/v1/models':
            return json_resp(self, 200, {
                'data': [
                    {'id': DEFAULT_MODEL, 'type': 'model', 'display_name': DEFAULT_MODEL, 'created_at': '2026-01-01T00:00:00Z'},
                    {'id': 'claude-opus-4-6', 'type': 'model', 'display_name': 'claude-opus-4-6', 'created_at': '2026-01-01T00:00:00Z'},
                    {'id': 'claude-sonnet-4-6', 'type': 'model', 'display_name': 'claude-sonnet-4-6', 'created_at': '2026-01-01T00:00:00Z'}
                ],
                'has_more': False,
                'first_id': DEFAULT_MODEL,
                'last_id': 'claude-sonnet-4-6'
            })
        return json_resp(self, 404, {'error': {'type': 'not_found', 'message': f'Invalid URL ({self.command} {self.path})'}})

    def do_POST(self):
        path = urlparse(self.path).path
        n = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(n) if n else b'{}'
        try:
            body = json.loads(raw.decode('utf-8') or '{}')
        except Exception:
            return json_resp(self, 400, {'error': {'type': 'invalid_request_error', 'message': 'Invalid JSON'}})

        if path == '/v1/messages/count_tokens':
            text = flatten_content(body.get('messages', [])) if isinstance(body.get('messages'), list) else json.dumps(body.get('messages', ''))
            est = max(1, len(text) // 4)
            return json_resp(self, 200, {'input_tokens': est})

        if path == '/v1/messages':
            requested_model = body.get('model') or DEFAULT_MODEL
            body['model'] = DEFAULT_MODEL if requested_model.startswith('claude-') else requested_model
            payload = anthropic_to_openai(body)
            try:
                resp = openai_chat(payload)
                return json_resp(self, 200, openai_to_anthropic(resp, requested_model))
            except HTTPError as e:
                try:
                    detail = e.read().decode('utf-8', errors='ignore')
                except Exception:
                    detail = str(e)
                return json_resp(self, e.code, {'error': {'type': 'upstream_error', 'message': detail}})
            except Exception as e:
                return json_resp(self, 500, {'error': {'type': 'internal_server_error', 'message': str(e)}})

        return json_resp(self, 404, {'error': {'type': 'not_found', 'message': f'Invalid URL ({self.command} {self.path})'}})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    print(f'Claude-Yescode bridge listening on http://127.0.0.1:{PORT}', flush=True)
    server.serve_forever()
