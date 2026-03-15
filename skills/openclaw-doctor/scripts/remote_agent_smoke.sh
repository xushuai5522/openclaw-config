#!/bin/bash
set -euo pipefail

# 用法：remote_agent_smoke.sh <host> <key_path>
HOST="${1:-}"
KEY="${2:-}"

if [[ -z "$HOST" || -z "$KEY" ]]; then
  echo "usage: $0 <host> <key_path>" >&2
  exit 1
fi

TMP_SCRIPT="$(mktemp)"
cat > "$TMP_SCRIPT" <<'SH'
#!/bin/bash
set -e
export PATH="/Users/xs/Documents/node-v24.14.0-darwin-x64/bin:$HOME/.local/bin:$PATH"
openclaw agent --agent main --message "用 exec 执行命令: echo TOOL_OK 。不要解释，只返回执行结果。" --thinking low --timeout 120 --json > /tmp/agent_smoke.json
python3 - <<'PY'
import json
obj=json.load(open('/tmp/agent_smoke.json'))
print(obj['result']['payloads'][0].get('text',''))
PY
SH

scp -i "$KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o PreferredAuthentications=publickey "$TMP_SCRIPT" "$HOST:/tmp/remote_agent_smoke.sh" >/dev/null
ssh -i "$KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o PreferredAuthentications=publickey "$HOST" 'bash /tmp/remote_agent_smoke.sh'
rm -f "$TMP_SCRIPT"
