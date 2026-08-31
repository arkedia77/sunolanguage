#!/usr/bin/env python3
"""antisuno · 이식 변환기 v0 (dry-run 전용 · 생성 호출 없음)

우리 자산(style_prompt + suno_lyrics)을 목표 엔진 문법으로 **변환만** 한다.
⛔이 변환이 뜻을 보존한다는 실측은 0건이다(`docs/antisuno/portability_rules_v0.md` §7).
   유일한 실측은 「무변경 이식은 깨진다」 1건(M4·n=1)이다.

사용:
  python3 scripts/antisuno_port.py --engine minimax_music_3 --in <song.json>
  python3 scripts/antisuno_port.py --engine eleven_music_v2 --in <song.json> --field-lyrics suno_lyrics
  python3 scripts/antisuno_port.py --list

입력 JSON: {"style_prompt": "...", "suno_lyrics": "..."} 또는 그 키를 품은 객체.
"""
import argparse, json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = ROOT / "data/antisuno/portability_rules_v0.json"
BR = re.compile(r'\[([^\]]*)\]')


def load_rules():
    return json.loads(RULES.read_text(encoding="utf-8"))


def classify(text, canon):
    """브라켓 문면을 S(섹션 라벨) / D(연주 지시)로 가른다."""
    head = re.sub(r'[^a-z\s-]', ' ', text.lower()).strip()
    for c in sorted(canon, key=len, reverse=True):
        if head.startswith(c) or head.split(' -')[0].strip() == c:
            return 'S'
    return 'D'


def split_brackets(lyrics, canon):
    out = []
    for m in BR.finditer(lyrics):
        body = m.group(1)
        out.append({"span": m.span(), "text": body, "kind": classify(body, canon),
                    "words": len(body.split())})
    return out


def map_section(body, official):
    """S형을 목표 엔진의 공식 태그로 매핑. 못 찾으면 None."""
    key = re.sub(r'[^a-z\s]', ' ', body.lower()).split()
    if not key:
        return None
    joined = ' '.join(key)
    best = None
    for tag in official:
        name = tag.strip('[]').lower()
        if joined.startswith(name) or name.startswith(joined.split()[0]):
            if best is None or len(name) > len(best.strip('[]')):
                best = tag
    return best


