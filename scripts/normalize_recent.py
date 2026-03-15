#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('/Users/xs/.openclaw/workspace')
RECENT = ROOT / 'recent'

DEFAULTS = {
    'confidence': 'medium',
    'source': '',
    'tags': [],
    'review_after': '',
}

WIN_KEYS = ['date', 'task_type', 'project', 'pattern', 'applies_when', 'source', 'confidence', 'tags', 'review_after']
FAIL_KEYS = ['date', 'task_type', 'project', 'failure', 'cause', 'avoid', 'applies_when', 'source', 'confidence', 'tags', 'review_after']


def load_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def dump_jsonl(path: Path, rows: list[dict], keys: list[str]):
    lines = []
    for row in rows:
        clean = {k: row.get(k, '' if k != 'tags' and k != 'applies_when' else []) for k in keys}
        lines.append(json.dumps(clean, ensure_ascii=False))
    path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')


def normalize_win(row: dict):
    out = {**DEFAULTS, **row}
    out.setdefault('applies_when', [])
    if not isinstance(out['applies_when'], list):
        out['applies_when'] = [str(out['applies_when'])]
    if not isinstance(out['tags'], list):
        out['tags'] = [str(out['tags'])]
    out['task_type'] = str(out.get('task_type', '')).strip()
    out['project'] = str(out.get('project', 'global')).strip() or 'global'
    out['pattern'] = str(out.get('pattern', '')).strip()
    if not out['tags']:
        out['tags'] = [out['project'], out['task_type']]
    return out


def normalize_fail(row: dict):
    out = {**DEFAULTS, **row}
    out.setdefault('applies_when', [])
    if not isinstance(out['applies_when'], list):
        out['applies_when'] = [str(out['applies_when'])]
    if not isinstance(out['tags'], list):
        out['tags'] = [str(out['tags'])]
    out['task_type'] = str(out.get('task_type', '')).strip()
    out['project'] = str(out.get('project', 'global')).strip() or 'global'
    out['failure'] = str(out.get('failure', '')).strip()
    out['cause'] = str(out.get('cause', '')).strip()
    out['avoid'] = str(out.get('avoid', '')).strip()
    if not out['tags']:
        out['tags'] = [out['project'], out['task_type']]
    return out


def dedupe(rows: list[dict], key_fields: list[str]):
    seen = set()
    out = []
    for row in rows:
        key = tuple(row.get(k, '') if not isinstance(row.get(k, ''), list) else tuple(row.get(k, [])) for k in key_fields)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def main():
    wins_path = RECENT / 'wins.jsonl'
    fails_path = RECENT / 'failures.jsonl'

    wins = [normalize_win(x) for x in load_jsonl(wins_path)]
    fails = [normalize_fail(x) for x in load_jsonl(fails_path)]

    wins = dedupe(wins, ['project', 'task_type', 'pattern'])
    fails = dedupe(fails, ['project', 'task_type', 'failure'])

    dump_jsonl(wins_path, wins, WIN_KEYS)
    dump_jsonl(fails_path, fails, FAIL_KEYS)

    print(f'wins: {len(wins)} rows normalized')
    print(f'failures: {len(fails)} rows normalized')


if __name__ == '__main__':
    main()
