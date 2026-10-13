#!/usr/bin/env python3
"""number_reading_class_v1.py — 가사 본문 «한글로 적은 수»의 읽기 계열↔단위 짝맞음 측정 (읽기 전용)

왜(자기 발제 2026-10-13 · A-177 유휴분기):
  LEO 지시(encore 122703)는 두 겹이다 — ⑴본문에 아라비아 숫자 0 ⑵**소리 나는 대로** 한글로 적는다
  (고유어 단위 시·번·개·살 → 한·두·세·네… / 한자어 단위 분·초·년·원 → 일·이·삼…).
  ⛔내 검문 3곳(`g2_lyrics_gate ⑥`·`n_series_gate G7`·`songcard pipeline`)은 **⑴만** 본다.
  「사 시에 만나」는 아라비아 숫자가 0이므로 **전부 통과한다** — 규칙 위반인데 통과한다.
  ⇒ 검사 ⑦를 신설할 값이 있나? **빈도를 재기 전에는 모른다.** 이 스크립트는 그 분모만 낸다.

★판별 한계를 먼저 박아 둔다(이게 이 측정의 핵심 위험이다):
  한자어 수사는 흔한 낱말과 동형이다 — 「이」(this)·「일」(work/day)·「사」(buy)·「오」(감탄)·「구」.
  「이 번」=this time · 「일 번」=number one(정당) · 「네 분」=four people(정당) · 「세 개월」(정당).
  ⇒ 넓은 패턴은 **오탐 공장**이다. 그래서 ⑴짝을 «오탐이 적은 것»으로만 좁히고
    ⑵걸린 줄은 **전건 사람이 읽어 확인**하며 ⑶정밀도를 같이 보고한다.
  ⛔「0건」을 내려면 **양성통제**(일부러 틀린 줄을 넣어 검출기가 우는지)를 먼저 통과해야 한다.
  ⛔이 측정은 «입력 글자»를 본다 — 수노가 실제로 어떻게 읽었는지는 **못 잰다**(PROBE_NUM01 축).

사용:
  .venv/bin/python scripts/number_reading_class_v1.py --selftest
  .venv/bin/python scripts/number_reading_class_v1.py --pg   [--limit N]
"""
import argparse, os, re, sys, json
from collections import Counter

BRACKET_SPAN = re.compile(r"\[[^\]]*\]")

