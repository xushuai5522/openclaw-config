#!/bin/zsh
set -euo pipefail
OPENCLAW_BIN="/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
if lsof -nP -iTCP:18789 -sTCP:LISTEN >/dev/null 2>&1 || pgrep -af "openclaw-gateway|bin/openclaw gateway|/bin/openclaw gateway" >/dev/null 2>&1; then
  echo "$STAMP gateway_ok" >> "$LOG_DIR/gateway-watchdog.log"
  exit 0
fi
{
  echo "$STAMP gateway_down_try_start"
  nohup "$OPENCLAW_BIN" gateway >> "$LOG_DIR/gateway-manual-start.log" 2>&1 &
  sleep 5
  if lsof -nP -iTCP:18789 -sTCP:LISTEN >/dev/null 2>&1 || pgrep -af "openclaw-gateway|bin/openclaw gateway|/bin/openclaw gateway" >/dev/null 2>&1; then
    echo "$STAMP gateway_restart_ok"
  else
    echo "$STAMP gateway_restart_failed"
  fi
} >> "$LOG_DIR/gateway-watchdog.log" 2>&1
