#!/usr/bin/env python3
"""build_suno_sp_shelf_v1.py — 수노 «SP 재작성» 채널의 신어·문형 후보 선반(격리).

⛔왜 «별도» 선반인가 (이 파일의 존재 이유):
  기존 `candidate_shelf_v1.json`은 **외부 전언(D등급) 격리 대장**이다. 여기 내 실측을
  섞으면 등급이 거짓이 된다.
  ★그리고 더 중요한 것: 이 후보들은 **「수노가 완성곡을 «듣고» 쓴 서술」이 아니다.**
  코퍼스 `attested_count`의 정의(crosswalk `attested_count_scope`)는 **재분석 출력층**인데,
  재작성 SP는 **렌더 «전»에 텍스트를 고쳐 쓴 것**이다 — 같은 「수노 산출」이라도 **채널이 다르다.**
  ⛔섞으면 2026-09-02 층 오염을 **새 모양으로 반복**한다.

⛔이 선반이 «하지 않는» 것: expr_*·사전·커넥터로의 승격. 그건 별건 결재다.
사용: .venv/bin/python scripts/build_suno_sp_shelf_v1.py [--apply]
"""
import json, re, sqlite3, sys, collections
sys.path.insert(0, 'scripts')
from emission_measure import known_vocab, WORD, STOP, fold  # noqa: E402 — 자는 하나만 쓴다

OUT = 'data/metatag_external/candidate_shelf_suno_sp_v1.json'
REFRAME = re.compile(r'([A-Za-z][A-Za-z0-9 \-]{2,40}?)\s+reframed\s+as\s+([^,.:;]{3,60})', re.I)


