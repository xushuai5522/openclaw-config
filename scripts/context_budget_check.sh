#!/usr/bin/env bash
set -euo pipefail

cd /Users/xs/.openclaw/workspace

check() {
  local file="$1" max="$2"
  local n
  n=$(wc -l < "$file" | tr -d ' ')
  if [ "$n" -le "$max" ]; then
    printf "✅ %-18s %4s/%s\n" "$file" "$n" "$max"
  else
    printf "❌ %-18s %4s/%s  (超预算)\n" "$file" "$n" "$max"
  fi
}

echo "== Context Budget Check =="
check AGENTS.md 120
check SOUL.md 120
check MEMORY.md 100
check TOOLS.md 80

echo
echo "建议：超预算时按 CONTEXT_BUDGET.md 顺序处理（删重复→改引用→迁内容→再压缩）"
echo "建议：会话发钝时执行 /compact；周检执行 /context list"
