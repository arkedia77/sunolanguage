#!/usr/bin/env python3
"""n_series_notify.py — N시리즈 배치 적재 통지(sunomusic 앞) 발신.

★본문 칸은 설계 파일·DB 실물에서 «기계로» 뽑는다 — 손으로 옮겨 적으면 배치마다 갈린다.
사용: .venv/bin/python scripts/n_series_notify.py N051 30519 --cumulative 10 [--extra "한 줄"]
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv/bin/python")

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("gid_start", type=int)
ap.add_argument("--cumulative", type=int, required=True, help="이 라인 누적 곡수")
ap.add_argument("--extra", default="")
# ★2026-09-13: 이 자리에 「무료창 유지 구간으로 알고 있습니다」가 **고정 문구**로 박혀 있었다.
#   09-13 06:10에 무료창이 닫히고 배차기가 정지된 뒤였으므로 그대로 보냈으면 **내가 아는 사실과
#   반대되는 문장**이 열 통 나갈 뻔했다. ⇒ 렌더 상태는 상수가 아니라 **발신 시점에 넘기는 인자**다.
#   같은 병의 앞 사례 = 이 파일 native 고정 문구(09-12). 교훈=「도구가 대신 단정한다」.
ap.add_argument("--render-note", required=True,
                help="발신 시점의 렌더 조건 한 줄 — ⛔기본값 없음(상태를 안 적으면 안 나간다)")
a = ap.parse_args()

d = json.loads((ROOT / f"data/{a.tag.lower()}/{a.tag}_design.json").read_text(encoding="utf-8"))
songs = d["songs"]
end = a.gid_start + len(songs) - 1

sys.path.insert(0, str(ROOT / "scripts"))
from json_to_db import get_conn
con = get_conn(); cur = con.cursor()
cur.execute("SELECT count(*), count(*) FILTER (WHERE status='pending_suno'), "
            "count(*) FILTER (WHERE music_engine='suno_v6') FROM songs "
            "WHERE global_id BETWEEN %s AND %s", (a.gid_start, end))
c, pend, v6 = cur.fetchone(); con.close()

# ★게이트는 «적재 전»에 찍은 박제분을 읽는다. 여기서 다시 돌리면 대조군에 자기 배치가
#   들어가 jaccard가 1.000이 된다(N051에서 실제로 찍혔고 발신 전에 잡았다).
gate_txt = ROOT / f"data/{a.tag.lower()}/{a.tag}_gate.txt"
if not gate_txt.exists():
    sys.exit(f"⛔게이트 박제 없음: {gate_txt} — n_series_ship.py 를 먼저 돌린다(사후 재실행 금지).")
gout = gate_txt.read_text(encoding="utf-8")
unatt = len([l for l in gout.splitlines() if "장르 라벨 미관측" in l])
# ★어휘 native는 «세서» 적는다. 09-12까지 이 자리에 "native 전건 1.0000"이 **고정 문구**로
#   박혀 있었다 — N051~N060에서는 결과적으로 참이었지만(100/100 재측정 일치) 그때 나는
#   재지 않고 단정했다. sunomusic이 같은 날 자인한 「산출물 칸에서는 단정하고 산문에서는
#   유보」와 같은 형태다. ⇒ 게이트 박제의 G2 미관측 줄 수로 파생한다.
vocab_unatt = len([l for l in gout.splitlines() if "G2 미관측" in l])
n_songs = len(songs)
native_line = (f"어휘 native **{n_songs - vocab_unatt}/{n_songs}곡이 1.0000**"
               + ("" if not vocab_unatt else f" · ⛔미관측 어휘 선언곡 {vocab_unatt}건"))
maxj = next((l.split("=")[1].strip() for l in gout.splitlines() if l.startswith("최대 jaccard")), "?")

body = {
 "0_한줄": f"★**{a.tag} 10곡 적재 — gid {a.gid_start}~{end}** · 축=「{d['축'].split('—')[0].strip()}」 · "
           f"게이트 10/10 PASS · 라인 누적 **{a.cumulative}곡**." + (f" {a.extra}" if a.extra else ""),
 "1_적재_실물": {
  "gid": f"{a.gid_start}~{end} 연속·결번 0",
  "DB_검증": f"{c}행 · `status=pending_suno` {pend} · `music_engine=suno_v6` {v6} "
             f"(★성공 출력이 아니라 적재 후 DB 재조회분입니다)",
  "설계": f"`repo:sunolanguage:data/{a.tag.lower()}/{a.tag}_design.json` · "
          f"`{a.tag}_raw.json` · 방식 `sunolanguage_design_v1`(설계 기반·코퍼스 조합 아님)"},
 "2_게이트": {
  "결과": f"G1~G6 hard fail 0 · {native_line} · **최대 jaccard {maxj}**"
          f"(대조군 = PG 내 우리 곡 전건 ∪ 같은 배치 앞 곡)",
  "⚠미관측": (f"장르 라벨 미관측 **{unatt}건** — 발주 차단 아님. ⛔**관측 라벨로 인용하지 마십시오.** "
             f"앞 라인(N021~N050)과 같은 라벨 풀을 일부러 유지합니다(라벨 드리프트 차단)."
             if unatt else "미관측 0건")},
 "3_축": d["축"],
 "4_조건": {
  "렌더": a.render_note,
  "★대조본": "이 라인은 Variety **2** 구간으로 예상합니다(귀 13:51 경계). ⛔제 대장에는 **곡별 `variety` 실값**으로 적습니다 — 예상으로 안 적습니다.",
  "가사칸": "`렌더입력_가사` 칸 수락분이 이 라인에도 실리면 좋겠습니다(N041~N050과 동일)."},
 "5_곡목": [{"gid": a.gid_start + i, "title": s["title"], "genre": s["genre"],
             "key": s["key"], "bpm": s["bpm"]} for i, s in enumerate(songs)],
}
tmp = Path("/tmp") / f"n_notify_{a.tag}.json"
tmp.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")
kw = f"{a.tag}_10곡적재_gid{a.gid_start}~{end}_게이트10of10_maxJ{maxj}_누적{a.cumulative}곡"
subj = (f"[적재 통지] {a.tag} 10곡 · gid {a.gid_start}~{end} · 축=「{d['축'].split('—')[0].strip()}」 · "
        f"게이트 10/10 PASS(최대 jaccard {maxj}) · 라인 누적 {a.cumulative}곡")
r = subprocess.run([PY, "scripts/send_msg.py", "sunomusic", kw, str(tmp), "--subject", subj],
                   cwd=ROOT, text=True, capture_output=True)
print(r.stdout.rstrip(), r.stderr.rstrip())
