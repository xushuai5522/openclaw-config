#!/usr/bin/env python3
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path('/Users/xs/.openclaw/workspace')

PROJECT_ALIASES = {
    '人人租': 'rrz',
    'rrz': 'rrz',
    'openclaw': 'openclaw-ops',
    'session': 'openclaw-ops',
    'gateway': 'openclaw-ops',
    '小红书': 'xiaohongshu',
    '红书': 'xiaohongshu',
    'xiaohongshu': 'xiaohongshu',
}

PRIORITY_WEIGHT = {
    'high': 3,
    'medium': 2,
    'low': 1,
}


def tokenize(text: str):
    text = text.lower()
    parts = re.split(r'[^\w\u4e00-\u9fff]+', text)
    tokens = [p for p in parts if p]

    cjk_chunks = [p for p in tokens if re.fullmatch(r'[\u4e00-\u9fff]+', p)]
    cjk_ngrams = []
    for chunk in cjk_chunks:
        if len(chunk) <= 4:
            cjk_ngrams.append(chunk)
        for n in (2, 3, 4):
            if len(chunk) >= n:
                cjk_ngrams.extend(chunk[i:i+n] for i in range(len(chunk) - n + 1))

    token_bigrams = [tokens[i] + tokens[i + 1] for i in range(len(tokens) - 1)]
    return set(tokens + token_bigrams + cjk_ngrams)


def textify(*fields):
    return ' '.join([
        json.dumps(f, ensure_ascii=False) if not isinstance(f, str) else f
        for f in fields
    ]).lower()


def score_text(query_tokens, *fields):
    hay = textify(*fields)
    score = 0
    for tok in query_tokens:
        if tok and tok in hay:
            score += 1
    return score


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def project_cards():
    rows = []
    for p in (ROOT / 'projects').glob('*.md'):
        text = p.read_text(encoding='utf-8')
        rows.append({'path': str(p.relative_to(ROOT)), 'text': text, 'name': p.stem})
    return rows


def detect_projects(query: str, query_tokens):
    hits = set()
    hay = query.lower()
    for alias, project in PROJECT_ALIASES.items():
        if alias.lower() in hay or alias.lower() in query_tokens:
            hits.add(project)
    return hits


def extract_section(text: str, heading: str):
    m = re.search(rf'(^##\s+{re.escape(heading)}\n)(.*?)(?=\n##\s+|\Z)', text, flags=re.M | re.S)
    if not m:
        return []
    body = m.group(2).strip()
    lines = [ln.strip('- ').strip() for ln in body.splitlines() if ln.strip()]
    return [ln for ln in lines if ln]


def summarize_card(card_text: str):
    return {
        'recommended': extract_section(card_text, '当前推荐默认策略')[:5],
        'pitfalls': extract_section(card_text, '不要再走的旧路')[:4],
        'checklist': extract_section(card_text, '开场检查清单')[:5],
    }


def read_memory_texts():
    memory_text = (ROOT / 'MEMORY.md').read_text(encoding='utf-8')
    today = date.today()
    candidates = [ROOT / 'memory' / f'{today.isoformat()}.md', ROOT / 'memory' / f'{(today - timedelta(days=1)).isoformat()}.md']
    daily = None
    for p in candidates:
        if p.exists():
            daily = {'path': str(p.relative_to(ROOT)), 'text': p.read_text(encoding='utf-8')}
            break
    return memory_text, daily


def top_memory_snippets(text: str, query_tokens, label: str, limit=3):
    snippets = []
    for block in re.split(r'\n\n+', text):
        block = block.strip()
        if not block:
            continue
        score = score_text(query_tokens, block)
        if score > 0:
            one_line = re.sub(r'\s+', ' ', block)
            snippets.append((score, one_line[:180], label))
    snippets.sort(key=lambda x: x[0], reverse=True)
    return snippets[:limit]


