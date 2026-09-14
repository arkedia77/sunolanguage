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
# ⛔2026-09-14 자적발 — 같은 것을 «두 자»로 세고 있었다(통에 104, 선반에 102).
#   원인 = **세는 자**(맨 `reframed as`)와 **뽑는 자**(`X … as Y` 전체형)가 달랐는데
#   둘 다 「문형 클립 수」라는 이름으로 나갔다. ⇒ ★**세는 자는 하나**로 못 박는다.
#   HAS = 클립을 «세는» 자 · REFRAME = X·Y를 «뽑는» 자(세기에 안 쓴다).
HAS = re.compile(r'\breframed\s+as\b', re.I)
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
    # ⛔2026-09-14 자체 하향 — 이 문형을 「수노가 쓰는 문형」으로 적었다가 배치별로 세어 보니
    #   **특정 창에 뭉쳐 있고 N062 이후 7배치 연속 0**이었다. ⇒ 배치표·교란을 «선반에» 박는다.
    #   ★0으로 돌아선 것을 지우지 않는다 — 지우면 다음에 「왜 갑자기 나왔나」를 못 본다.
    perbatch = collections.defaultdict(lambda: [0, 0])
    peracct = collections.defaultdict(lambda: [0, 0])
    lr_hit, lr_no = [], []
    inord = 0
    for u, b, a, e, o in rows:
        if HAS.search(o or ''):
            inord += 1
        _hit = 1 if HAS.search(e) else 0
        if b:
            perbatch[b][0] += 1
            perbatch[b][1] += _hit
        for m in REFRAME.finditer(e):
            pat[f'V{a}'] += 1
            srcs[m.group(1).strip().lower()] += 1
            tgt[m.group(2).strip().lower()] += 1
            if len(pex) < 10:
                pex.append({'버킷': f'V{a}', 'X': m.group(1).strip(), 'Y': m.group(2).strip()})

    # 교란 — 계정·길이비
    for u, b, a, e, o in c.execute("""select clip_uuid,batch,account,emitted_sp,length_ratio
                                      from suno_sp_emissions where rewritten=1""").fetchall():
        h = 1 if HAS.search(e or '') else 0
        peracct[a or '?'][0] += 1
        peracct[a or '?'][1] += h
        (lr_hit if h else lr_no).append(o or 0)
    ks_b = sorted(perbatch)
    last_hit = max((j for j, x in enumerate(ks_b) if perbatch[x][1] > 0), default=None)
    tail = ks_b[last_hit + 1:] if last_hit is not None else []
    import statistics
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
            "★클립_수": sum(1 for _u, _b, _a, _e, _o in rows if HAS.search(_e)),
            "★세는_자": "`\\breframed\\s+as\\b` 하나. X·Y 추출용 정규식은 «세기에 쓰지 않는다»(두 자로 세면 같은 값이 두 수가 된다 — 2026-09-14 실물 104↔102).",
            "⛔X·Y_추출_누락": "전체형(X … as Y)으로 안 잡히는 클립이 있다 — 그건 «추출 실패»이지 «출현 안 함»이 아니다.",
            "★단위_주의": "「출현」과 「클립」은 다른 수다 — 한 클립에 두 번 나오는 경우가 있다. 인용 시 단위를 붙일 것.",
            "★★배치별": {b: f"{perbatch[b][1]}/{perbatch[b][0]}" for b in ks_b},
            "★★현재_상태": (f"마지막 출현 = {ks_b[last_hit]} · 이후 **{len(tail)}배치 연속 0"
                          f"(분모 {sum(perbatch[b][0] for b in tail)}클립)**"
                          if tail else "최근 배치에서도 출현 중"),
            "⛔그래서_말할_수_있는_것": "⑴「수노가 이 구문을 «썼다»」=참 ⑵「수노가 이 구문을 «쓴다»」=⛔과하다.",
            "⛔철회된_계정_교란": {
                "내가_적었던_것": "asiloveu 32/98(32.7%) ↔ leoarkedia 72/839(8.6%) ⇒ 「계정 교란」",
                "★깨진_근거": {k: f"{v[1]}/{v[0]}" for k, v in sorted(peracct.items())},
                "★배치로_쪼개면": "asiloveu 적중 32건이 **전부 N060·N062 두 배치**다. 같은 계정인 **N067·N068·N069는 0/58**.",
                "⇒": "★**계정이 축이면 최근 세 배치에서 다시 나왔어야 한다. 안 나왔다.** ⇒ **철회.** 축은 계정이 아니라 시각이다(경계 09-14 00:56~01:14 · 근거=sunomusic 원장 렌더 시각).",
                "★★내_결함": "**주변합만 보고 교란이라 적었다.** 배치로 교차하면 바로 깨지는 값이었고, ⛔**그 반증은 내 DB 안에 이미 있었다** — 내가 교차표를 안 만든 것뿐이다.",
            },
            "★교란_길이비": {
                "주변합": (f"있음 {statistics.median(lr_hit):.4f}(n={len(lr_hit)}) ↔ "
                         f"없음 {statistics.median(lr_no):.4f}(n={len(lr_no)})"),
                "★배치_고정": "같은 배치 안에 둘 다 있는 23배치에서 (있음−없음) 중앙값 차 = **+0.0551 · 양수 21/23**",
                "★N060·N062_제외": "있음 0.8698(n=72) ↔ 없음 0.7534(n=825)",
                "⇒": "★**계정과 달리 이 연관은 배치를 고정해도 남는다.** 「이 구문은 «덜 줄어든» 재작성에 붙는다」까지가 실측. ⛔**인과·방향(더해서인지 안 줄여서인지)은 미상** — sunomusic도 「결과만 싣고 과정은 안 싣는다」고 답했다.",
            },
            "⛔Variety로_돌리지_않는다": "버킷별 차이(V2·V3 ↔ V4)는 **시기와 뒤엉켜** 있다. 「Variety의 효과」로 돌릴 근거가 없다. ★sunomusic 확인: 경계 구간에 **그쪽 설정·경로·파라미터 전건 불변**(레버는 N059~N069 전 배치 동일값 3).",
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
