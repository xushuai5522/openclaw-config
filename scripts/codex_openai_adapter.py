#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
import time
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


DEFAULT_MODELS = [
    "gpt-5.4",
    "gpt-5.3-codex",
    "gpt-5.2-codex",
    "gpt-5.1-codex",
]
def load_models() -> list[str]:
    raw = os.environ.get("CODEX_LOCAL_MODELS", "")
    if not raw.strip():
        return DEFAULT_MODELS[:]
    models = [item.strip() for item in raw.split(",") if item.strip()]
    return models or DEFAULT_MODELS[:]


CODEX_BIN = os.environ.get("CODEX_BIN", "/Users/xs/Downloads/codex-x86_64-apple-darwin")
API_KEY = os.environ.get("CODEX_LOCAL_API_KEY", "")
WORKDIR = os.environ.get("CODEX_LOCAL_WORKDIR", "/Users/xs")
BIND = os.environ.get("CODEX_LOCAL_BIND", "127.0.0.1")
PORT = int(os.environ.get("CODEX_LOCAL_PORT", "18888"))
SANDBOX = os.environ.get("CODEX_LOCAL_SANDBOX", "read-only")
APPROVAL = os.environ.get("CODEX_LOCAL_APPROVAL", "never")
DEFAULT_REASONING = os.environ.get("CODEX_LOCAL_DEFAULT_REASONING", "low").strip() or None
DEFAULT_VERBOSITY = os.environ.get("CODEX_LOCAL_DEFAULT_VERBOSITY", "").strip() or None
MODELS = load_models()
MAX_SYSTEM_CHARS = int(os.environ.get("CODEX_LOCAL_MAX_SYSTEM_CHARS", "5000"))
MAX_MESSAGE_CHARS = int(os.environ.get("CODEX_LOCAL_MAX_MESSAGE_CHARS", "3000"))
MAX_CONVERSATION_MESSAGES = int(os.environ.get("CODEX_LOCAL_MAX_CONVERSATION_MESSAGES", "6"))
MAX_PROMPT_CHARS = int(os.environ.get("CODEX_LOCAL_MAX_PROMPT_CHARS", "16000"))


def message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(content)


def trim_text(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    head = max(limit - 32, 0)
    return text[:head].rstrip() + "\n...[truncated]..."


def build_prompt(messages) -> str:
    normalized = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "user")).lower()
        text = message_text(item.get("content", ""))
        if not text:
            continue
        normalized.append((role, text.strip()))

    if not normalized:
        return "USER:\nReply briefly."

    latest_system = ""
    conversation = []
    for role, text in normalized:
        if role == "system":
            latest_system = text
            continue
        conversation.append((role, text))

    conversation = conversation[-MAX_CONVERSATION_MESSAGES:]
    sections = []
    if latest_system:
        sections.append(f"SYSTEM:\n{trim_text(latest_system, MAX_SYSTEM_CHARS)}")

    for role, text in conversation:
        sections.append(f"{role.upper()}:\n{trim_text(text, MAX_MESSAGE_CHARS)}")

    sections.append(
        "SYSTEM:\n"
        "Prior context may be truncated for latency. "
        "Answer the latest user request directly, and only rely on older context if it is clearly required."
    )

    prompt = "\n\n".join(sections)
    if len(prompt) <= MAX_PROMPT_CHARS:
        return prompt

    keep = sections[:1]
    tail = sections[1:]
    compact_tail = []
    total = len("\n\n".join(keep)) if keep else 0
    for section in reversed(tail):
        section_len = len(section) + 2
        if total + section_len > MAX_PROMPT_CHARS:
            break
        compact_tail.append(section)
        total += section_len
    compact_tail.reverse()
    compact = keep + compact_tail
    return "\n\n".join(compact)


