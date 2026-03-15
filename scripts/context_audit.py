#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path('/Users/xs/.openclaw/workspace')

STARTUP_FILES = [
    'SOUL.md',
    'USER.md',
    'MEMORY.md',
    'AGENTS.md',
    'registry/playbooks.json',
    'recent/wins.jsonl',
    'recent/failures.jsonl',
]

THRESHOLDS = {
    'SOUL.md': 4000,
    'USER.md': 2500,
    'MEMORY.md': 4000,
    'AGENTS.md': 5000,
    'registry/playbooks.json': 6000,
    'recent/wins.jsonl': 6000,
    'recent/failures.jsonl': 6000,
    'daily_note_chars': 4000,
    'project_card_chars': 6000,
}


def file_stats(path: Path):
    text = path.read_text(encoding='utf-8')
    return {
        'path': str(path.relative_to(ROOT)),
        'chars': len(text),
        'lines': text.count('\n') + 1,
        'bytes': path.stat().st_size,
    }


def status(chars: int, limit: int):
    if chars >= limit * 1.5:
        return 'OVER'
    if chars >= limit:
        return 'WARN'
    return 'OK'


def latest_daily_note():
    notes = sorted((ROOT / 'memory').glob('20*.md'))
    if not notes:
        return None
    return notes[-1]


def project_cards():
    return sorted((ROOT / 'projects').glob('*.md'))


def main():
    print('=== Startup Context Audit ===')
    for rel in STARTUP_FILES:
        p = ROOT / rel
        if not p.exists():
            print(f'- {rel}: MISSING')
            continue
        st = file_stats(p)
        lim = THRESHOLDS.get(rel, 4000)
        print(f'- {rel}: {status(st["chars"], lim)} | chars={st["chars"]} lines={st["lines"]} limit={lim}')

    note = latest_daily_note()
    print('\n=== Daily Note ===')
    if note and note.exists():
        st = file_stats(note)
        lim = THRESHOLDS['daily_note_chars']
        print(f'- {st["path"]}: {status(st["chars"], lim)} | chars={st["chars"]} lines={st["lines"]} limit={lim}')
    else:
        print('- none')

    print('\n=== Project Cards ===')
    noisy = []
    for p in project_cards():
        st = file_stats(p)
        lim = THRESHOLDS['project_card_chars']
        s = status(st['chars'], lim)
        print(f'- {st["path"]}: {s} | chars={st["chars"]} lines={st["lines"]} limit={lim}')
        if s != 'OK':
            noisy.append(st)

    print('\n=== Folder Sizes ===')
    for folder in ['memory', 'projects', 'skills', 'registry', 'recent']:
        total = 0
        count = 0
        for f in (ROOT / folder).rglob('*'):
            if f.is_file():
                total += f.stat().st_size
                count += 1
        print(f'- {folder}/: bytes={total} files={count}')

    print('\n=== Verdict ===')
    startup_ok = True
    for rel in STARTUP_FILES:
        p = ROOT / rel
        if p.exists():
            st = file_stats(p)
            lim = THRESHOLDS.get(rel, 4000)
            if status(st['chars'], lim) != 'OK':
                startup_ok = False
    if note and status(file_stats(note)['chars'], THRESHOLDS['daily_note_chars']) != 'OK':
        startup_ok = False

    if startup_ok and not noisy:
        print('当前启动必读层整体偏轻，不需要为了压缩而压缩。重点盯住 daily note 和 project cards，别重新长胖。')
    else:
        print('存在值得压缩的上下文文件；优先压 daily note、project cards、MEMORY.md，避免把长过程塞回启动层。')


if __name__ == '__main__':
    main()
