#!/usr/bin/env python3
"""antisuno Phase 0 — codex exec 원본(raw_*.txt)에서 마지막 ```json 펜스를 뽑아 파싱본으로 저장.
브리프 자체가 스키마 예시로 ```json 을 포함하므로 **마지막** 펜스만 취한다."""
import json, re, sys, pathlib

SURVEY = pathlib.Path('data/antisuno/survey')

def extract(path):
    txt = path.read_text(errors='replace')
    blocks = re.findall(r'```json\s*\n(.*?)\n```', txt, re.S)
    if not blocks:
        return None, 'no json fence'
    for blk in reversed(blocks):
        try:
            return json.loads(blk), None
        except json.JSONDecodeError as e:
            last = f'{e}'
    return None, f'json parse failed: {last}'

def main():
    ok = []
    for raw in sorted(SURVEY.glob('raw_*.txt')):
        if 'tokens used' not in raw.read_text(errors='replace'):
            print(f'  … {raw.name}: 미완료(스킵)')
            continue
        obj, err = extract(raw)
        if err:
            print(f'  ⛔ {raw.name}: {err}')
            continue
        out = SURVEY / (raw.stem.replace('raw_', 'parsed_') + '.json')
        out.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
        n = len(obj.get('engines', []))
        print(f'  ✅ {raw.name} → {out.name} · engines={n}')
        ok.append(out)
    return ok

if __name__ == '__main__':
    main()
