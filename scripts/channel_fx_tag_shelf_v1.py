#!/usr/bin/env python3
"""채널·처리 태그 선반 v1 — 외부 lane1(전화·방송·필터) 109종을 우리 코퍼스 접지로 3분류.

계기: LEO 질의(08-25) 「스포큰 말고 전화라던지 여러 개 있지?」 → 있다. 레인이 통째로 있다.
      단 **등급이 전건 B_recited**(A_demo 0)이고 **우리 접지는 20종뿐**이다.

★후보 선반(`candidate_shelf_v1.json` 236행)과 **섞지 않는다** — 그쪽은 나레이션·화자 모집단이고
  인용 표준이 「나레이션 고유 N종」이다. 여기 채널·효과를 섞으면 그 인용이 조용히 오염된다(08-22 교훈).
"""
import json, re, sqlite3, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "data/metatag_external/v2_lanes/lane1_phone_broadcast.json"
LEX = ROOT / "data/reanalysis_v2/lexical_index.sqlite"
OUT = ROOT / "data/metatag_external/channel_fx_tag_shelf_v1.json"

d = json.loads(LANE.read_text())
con = sqlite3.connect(LEX)
rows = con.execute("SELECT source,entity,sentence,modifiers FROM entries").fetchall()
txt = lambda r: " ".join(x for x in (r[1], r[2], r[3]) if x).lower()
BR = " || ".join(txt(r) for r in rows if r[0] in ("bracket_entity", "stems_bracket"))
COLON = re.compile(r"^\[?[A-Za-z][A-Za-z ]{1,20}:")

tags = sorted({(x.get("tag") or "").strip() for x in d["tags"] if (x.get("tag") or "").strip()})
A, B, C = [], [], []
for t in tags:
    (B if COLON.match(t) else (A if t.strip("[]").lower() in BR else C)).append(t)

out = {
 "무엇": "외부 lane1(전화·방송·필터) 109종을 우리 코퍼스 접지로 3분류",
 "재현": "scripts/channel_fx_tag_shelf_v1.py",
 "★등급": f"레인 {len(d['tags'])}건 전부 **B_recited** — A_demo 0건(전부 남의 말, 우리 검증 0)",
 "A_출력층_실물_있음": A, "B_콜론파라미터형_비권장": B, "C_우리접지0_후보": C,
 "★분류_뜻": {
   "A": "우리 540곡 출력층 브라켓에 **문자열 실물**이 있다 — 지금 근거를 대고 쓸 수 있다.",
   "B": "콜론 파라미터형. **X2 검산에서 음성 수렴** 판정(출력층 0·입력층 0·외부는 placebo라 부름) — 권하지 않는다.",
   "C": "우리 접지 0. **전화 계열이 전부 여기 있다.**",
 },
 "★주의": [
   "접지 0 = 「Suno가 모른다」가 아니라 **「우리 540곡에서 안 나왔다」**.",
   "A군도 「출력층에 있다」이지 **「입력으로 넣으면 먹는다」가 아니다** — 층이 다르다(X2 §4-1).",
   "후보 선반 236행과 **섞지 않는다** — 모집단이 다르다(나레이션·화자 ↔ 채널·효과).",
 ],
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"A {len(A)} / B {len(B)} / C {len(C)} → {OUT.relative_to(ROOT)}")