def port(song, engine, rules):
    eng = rules['engines'].get(engine)
    if not eng:
        sys.exit(f"unknown engine: {engine}. --list 로 확인.")
    canon = rules['section_canon']
    lyr = song.get('suno_lyrics') or song.get('lyrics') or ''
    sp = song.get('style_prompt') or song.get('sp') or ''
    brs = split_brackets(lyr, canon)

    moved, dropped, kept, remapped, warnings = [], [], [], [], []
    new = lyr
    # 뒤에서부터 치환해야 span이 안 밀린다
    for b in sorted(brs, key=lambda x: -x['span'][0]):
        s, e = b['span']
        act = eng.get(b['kind'], 'keep')
        repl = f"[{b['text']}]"
        if act == 'keep':
            kept.append(b['text'])
        elif act == 'lowercase':
            repl = f"[{b['text'].lower()}]"; remapped.append((b['text'], repl))
        elif act == 'map_to_official':
            t = map_section(b['text'], eng.get('official_tags', []))
            if t:
                repl = t; remapped.append((b['text'], t))
            else:
                repl = ''; dropped.append(b['text'])
                warnings.append(f"S형 `{b['text']}` 가 공식 태그에 없어 제거됨")
        elif act == 'closed_vocab':
            t = map_section(b['text'], eng.get('closed_vocab', []))
            if t:
                repl = t; remapped.append((b['text'], t))
            else:
                repl = ''; dropped.append(b['text'])
                warnings.append(f"S형 `{b['text']}` 가 폐쇄 어휘 밖이라 제거됨")
        elif act == 'to_braces':
            repl = '{' + b['text'] + '}'; remapped.append((b['text'], repl))
        elif act in ('move_to_prompt', 'move_to_caption', 'move_to_descriptions',
                     'to_weighted_prompt', 'to_timestamp_prose'):
            repl = ''; moved.append(b['text'])
        elif act == 'drop':
            repl = ''; dropped.append(b['text'])
        new = new[:s] + repl + new[e:]

    # 빈 줄 정리
    new = re.sub(r'\n{3,}', '\n\n', new).strip()

    # ★D형 무이동 경고 — 이 도구의 존재 이유
    if eng.get('D') == 'keep':
        longs = [b for b in brs if b['kind'] == 'D' and b['words'] >= 9]
        if longs:
            warnings.append(
                f"⚠D형 {len(longs)}건이 9어 이상인데 이 엔진은 keep이다. "
                f"MiniMax에서 같은 형태가 가창된 실측이 있다(M4·n=1) — 이 엔진에서는 미측정.")

    style_out = sp
    if eng.get('style') == 'array':
        # 슬롯 라벨(`vocal:` `lead:` 등)과 문장부호에서만 가른다.
        # ⛔`and`로 가르면 'close-mic and quiet on the verses'가 쪼개져 뜻이 깨진다(v0 시행착오).
        parts = re.split(r'[,;.]\s+|\s*\b(?=[a-z_]+:\s)', sp)
        style_out = [t.strip(' .;,') for t in parts if t.strip(' .;,')]
        if eng.get('style_max_items') and len(style_out) > eng['style_max_items']:
            warnings.append(f"style 서술자 {len(style_out)}개 > 상한 {eng['style_max_items']}")
    if eng.get('style_lang') == 'en_required' and re.search(r'[가-힣]', sp):
        warnings.append("⚠style에 한국어가 있다 — 이 엔진은 스타일 서술자 영어 필수(가사는 임의 언어).")
    if eng.get('style_max_chars') and len(sp) > eng['style_max_chars']:
        warnings.append(f"style {len(sp)}자 > 상한 {eng['style_max_chars']}")
    if eng.get('lyrics_field') is False:
        warnings.append("⛔이 엔진에는 가사 칸이 없다. 가사를 쓰려면 다른 엔진을 골라야 한다.")
    nums = re.findall(r'\b\d+\s*(?:bpm|bar|bars|sec|s)\b', sp, re.I)
    if nums and eng.get('numbers') not in ('text_only', None):
        tgt = eng.get('numbers')
        if tgt == 'none':
            warnings.append(f"style 안 숫자 {nums} → 이 엔진엔 받을 파라미터가 없다. 텍스트로 두면 D015 상황이 재현될 수 있다(미측정).")
        else:
            warnings.append(f"style 안 숫자 {nums} → 이 엔진의 파라미터로 이사시켜라: {tgt}")

    return {
        "engine": engine, "evidence": eng.get('evidence'),
        "style": style_out,
        "lyrics": new,
        "moved_to_style_channel": moved,
        "dropped": dropped, "remapped": remapped, "kept": kept,
        "warnings": warnings,
        "bracket_census": {"total": len(brs),
                           "S": sum(1 for b in brs if b['kind'] == 'S'),
                           "D": sum(1 for b in brs if b['kind'] == 'D')},
        "⛔한계": "이 변환이 뜻을 보존한다는 실측은 0건이다. 처방은 벤더 문서(E)에서 유도했다.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine')
    ap.add_argument('--in', dest='inp')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    rules = load_rules()
    if a.list:
        for k, v in rules['engines'].items():
            print(f"  {k:22} 가사칸={v.get('lyrics_field')} S={v.get('S')} D={v.get('D')} 등급={v.get('evidence')}")
        return
    if not (a.engine and a.inp):
        sys.exit("--engine 과 --in 이 필요하다 (또는 --list)")
    song = json.loads(pathlib.Path(a.inp).read_text(encoding='utf-8'))
    print(json.dumps(port(song, a.engine, rules), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
