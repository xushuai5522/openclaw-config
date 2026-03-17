#!/bin/zsh
set -euo pipefail

OPENCLAW_BIN="/Users/xs/Documents/node-v24.14.0-darwin-x64/bin/openclaw"
LOG_DIR="$HOME/.openclaw/logs"
COOLDOWN_SECONDS=600
LAST_START_FILE="$LOG_DIR/gateway-last-start.ts"

mkdir -p "$LOG_DIR"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
NOW_TS="$(date +%s)"

if lsof -nP -iTCP:18789 -sTCP:LISTEN >/dev/null 2>&1 || pgrep -af "openclaw-gateway|bin/openclaw gateway|/bin/openclaw gateway" >/dev/null 2>&1; then
  echo "$STAMP gateway_ok" >> "$LOG_DIR/gateway-watchdog.log"
  exit 0
fi

LAST_TS=0
if [ -f "$LAST_START_FILE" ]; then
  LAST_RAW="$(cat "$LAST_START_FILE" 2>/dev/null || true)"
  if [[ "$LAST_RAW" == <-> ]]; then
    LAST_TS="$LAST_RAW"
  fi
fi

ELAPSED=$((NOW_TS - LAST_TS))
if [ "$LAST_TS" -gt 0 ] && [ "$ELAPSED" -lt "$COOLDOWN_SECONDS" ]; then
  echo "$STAMP gateway_down_cooldown_skip elapsed=${ELAPSED}s cooldown=${COOLDOWN_SECONDS}s" >> "$LOG_DIR/gateway-watchdog.log"
  exit 0
fi

{
  echo "$STAMP gateway_down_try_start"
  echo "$NOW_TS" > "$LAST_START_FILE"
  "$OPENCLAW_BIN" gateway start >> "$LOG_DIR/gateway-manual-start.log" 2>&1 || true
  sleep 5
  if lsof -nP -iTCP:18789 -sTCP:LISTEN >/dev/null 2>&1 || pgrep -af "openclaw-gateway|bin/openclaw gateway|/bin/openclaw gateway" >/dev/null 2>&1; then
    echo "$STAMP gateway_restart_ok"
  else
    echo "$STAMP gateway_restart_failed"
  fi
} >> "$LOG_DIR/gateway-watchdog.log" 2>&1