def main(query: str):
    q = tokenize(query)
    project_hints = detect_projects(query, q)

    playbooks = load_json(ROOT / 'registry/playbooks.json')
    wins = load_jsonl(ROOT / 'recent/wins.jsonl')
    failures = load_jsonl(ROOT / 'recent/failures.jsonl')
    cards = project_cards()
    memory_text, daily = read_memory_texts()

    playbook_hits = []
    for p in playbooks:
        score = score_text(q, p.get('name', ''), p.get('summary', ''), p.get('triggers', []), p.get('for_projects', []), p.get('do', []), p.get('avoid', []))
        if project_hints and (set(p.get('for_projects', [])) & project_hints):
            score += 6
        score += PRIORITY_WEIGHT.get(p.get('priority', 'low'), 0)
        playbook_hits.append((score, p))
    playbook_hits.sort(key=lambda x: x[0], reverse=True)

    win_hits = []
    for w in wins:
        score = score_text(q, w.get('task_type', ''), w.get('project', ''), w.get('pattern', ''), w.get('applies_when', []), w.get('tags', []), w.get('source', ''))
        if project_hints and w.get('project') in project_hints:
            score += 5
        if w.get('confidence') == 'high':
            score += 2
        win_hits.append((score, w))
    win_hits.sort(key=lambda x: x[0], reverse=True)

    fail_hits = []
    for r in failures:
        score = score_text(q, r.get('task_type', ''), r.get('project', ''), r.get('failure', ''), r.get('cause', ''), r.get('avoid', ''), r.get('applies_when', []), r.get('tags', []), r.get('source', ''))
        if project_hints and r.get('project') in project_hints:
            score += 5
        if r.get('confidence') == 'high':
            score += 2
        fail_hits.append((score, r))
    fail_hits.sort(key=lambda x: x[0], reverse=True)

    card_hits = []
    for c in cards:
        score = score_text(q, c['path'], c['text'])
        if project_hints and c['name'] in project_hints:
            score += 8
        card_hits.append((score, c))
    card_hits.sort(key=lambda x: x[0], reverse=True)

    memory_hits = top_memory_snippets(memory_text, q, 'MEMORY.md')
    daily_hits = top_memory_snippets(daily['text'], q, daily['path']) if daily else []

    print(f'查询: {query}')
    if project_hints:
        print(f'命中项目: {", ".join(sorted(project_hints))}')

    print('\n=== 先看这些项目卡 ===')
    for score, c in card_hits[:3]:
        if score < 2:
            continue
        print(f'- {c["path"]} (score={score})')
        summary = summarize_card(c['text'])
        for step in summary['recommended'][:3]:
            print(f'  推荐: {step}')
        for pit in summary['pitfalls'][:2]:
            print(f'  避坑: {pit}')
        for item in summary['checklist'][:2]:
            print(f'  检查: {item}')

    print('\n=== 推荐默认剧本 ===')
    for score, p in playbook_hits[:4]:
        if score < 4:
            continue
        print(f'- {p["name"]} [{p.get("priority", "?")}] (score={score})')
        print(f'  {p["summary"]}')
        for step in p.get('do', [])[:4]:
            print(f'  · 做: {step}')
        for item in p.get('avoid', [])[:2]:
            print(f'  · 别: {item}')

    print('\n=== 最近成功经验（优先复用） ===')
    for score, w in win_hits[:4]:
        if score < 3:
            continue
        print(f'- {w["date"]} [{w.get("project", "?")}] {w["pattern"]} (score={score})')

    print('\n=== 最近失败模式（优先避开） ===')
    for score, r in fail_hits[:4]:
        if score < 3:
            continue
        print(f'- {r["date"]} [{r.get("project", "?")}] {r["failure"]} (score={score})')
        print(f'  原因: {r.get("cause", "") or "-"}')
        print(f'  避免: {r.get("avoid", "") or "-"}')

    print('\n=== 长期记忆提醒 ===')
    for score, snippet, label in memory_hits[:3]:
        if score < 2:
            continue
        print(f'- {label}: {snippet} (score={score})')

    daily_hits = [item for item in daily_hits if item[0] >= 2]
    if daily_hits:
        print('\n=== 今日日记相关 ===')
        for score, snippet, label in daily_hits[:3]:
            print(f'- {label}: {snippet} (score={score})')


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python3 scripts/context_recall.py <任务描述>')
        raise SystemExit(1)
    main(' '.join(sys.argv[1:]))