def main():
    c = sqlite3.connect('sunolang.db')
    rows = c.execute("""select clip_uuid,batch,aug_creativity,emitted_sp,ordered_sp
                        from suno_sp_emissions where rewritten=1 and ordered_sp is not null""").fetchall()
    ks, _ = known_vocab()
    cand = {}
    buckets = collections.Counter()
    for u, b, a, e, o in rows:
        buckets[f'V{a}'] += 1
        new = set(WORD.findall(e.lower())) - set(WORD.findall(o.lower()))
        for w in new:
            parts = fold(w)
            if not parts or all(x in STOP for x in parts) or any(x in ks for x in parts):
                continue
            d = cand.setdefault(w, {'표기': w, '클립수': 0, '버킷': collections.Counter(),
                                    '배치': set(), '예문': []})
            d['클립수'] += 1
            d['버킷'][f'V{a}'] += 1
            d['배치'].add(b)
            if len(d['예문']) < 2:
                m = re.search(r'[^.;]{0,80}\b' + re.escape(w) + r'\b[^.;]{0,50}', e, re.I)
                if m:
                    d['예문'].append(m.group(0).strip())
    for d in cand.values():
        d['버킷'] = dict(d['버킷'])
        d['배치'] = sorted(x for x in d['배치'] if x)
    # 문형
    pat = collections.Counter()
    tgt, srcs, pex = collections.Counter(), collections.Counter(), []
    inord = 0
    for u, b, a, e, o in rows:
        if REFRAME.search(o or ''):
            inord += 1
        for m in REFRAME.finditer(e):
            pat[f'V{a}'] += 1
            srcs[m.group(1).strip().lower()] += 1
            tgt[m.group(2).strip().lower()] += 1
            if len(pex) < 10:
                pex.append({'버킷': f'V{a}', 'X': m.group(1).strip(), 'Y': m.group(2).strip()})

    shelf = {
        "무엇": "후보 선반 — 수노 «SP 재작성» 채널의 미등재 낱말·문형 (★expr_* 아님·사전 아님)",
        "재현": "scripts/build_suno_sp_shelf_v1.py (수치를 상수로 안 박는다 — 매번 DB·사전에서 다시 잰다)",
        "원자료": "sunolang.db:suno_sp_emissions (layer='suno_out' · source_field='metadata.tags')",
        "★채널_한정자": {
            "이것은": "수노가 **렌더 전에 우리 SP를 고쳐 쓴** 문자열이다.",
            "이것이_아닌_것": "⛔**수노가 완성곡을 «듣고» 쓴 서술이 아니다.** 코퍼스 `attested_count`의 정의(재분석 출력층)와 **채널이 다르다.**",
            "⇒": "★**`attested_count`에 합산 금지.** 섞으면 2026-09-02 층 오염(입력층이 Suno 관측으로 세어짐)을 **새 모양으로 반복**한다.",
        },
        "대장_등급": "A_관측(우리 실측·출력 문자열 전수) — ⛔단 **채널이 코퍼스와 다르므로 승격 자격은 별건**이다.",
        "승격_규칙": "⛔이 스크립트는 승격을 하지 않는다. expr_*·사전·커넥터 반영은 **오너 결재 + 채널 정의 확정** 뒤에만.",
        "분모": {"재작성 클립": len(rows), "버킷": dict(buckets),
                 "★주": "V0은 분모에 없다 — Variety 0에서 수노는 우리 SP를 그대로 돌려주므로 재작성이 구조적으로 0이다."},
        "미등재_낱말": {
            "고유 종수": len(cand),
            "★자_한정자": "「미등재」는 대상의 성질이 아니라 **내 대조기의 출력**이다. 기능어 제외·하이픈 접기 후의 수이며, 첫 측정에서 이 둘을 안 했을 때는 739였다(→342→현재). 인용 시 **대조 규칙을 함께** 적을 것.",
            "⛔비영어_주의": "V4 상위가 프랑스어(avec·guitare·voix·batterie)인데 이는 기존 「비영어 재작성」 항목이지 **신어가 아니다.**",
            "항목": sorted(cand.values(), key=lambda x: -x['클립수']),
        },
        "★문형_reframed_as": {
            "무엇": "「X reframed as Y」 — 수노가 원 장르 X를 **다른 장르 Y로 다시 걸어** 서술하는 구문.",
            "출현": sum(pat.values()), "버킷": dict(pat),
            "⛔우리_발주에_있던_클립": inord,
            "Y_고유_종수": len(tgt), "X_고유_종수": len(srcs),
            "Y_표본": [k for k, _ in tgt.most_common(25)],
            "예": pex,
            "⚠교란": "버킷별 출현율이 V2 20%·V3 19% ↔ V4 1%로 갈리지만 **V4는 시기·판번이 다르다** ⇒ ⛔「Variety 단계가 올리면 는다」고 말하지 않는다. 수만 적는다.",
        },
        "★한계": [
            "유효성은 하나도 안 쟀다 — 이 선반은 「수노가 무엇을 썼나」의 대장이지 「무엇이 먹히나」의 대장이 아니다.",
            "Y 장르 라벨은 수노의 «서술»이지 그 장르로 실제로 렌더됐다는 증거가 아니다(오디오층 미측정).",
            "분모가 세 버킷 혼재다. 버킷별로 쪼개면 검정력이 떨어진다 — 판정 전에 검정력을 먼저 계산할 것.",
        ],
    }
    if '--apply' not in sys.argv:
        print(f"(dry-run) 미등재 낱말 {len(cand)}종 · 문형 출현 {sum(pat.values())}회 "
              f"· 재작성 클립 {len(rows)} — `--apply`로 씀")
        return
    json.dump(shelf, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f"✅{OUT}")
    print(f"   미등재 낱말 {len(cand)}종 · 문형 「X reframed as Y」 {sum(pat.values())}회 "
          f"(발주 유래 {inord}) · 재작성 클립 {len(rows)}")
    back = json.load(open(OUT))
    print(f"   양성통제(다시 읽기): 항목 {len(back['미등재_낱말']['항목'])}종 "
          f"{'✅' if len(back['미등재_낱말']['항목']) == len(cand) else '⛔'}")


if __name__ == '__main__':
    main()