def run_codex(model: str, prompt: str, request: dict) -> tuple[str, dict]:
    reasoning = request.get("reasoning_effort") or DEFAULT_REASONING
    verbosity = request.get("verbosity") or DEFAULT_VERBOSITY
    timeout = int(request.get("timeout", 180))
    cmd = [
        "/usr/bin/script",
        "-q",
        "/dev/null",
        CODEX_BIN,
        "exec",
        "--skip-git-repo-check",
        "--json",
        "--color",
        "never",
        "-m",
        model,
        "-s",
        SANDBOX,
        "-C",
        WORKDIR,
    ]
    if APPROVAL:
        cmd.extend(["-c", f'approval_mode="{APPROVAL}"'])
    if reasoning:
        cmd.extend(["-c", f'model_reasoning_effort="{reasoning}"'])
    if verbosity:
        cmd.extend(["-c", f'model_verbosity="{verbosity}"'])
    cmd.append(prompt)

    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=os.environ.copy(),
    )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    usage = {}
    errors = []
    content = ""
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if "{" in line:
            line = line[line.find("{") :]
        if not line or not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
        elif event.get("type") == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message" and item.get("text"):
                content = str(item["text"]).strip()
        elif event.get("type") == "error":
            errors.append(event.get("message") or "Unknown Codex error")

    if proc.returncode != 0 or not content:
        detail = errors[-1] if errors else stderr.strip() or stdout.strip() or f"codex exit {proc.returncode}"
        raise RuntimeError(detail)

    return content, usage


class Handler(BaseHTTPRequestHandler):
    server_version = "CodexLocalOpenAI/0.1"

    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def unauthorized(self) -> None:
        self.send_json(HTTPStatus.UNAUTHORIZED, {"error": {"message": "Unauthorized", "type": "auth_error"}})

    def bad_request(self, message: str) -> None:
        self.send_json(HTTPStatus.BAD_REQUEST, {"error": {"message": message, "type": "invalid_request_error"}})

    def check_auth(self) -> bool:
        if not API_KEY:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        token = header[7:].strip()
        return token == API_KEY

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_json(HTTPStatus.OK, {"ok": True})
            return
        if self.path == "/v1/models":
            if not self.check_auth():
                self.unauthorized()
                return
            payload = {
                "object": "list",
                "data": [
                    {
                        "id": model,
                        "object": "model",
                        "created": 0,
                        "owned_by": "codex-local",
                    }
                    for model in MODELS
                ],
            }
            self.send_json(HTTPStatus.OK, payload)
            return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": {"message": "Not found", "type": "not_found"}})

    def do_POST(self) -> None:
        try:
            if self.path != "/v1/chat/completions":
                self.send_json(HTTPStatus.NOT_FOUND, {"error": {"message": "Not found", "type": "not_found"}})
                return
            if not self.check_auth():
                self.unauthorized()
                return
            try:
                request = self.read_json()
            except json.JSONDecodeError:
                self.bad_request("Invalid JSON body")
                return
            model = request.get("model")
            if not model:
                self.bad_request("Missing model")
                return
            if model not in MODELS:
                self.bad_request(f"Unsupported model: {model}")
                return

            prompt = build_prompt(request.get("messages") or [])
            try:
                content, usage = run_codex(model, prompt, request)
            except subprocess.TimeoutExpired:
                self.send_json(HTTPStatus.GATEWAY_TIMEOUT, {"error": {"message": "Codex timed out", "type": "timeout_error"}})
                return
            except Exception as exc:
                print(f"upstream_error model={model}: {exc}", file=sys.stderr, flush=True)
                self.send_json(HTTPStatus.BAD_GATEWAY, {"error": {"message": str(exc), "type": "upstream_error"}})
                return

            created = int(time.time())
            response_id = f"chatcmpl-codex-local-{created}"
            if request.get("stream"):
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                role_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
                }
                self.wfile.write(f"data: {json.dumps(role_chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
                if content:
                    content_chunk = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
                    }
                    self.wfile.write(f"data: {json.dumps(content_chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
                final_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                }
                self.wfile.write(f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
                self.wfile.write(b"data: [DONE]\n\n")
                return

            prompt_tokens = int(usage.get("input_tokens") or 0)
            completion_tokens = int(usage.get("output_tokens") or 0)
            payload = {
                "id": response_id,
                "object": "chat.completion",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }
            self.send_json(HTTPStatus.OK, payload)
        except BrokenPipeError:
            return
        except Exception:
            traceback.print_exc()
            try:
                self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": {"message": "Internal adapter error", "type": "server_error"}})
            except BrokenPipeError:
                return


def main() -> None:
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    print(
        f"codex-local adapter listening on http://{BIND}:{PORT} "
        f"models={','.join(MODELS)} workdir={shlex.quote(WORKDIR)}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
