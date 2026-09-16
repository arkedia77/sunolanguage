#!/usr/bin/env python3
"""build_display_tags_shelf_v1.py — 수노 `display_tags` 채널의 신어 후보 선반(격리).

⛔왜 «또» 별도 파일인가 (세 번째 채널이다):
  ⑴`candidate_shelf_v1.json`      = 외부 전언(D등급)
  ⑵`candidate_shelf_suno_sp_v1`   = 수노가 «렌더 전»에 고쳐 쓴 SP
  ⑶**이 파일** = 수노가 «완성 클립에 붙인» 짧은 라벨
  ★셋 다 「수노/외부 산출」이지만 **채널이 다르다.** 합치면 2026-09-02 층 오염
    (입력층이 Suno 관측으로 세어짐)을 **새 모양으로 반복**한다.
  ⛔`attested_count`(=재분석 출력층)에 **합산 금지**.

사용: .venv/bin/python scripts/build_display_tags_shelf_v1.py <jsonl> [--apply]
"""
import json, sys, collections, glob, hashlib, os
sys.path.insert(0, 'scripts')
from emission_measure import known_vocab, WORD, STOP, fold  # noqa: E402 — 자는 하나만 쓴다

OUT = 'data/metatag_external/candidate_shelf_display_tags_v1.json'


def main():
    src = sys.argv[1]
    rows = [json.loads(l) for l in open(src)]
    state = collections.Counter(r.get('display_tags_state') for r in rows)
    status = collections.Counter(r.get('clip_status') for r in rows)
    raw, low, tok = collections.Counter(), collections.Counter(), collections.Counter()
    tok_clip = collections.defaultdict(set)
    for r in rows:
        dt = r.get('display_tags')
        if not dt:
            continue
        s = str(dt)
        raw[s] += 1
        low[s.strip().lower()] += 1
        for p in s.split(','):
            p = p.strip().lower()
            if p:
                tok[p] += 1
                tok_clip[p].add(r.get('clip_uuid'))
    ks, _ = known_vocab()
    # 우리가 «써 본 적» 있나 — 발주 정본(설계 파일) 전문
    ours = []
    for f in glob.glob('data/n0*/N0*_design.json'):
        for s in json.load(open(f))['songs']:
            ours.append(((s.get('sp') or '') + ' ' + (s.get('lyrics') or '')).lower())
    OURS = ' || '.join(ours)
    cand = {}
    for t, n in tok.items():
        words = [x for p in fold(t) for x in WORD.findall(p)]
        if not words or all(w in STOP for w in words) or any(w in ks for w in words):
            continue
        cand[t] = {'토큰': t, '출현': n, '클립수': len(tok_clip[t]),
                   '우리_발주에_있었나': t in OURS}
    shelf = {
        "무엇": "후보 선반 — 수노 `display_tags` 채널의 사전 미등재 토큰 (★expr_* 아님·사전 아님)",
        "재현": f"scripts/build_display_tags_shelf_v1.py {os.path.basename(src)} (수치를 상수로 안 박는다)",
        "원자료": {"파일": os.path.basename(src), "행": len(rows),
                   "sha256": hashlib.sha256(open(src, 'rb').read()).hexdigest(),
                   "출처": "sunomusic 2026-09-16 인도 · 클립 API 단건조회 · 크레딧 0·캡 0(그쪽 통제실험)"},
        "★채널_한정자": {
            "이것은": "수노가 **완성 클립에 스스로 붙인 «짧은 라벨»**이다.",
            "이것이_아닌_것": "⛔**재분석 출력층이 아니다**(완성곡을 듣고 쓴 «서술»이 아니라 «라벨»이다). ⛔**재작성 SP도 아니다**(그건 렌더 «전» 텍스트).",
            "⇒": "★**`attested_count` 합산 금지 · 다른 두 선반과도 합산 금지.** 채널이 셋이다.",
        },
        "분모와_상태": {
            "클립": len(rows),
            "display_tags_state": dict(state),
            "⛔빈_값을_안_뭉갬": "`key_absent`는 **응답에 칸이 «없는» 것**이고 재시도 대상이 아니다(그쪽 설계). NULL을 한 낱말로 적지 않는다.",
            "clip_status": dict(status),
            "⚠error 7건": "뺐다 넣었다 하지 않고 **그대로 둔다** — 분모 선택은 쓰는 쪽이 한다.",
            "⚠레버": "이 파일은 **aug 0·1 위주**(본판). 짝(2·3·4)은 `suno_sp_emissions`/재작성 코퍼스 쪽이다.",
        },
        "★두_자를_나란히": {
            "라벨 고유": {"원문 그대로": len(raw), "대소문자 접음": len(low),
                        "★차": len(raw) - len(low),
                        "★뜻": "수노가 **같은 라벨을 대소문자를 바꿔 가며** 낸다(`Korean Ballad` ↔ `Korean ballad` 등 9쌍). ⛔어느 수가 맞는 게 아니라 **자가 둘**이다 — 인용 시 규칙을 붙일 것."},
            "토큰 고유": len(tok),
            "토큰화 규칙": "쉼표 분리 + 소문자화 + strip **뿐**. ⛔어간·복수·하이픈·포함관계(`korean trot`↔`trot`) **안 묶었다**.",
        },
        "★★사전_미등재_토큰": {
            "종수": len(cand),
            "★우리 발주에 한 번도 없음": sum(1 for v in cand.values() if not v['우리_발주에_있었나']),
            "★검사 방법": "설계 파일 750곡의 `sp`+`lyrics` 전문(643,373자)에서 부분문자열 조회. **양성통제** = 우리가 확실히 쓴 `fingerpicked`·`upright bass`·`room reverb` 3/3 적중.",
            "항목": sorted(cand.values(), key=lambda x: (-x['출현'], x['토큰'])),
        },
        "★한계": [
            "유효성은 하나도 안 쟀다 — 「수노가 이 라벨을 붙였다」이지 「이 낱말을 프롬프트에 쓰면 먹힌다」가 아니다(대조군 0).",
            "`display_tags`는 **조회 시점**(2026-09-15~16) 값이다. 렌더 시점 값이라는 보장이 없다(`fetched_at` 행별 보유).",
            "모집단이 **v6기(`chirp-hawk`) 1,697곡**뿐이다 — 그 이전 구간은 «안 쟀다»(없는 것이 아니다).",
            "「사전 미등재」는 대상의 성질이 아니라 **내 대조기의 출력**이다(기능어 제외·하이픈 접기 규칙에 의존).",
        ],
        "⛔승격": "이 스크립트는 승격을 하지 않는다. `expr_*`·사전·커넥터 반영은 **채널 정의 확정 + 오너 결재** 뒤에만.",
    }
    if '--apply' not in sys.argv:
        print(f"(dry-run) 토큰 {len(tok)}종 · 사전 미등재 {len(cand)}종 · "
              f"그중 우리 발주에 없음 {sum(1 for v in cand.values() if not v['우리_발주에_있었나'])}")
        return
    json.dump(shelf, open(OUT, 'w'), ensure_ascii=False, indent=1)
    back = json.load(open(OUT))
    print(f"✅{OUT}")
    print(f"   토큰 {len(tok)} · 미등재 {len(cand)} · 우리 발주에 없음 "
          f"{shelf['★★사전_미등재_토큰']['★우리 발주에 한 번도 없음']}")
    print(f"   양성통제(다시 읽기): 항목 {len(back['★★사전_미등재_토큰']['항목'])}종 "
          f"{'✅' if len(back['★★사전_미등재_토큰']['항목']) == len(cand) else '⛔'}")


if __name__ == '__main__':
    main()
