#!/usr/bin/env python3
"""suno_update_check.py — Suno 쪽 갱신 정기 점검(LEO 10-22 «수노 코퍼스 업데이트 주기적으로 체크해야해»).

두 갈래를 지난 점검과 비교한다(상태 = data/suno_update_state.json · 보고 = data/suno_update_reports/YYYYMMDD_HHMM.md):
  [공식]  help.suno.com 글(새 글·Edited 날짜 바뀜) · suno.com 릴리스 노트·블로그(새 slug) — 새 것은 본문까지 수집
  [자생]  PG suno_clip_style — 새 클립 수·새 model_name·Suno tags 에만 있고 우리 입력에 없는 낱말 중
          suno_emitted_terms 에 아직 없는 것(후보 · 등재 아님)
⛔이 스크립트는 sunolang.db 에 쓰지 않는다(단일 Writer 는 build_suno_emitted_v1.py). 찾기만 하고 등재는 사람이 판단.
⛔「변화 0」은 각 갈래가 실제로 응답했을 때만 쓴다 — 접속 실패는 「미측정」.

사용: .venv/bin/python scripts/suno_update_check.py [--no-help]   (--no-help = 도움말 108글 재수집 생략 · 목록만)
"""
import argparse, collections, datetime, json, re, sqlite3, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_suno_help as fh

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "data/suno_update_state.json"
REPORTS = REPO / "data/suno_update_reports"
DOCS = REPO / "data/suno_docs"
STOP = set("a an the and with of in into to on for at by from its it as is that this over under then while through "
           "between across up down out off but or so very more most than each every both all bpm key major minor".split())
NON_GEN = {"stem", "edit_upsample", "edit_infill", "upload"}


def words(s):
    return {w for w in re.findall(r"[a-z][a-z\-']+", (s or "").lower()) if w not in STOP and len(w) > 2}


def check_pages(kind):
    h = fh.subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "30", f"https://suno.com/{kind}"],
                          capture_output=True).stdout.decode("utf-8", "ignore")
    live = {x for x in re.findall(rf"/{kind}/([a-z0-9][a-z0-9-]+)", h)
            if x != "opengraph-image" and not x.startswith("page-")}  # 공유 이미지·페이지 조각 = 글 아님
    if not live:
        return None
    have = {p.stem for p in (DOCS / kind).glob("*.json")}
    new = sorted(live - have)
    if new:
        fh.fetch_pages(kind, new)
    return {"live": len(live), "stored": len(have), "new": new}


def check_help(prev_idx):
    fh.main()
    cur = json.loads((fh.OUT / "index.json").read_text())
    if not cur:
        return None
    old = {x["id"]: x for x in prev_idx}
    new = [x for x in cur if x["id"] not in old]
    edited = [x for x in cur if x["id"] in old and x["edited"] != old[x["id"]]["edited"]]
    gone = [i for i in old if i not in {x["id"] for x in cur}]
    return {"articles": len(cur), "new": [(x["id"], x["title"]) for x in new],
            "edited": [(x["id"], x["title"], old[x["id"]]["edited"], x["edited"]) for x in edited], "gone": gone}


