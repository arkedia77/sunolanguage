#!/usr/bin/env python3
"""ace_lyric_tag_check_v1.py — ACE 가사 샘플 태그·길이 셈 + Suno 홈 곡 브라켓에서 «[섹션 - 지시]» 꼴 곡 수 (encore 223912). 쓰기 0.
사용: ace_lyric_tag_check_v1.py <가사샘플.txt>"""
import collections, json, re, sys
sys.path.insert(0, "/Users/purple/sunolanguage/scripts")
import build_suno_phrase_dict_v2 as B

DASH = re.compile(r"^\[\s*[A-Za-z][A-Za-z\- ]*\d?\s+-\s+(.+)\]$")
INSTR = re.compile(r"\b(guitar|piano|rhodes|bass|drums?|snare|strings|synth|organ|brass|horns?|sax|violin|cello|percussion|kick|808|pad|keys|fingerpick\w*)\b", re.I)
VOC = re.compile(r"\b(vocals?|voice|harmony|harmonies|delivery|whisper|falsetto|belt|humming|spoken|rap)\b", re.I)
DYN = re.compile(r"\b(soft|gentle|full|muted|dynamics|build\w*|fade|fading|quiet|loud|explosive|intimate|delicate|stripped|sparse)\b", re.I)

refs = json.loads(B.REFS.read_text())["songs"]
tot, song, tags, lens = collections.Counter(), collections.Counter(), collections.Counter(), collections.defaultdict(list)
for s in refs:
    b = s.get("brackets") or []
    if not b:
        continue
    ch = "HS" if (s.get("gpt_description_prompt") or s.get("task") == "agentic_thinking") else "HU"
    tot[ch] += 1
    d = [t for t in b if DASH.match(t)]
    song[ch] += bool(d)
    for t in d:
        tags[ch] += 1; lens[ch].append(len(t))
print("브라켓 있는 곡", dict(tot), "· «[섹션 - 지시]» 1개↑ 곡", dict(song), "· 그 태그 수", dict(tags),
      "· 태그 글자 중앙", {k: sorted(v)[len(v) // 2] for k, v in lens.items()})
txt = open(sys.argv[1]).read()
L = [l for l in txt.splitlines() if l.strip()]
tg = [l for l in L if l.startswith("[")]; ly = [l for l in L if not l.startswith("[")]
syl = lambda l: len(re.findall(r"[가-힣]", l))
print("샘플 전체", len(txt), "자 · 태그", len(tg), [len(t) for t in tg], "· 가사 줄", len(ly), "· 음절", sum(map(syl, ly)), "· 고유 줄", len(set(ly)))
for t in tg:
    x = t.strip("[]").split(" - ", 1)[-1]
    print(" ", t, "|", " ".join(k for k, rx in (("악기", INSTR), ("보컬", VOC), ("다이내믹", DYN)) if rx.search(x)))