# 고유어 수사(관형형) — 단위 앞에 서는 꼴만
NATIVE = ["한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉", "열",
          "열한", "열두", "스무", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
# 한자어 수사 — ⛔동형 낱말이 흔한 「이·일·오·구·만·천」은 **일부러 뺀다**(오탐 공장)
# ⛔1차 실측 자기정정(10-13): 「십·백」을 넣었다가 **오탐 64/108 = 59%**를 만들었다 —
#   고유어 수사는 아흔아홉에서 끝나므로 **100 이상은 한자어가 표준**이다(「백 개」·「백 명」은 정당).
#   「십 개」·「십 명」도 「열 개」와 함께 표준이라 같이 뺀다. ⇒ 1~9 자리에서만 본다.
SINO = ["삼", "사", "육", "칠", "팔"]

# ㉮ 고유어가 거의 의무인 단위(한자어 수사가 오면 틀린 쪽)
UNIT_NATIVE_ONLY = ["시", "살", "개", "명", "마리", "송이", "켤레", "그루", "자루", "벌", "채", "알"]
# ㉯ 한자어가 거의 의무인 단위(고유어 수사가 오면 틀린 쪽)
#   ⛔「분」(=사람 높임)·「층」·「개월」·「달」은 양쪽 다 정당해서 **뺀다**
UNIT_SINO_ONLY = ["초", "년", "원", "인분", "교시", "번지", "퍼센트", "세기", "주년"]


# ★단위 뒤에 올 수 있는 꼴 — 끝·비한글·«조사/어미 흰목록»만 허용한다.
#   ⛔첫 판은 `(?![가-힣])`로 막았는데 **조사가 전부 한글이라 양성 표본 3건이 전멸**했다
#     (「사 시«에»」가 안 걸렸다 — 자가검사가 바로 잡았다). 흰목록으로 바꾼다.
#   ★흰목록이라 「사 시«간»」·「삼 개«월»」처럼 **다른 단위로 이어지는 꼴은 계속 배제**된다(의도).
JOSA = ["에서", "에게", "부터", "까지", "마다", "보다", "처럼", "라고",
        "에", "을", "를", "이", "가", "은", "는", "도", "만", "과", "와", "의",
        "로", "야", "쯤", "씩", "째", "나", "라", "요", "다", "고", "지", "며", "면", "서", "랑", "엔"]


def _pat(nums, units):
    """수사 + (공백 0~1) + 단위 — 뒤는 끝·비한글·조사 흰목록(낱말 중간 적중 방지)."""
    n = "|".join(sorted(nums, key=len, reverse=True))
    u = "|".join(sorted(units, key=len, reverse=True))
    j = "|".join(sorted(JOSA, key=len, reverse=True))
    return re.compile(rf"(?<![가-힣])({n})\s?({u})(?=$|[^가-힣]|{j})")


P_A = _pat(SINO, UNIT_NATIVE_ONLY)      # 한자어 수사 + 고유어 단위
P_B = _pat(NATIVE, UNIT_SINO_ONLY)      # 고유어 수사 + 한자어 단위


def body_lines(lyrics: str):
    """가창 본문만 — 브라켓 구간은 행 안쪽이라도 걷어낸다(검문 3곳과 같은 규약)."""
    for i, ln in enumerate((lyrics or "").splitlines(), 1):
        b = BRACKET_SPAN.sub("", ln).strip()
        if b:
            yield i, b


def hits(lyrics: str):
    out = []
    for i, b in body_lines(lyrics):
        for kind, pat in (("A_한자어수사+고유어단위", P_A), ("B_고유어수사+한자어단위", P_B)):
            for m in pat.finditer(b):
                out.append({"line_no": i, "kind": kind, "token": m.group(0), "line": b})
    return out


SELFTEST = [
    # (가사, 기대 적중 수, 설명)
    ("새벽 사 시에 만나", 1, "㉮ 양성 — 「사 시」는 「네 시」로 적어야 한다"),
    ("새벽 네 시에 만나", 0, "㉮ 음성 — 올바른 표기"),
    ("사탕 삼 개를 쥐고", 1, "㉮ 양성 — 「세 개」"),
    ("삼 초만 기다려", 0, "㉯ 음성 — 초는 한자어가 맞다"),
    ("네 초만 기다려", 1, "㉯ 양성 — 「사 초」"),
    ("네 분이 오셨다", 0, "⛔제외 단위 — 「분」=사람 높임도 정당(일부러 안 본다)"),
    ("세 개월이 지나", 0, "⛔제외 단위 — 「세 개월」 정당"),
    ("이 번에는 달라", 0, "⛔제외 수사 — 「이」=this(동형)"),
    ("[Verse 1 사 시] 그 자리에서", 0, "브라켓 «안»은 대상 밖"),
    ("[Verse 1] 사 시에 만나", 1, "브라켓 «밖»은 본문 — 행 안쪽이라도 본다"),
    ("사 시간을 걸었다", 0, "⛔다른 단위로 이어지는 꼴(시간)은 배제 — 흰목록 효과"),
    ("새벽 4시에 만나", 0, "아라비아 숫자는 이 검사의 축이 아니다(⑥·G7 소관)"),
    ("팔 개월 만에", 0, "제외 단위"),
    ("별 백 개를 세었다", 0, "⛔100 이상은 한자어가 표준 — 「백 개」는 정당(1차 오탐 자기정정)"),
    ("사람 십 명이 모여", 0, "⛔「십 명」도 표준 — 1~9 자리만 본다"),
    ("열두 시에 울린다", 0, "㉮ 음성 — 고유어 수사 정당"),
]


def selftest():
    fail = 0
    for ly, want, why in SELFTEST:
        got = len(hits(ly))
        ok = got == want
        fail += not ok
        print(f"  {'✅' if ok else '⛔'} {want}건 기대 / {got}건 — {ly!r} · {why}")
    # ★음성통제: 패턴을 끊으면 양성 표본이 FAIL 로 돌아야 한다(표본이 실제로 패턴에 기대는가)
    global P_A, P_B
    keep = (P_A, P_B)
    P_A = P_B = re.compile(r"(?!x)x")
    broke = sum(1 for ly, want, _ in SELFTEST if len(hits(ly)) != want)
    P_A, P_B = keep
    print(f"  {'✅' if broke else '⛔'} 음성통제 — 패턴을 끊으면 {broke}건 FAIL"
          + ("" if broke else " ⛔표본이 아무것도 안 잰다"))
    print(f"[selftest] {'PASS' if not fail and broke else 'FAIL'}  (자가 {len(SELFTEST)}칸 중 실패 {fail})")
    return 0 if (not fail and broke) else 2


def pg_rows(limit=None):
    import psycopg2
    conf = {}
    for ln in open(os.path.expanduser("~/.config/leofamily_music/db_sunolanguage.conf")):
        ln = ln.strip()
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            conf[k.strip()] = v.strip()
    c = psycopg2.connect(host=conf["DB_HOST"], port=conf.get("DB_PORT", 5432),
                         dbname=conf["DB_NAME"], user=conf["DB_USER"],
                         password=conf.get("DB_PASSWORD", ""))
    q = ("SELECT global_id, source_project, batch, lyrics FROM songs "
         "WHERE lyrics IS NOT NULL AND btrim(lyrics) <> '' ORDER BY global_id")
    if limit:
        q += f" LIMIT {int(limit)}"
    cur = c.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    c.close()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pg", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    print("=== number_reading_class v1 — 읽기 계열↔단위 짝맞음 (읽기 전용) ===")
    rc = selftest()
    if a.selftest or not a.pg:
        return rc
    if rc:
        sys.exit("⛔자가검사 FAIL — 코퍼스를 재지 않는다(검출기를 믿을 수 없다).")
    rows = pg_rows(a.limit)
    per_proj = Counter(); per_proj_hit = Counter(); kinds = Counter(); tokens = Counter()
    details = []
    for gid, proj, batch, ly in rows:
        per_proj[proj] += 1
        h = hits(ly)
        if h:
            per_proj_hit[proj] += 1
            for x in h:
                kinds[x["kind"]] += 1
                tokens[x["token"]] += 1
                details.append({"global_id": gid, "source_project": proj, "batch": batch, **x})
    tot = sum(per_proj.values()); tot_hit = sum(per_proj_hit.values())
    print(f"\n■ 분모 = 가사 보유 {tot}곡 (입력층 songs · ★렌더는 안 들었다)")
    print(f"■ 짝 안 맞는 표기가 1곳 이상인 곡 = {tot_hit}곡 ({tot_hit/tot*100:.2f}%)  ⛔정밀도 미확인")
    for p, n in per_proj.most_common():
        print(f"    {p:<20} {per_proj_hit[p]:>4}/{n:<5} {per_proj_hit[p]/n*100:>6.2f}%")
    print("\n■ 유형: " + " · ".join(f"{k} {v}" for k, v in kinds.most_common()))
    print("■ 적중 표기 상위: " + " · ".join(f"{t}×{n}" for t, n in tokens.most_common(15)))
    if a.out:
        json.dump({"denominator_songs": tot, "songs_with_hit": tot_hit,
                   "per_project": {p: [per_proj_hit[p], n] for p, n in per_proj.items()},
                   "kinds": dict(kinds), "tokens": dict(tokens), "hits": details},
                  open(a.out, "w"), ensure_ascii=False, indent=1)
        print(f"\nWROTE {a.out}  (걸린 줄 전건 — 사람이 읽어 정밀도를 확인할 것)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