def check_emitted(since):
    from json_to_db import get_conn
    cur = get_conn().cursor()
    cur.execute("select model_name, count(*), max(clip_created_at) from suno_clip_style group by 1")
    models = {m: [n, str(t)] for m, n, t in cur.fetchall()}
    # 모델 이름만으론 «새 생성 모델»인지 못 가린다(10-23: haddock=stem·halibut=upsample·chirp-chirp=upload) — 용도 꼬리표
    cur.execute("""select model_name, coalesce(gen_method,'-'), coalesce(clip_type,'-'), count(*) from suno_clip_style
                   group by 1,2,3 order by 1, 4 desc""")
    kinds = collections.defaultdict(list)
    for m, g, t, n in cur.fetchall():
        kinds[m].append(f"{g}/{t}:{n}")
    # 도착(first_seen_at) 기준 — 생성일(clip_created_at) 기준이면 늦은 적재분이 영영 안 훑인다(10-23: 2,910 도착 중 458 만 새 생성)
    cur.execute("""select s.sp_suno, g.style_prompt, s.clip_created_at > %s, coalesce(s.gen_method,'')
                   from suno_clip_style s left join songs g on g.global_id=s.global_id
                   where s.first_seen_at > %s""", (since, since))
    rows = cur.fetchall()
    known = {t for t, in sqlite3.connect(REPO / "sunolang.db").execute("select lower(term) from suno_emitted_terms")}
    cnt, diff, skipped = collections.Counter(), 0, collections.Counter()
    for sp, inp, _, gm in rows:
        if gm in NON_GEN:  # 스템·업샘플·업로드 = 우리 SP 를 받아 새로 쓴 문장이 아님 — 후보에서 뺀다(뺀 수는 보고)
            skipped[gm] += 1
            continue
        extra = words(sp) - words(inp)
        if inp and extra:
            diff += 1
        if inp:
            cnt.update(w for w in extra if w not in known)
    # 되울림 가르기(10-23): 짝 입력엔 없어도 «다른 곡» 입력에 있으면 Suno 말이 아니라 우리 말이 돌아온 것(첫 측정 30 중 18)
    cur.execute("select style_prompt from songs where style_prompt is not null")
    ours = set().union(*(words(x) for x, in cur.fetchall()))
    top = cnt.most_common(30)
    return {"models": models, "model_kinds": dict(kinds), "arrived": len(rows),
            "new_clips": sum(1 for r in rows if r[2]), "non_gen_skipped": dict(skipped),
            "new_clips_with_input_and_extra": diff, "candidate_terms_top": top,
            "candidate_suno_only": [(w, n) for w, n in top if w not in ours],
            "candidate_echo": [(w, n) for w, n in top if w in ours]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-help", action="store_true")
    ap.add_argument("--since", help="자생 갈래 기준 시각 덮어쓰기(ISO) — 놓친 구간 재훑기용")
    a = ap.parse_args()
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    now = datetime.datetime.now().astimezone()
    since = a.since or st.get("emitted_checked_at", "2026-10-16T00:00:00+09:00")  # suno_emitted v1 적재 기준(V6 census 10-16)
    rep, out = {}, [f"# Suno 갱신 점검 {now:%Y-%m-%d %H:%M} (지난 점검 {st.get('checked_at', '없음 — 첫 점검')})", ""]

    prev_idx = json.loads((fh.OUT / "index.json").read_text()) if (fh.OUT / "index.json").exists() else []
    for kind in ("release-notes", "blog"):
        try:
            r = check_pages(kind)
        except Exception as e:
            r = None; out.append(f"- [공식] {kind}: 미측정({e})")
        rep[kind] = r
        if r is None:
            out.append(f"- [공식] {kind}: **미측정**(목록 0 — 접속·구조 변경 확인)")
        else:
            out.append(f"- [공식] {kind}: 목록 {r['live']} · 보관 {r['stored']} · **새 글 {len(r['new'])}** {r['new']}")
    if a.no_help:
        out.append("- [공식] help: 생략(--no-help) = 미측정")
    else:
        try:
            r = check_help(prev_idx)
        except Exception as e:
            r = None
        rep["help"] = r
        if r is None:
            out.append("- [공식] help: **미측정**(수집 0)")
        else:
            out.append(f"- [공식] help: 글 {r['articles']} · **새 글 {len(r['new'])}** {r['new']} · "
                       f"**Edited 바뀜 {len(r['edited'])}** {r['edited']} · 사라짐 {r['gone']}")
    try:
        r = check_emitted(since)
        rep["emitted"] = r
        total = sum(v[0] for v in r["models"].values())
        out.append(f"- [자생] PG suno_clip_style 전체 {total}행(지난 {st.get('total', '없음')}) — 생성일이 지난 점검보다 이른 늦은 적재분은 이 차이로만 보임")
        st["total"] = total
        out.append(f"- [자생] PG suno_clip_style: {since} 이후 **도착 {r['arrived']}**(first_seen_at) 중 새 생성 {r['new_clips']} · "
                   f"늦은 적재 {r['arrived'] - r['new_clips']} · 후보에서 뺀 비생성 {r['non_gen_skipped']} "
                   f"(입력 있고 Suno 쪽 새 낱말 있음 {r['new_clips_with_input_and_extra']})")
        old_models = set(st.get("models", {}))
        new_models = [m for m in r["models"] if old_models and m not in old_models]
        out.append(f"- [자생] model_name 새 것: {new_models or '0'} — ⚠이름 ≠ 새 생성 모델 · 용도(gen_method/clip_type:행) "
                   f"{ {m: r['model_kinds'].get(m) for m in new_models} }")
        out.append(f"- [자생] model 현황 {r['models']}")
        out.append(f"- [자생] suno_emitted 미등재 후보 낱말(곡 아님 · 클립 수) — **Suno 단독**(전 입력 코퍼스에 없음): "
                   f"{r['candidate_suno_only']} · 되울림(다른 곡 입력에 있음 · 후보 아님): {r['candidate_echo']}")
        st["models"] = r["models"]
        st["emitted_checked_at"] = now.isoformat()
    except Exception as e:
        out.append(f"- [자생] **미측정**({type(e).__name__}: {e})")
    out += ["", "▶ 새 글·Edited 바뀜 = 노트(`agent-comm:projects/sunolanguage/exchange/suno_docs_study_20261019/`) 대조 1주 안 · "
            "후보 낱말 = build_suno_emitted 재적재 여부 판단(등재 ≠ 원인)."]
    st["checked_at"] = now.isoformat()
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1))
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"{now:%Y%m%d_%H%M}.md").write_text("\n".join(out) + "\n")
    (REPORTS / f"{now:%Y%m%d_%H%M}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    print("\n".join(out))


if __name__ == "__main__":
    main()
