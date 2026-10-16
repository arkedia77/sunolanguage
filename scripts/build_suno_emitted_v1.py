#!/usr/bin/env python3
"""build_suno_emitted_v1.py — «Suno 자생 어휘» 층(suno_emitted) 적재.

발주: encore 2026-10-16 21:31 `213116` · LEO «우리가 안 넣고 수노가 자연생성시킨거면 당연히 늘어난 거지».
정의: **우리 입력 SP 에 없는데 Suno 의 metadata.tags 에 나온 낱말·구절.** 원인(슬라이더·장르·Variety)은 묻지 않는다.

⛔attested(expr_concepts · 문턱 30)와 다른 층이다 — 이 층에는 문턱을 적용하지 않고, attested 를 건드리지 않는다.
   표기 = «Suno 가 쓰는 말 = Suno 가 알아듣는 말 [추정 · 입력 실측 전]».

출처 3갈래(클립 단위 중복 제거 · 앞 갈래 우선):
  A  내 suno_sp_emissions 중 Variety ≥1 (재작성분) — 입력 = 같은 gid 의 Variety 0 메아리 행(= 우리 SP 원문)
  B  census «DB 배치 ∧ 입력 SP ≠ Suno tags» — 입력 = input_sp_ours
  C  census DB 행 없음 ∧ (커버 · agentic 리믹스 · style_weight > 0.5) — 입력 미상 ⇒ 우리 SP 집합과 글자 동일한 tags 는 버림
⛔Variety 0 메아리는 넣지 않는다(10-16 내 자기정정: 그 행은 우리 SP 를 그대로 돌려준 것).
⛔C 의 «화면 직접» 은 LEO 가 친 말인지 Suno 가 쓴 말인지 메타로 못 가린다 ⇒ author_known=0 으로 따로 적는다.

사용: .venv/bin/python scripts/build_suno_emitted_v1.py [--dry-run]
"""
import csv, gzip, io, json, re, sqlite3, sys, collections
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "sunolang.db"
CENSUS = Path.home() / "agent-comm-sunolanguage/projects/sunomusic/attachments/V6_CENSUS_20261016/v6_census_all.csv.gz"
STOP = set("a an the and with of in into to on for at by from its it as is that this over under then while "
           "through between across up down out off but or so very more most than each every both all".split())
REC = (r"recording|recorded|miked|mic'd|close-mic|unprocessed|processed|roomy|room sound|room ambience|room tone|"
       r"uncluttered|dynamics|\bdry\b|\bwet\b|reverb|saturation|\btape\b|studio|compression|compressed|\bmix\b|mixed|"
       r"ambience|\bproduction\b|produced|lo-fi|polished|unpolished")


def words(s):
    return {w for w in re.findall(r"[a-z][a-z\-']+", s.lower()) if w not in STOP and len(w) > 2}


def phrases(s):
    out = set()
    for p in re.split(r"[,;.\n]", s.lower()):
        p = re.sub(r"\s+", " ", p).strip(" -")
        if 2 <= len(p.split()) <= 6:
            out.add(p)
    return out


def main(dry):
    rows = list(csv.DictReader(io.TextIOWrapper(gzip.open(CENSUS), encoding="utf-8-sig")))
    cen = {r["clip"]: r for r in rows}
    ours = {(r["input_sp_ours"] or "").strip().lower() for r in rows if r["input_sp_ours"] not in ("", "DB 행 없음")}
    db = sqlite3.connect(DB)
    em = db.execute("select clip_uuid, gid, aug_creativity, emitted_sp from suno_sp_emissions").fetchall()
    v0 = {g: t for u, g, a, t in em if not a}
    ours |= {t.strip().lower() for t in v0.values() if t}

    src = []  # (clip, song_key, created, source, input_text|None, tags, author_known)
    seen = set()
    for u, g, a, t in em:
        if a and t and g in v0:
            c = cen.get(u, {})
            src.append((u, f"gid{g}", (c.get("created_at") or "")[:10], "A_variety", v0[g], t, 1)); seen.add(u)
    for r in rows:
        if r["clip"] in seen:
            continue
        sw = None
        try: sw = float(r["style_weight"])
        except ValueError: pass
        tags = r["suno_tags"] or ""
        if not tags:
            continue
        if r["method"] == "DB 배치" and r["input_eq_suno_tags"] == "False":
            # B 는 v1.2 에서 되살린다(10-16 22:0x). v1.1 의 제외 근거였던 sunomusic `215544` «40/40 사후 수정»을
            #   저자가 `220109` 에서 철회했다(절반 gid 충돌 · 절반 04-17 이관 판 차이). 그리고 감사 로그(songs_audit_log)
            #   실측상 이 140클립(70곡)은 생성 뒤 style_prompt 수정 0 ⇒ 입력 칸을 믿을 근거가 있다.
            #   ⛔그 감사 로그를 나는 못 연다(role_sunolanguage permission denied) — 근거는 sunomusic 실측(남의 값)이다.
            #   ⚠30클립은 Variety 0 인데 Suno tags 가 우리 SP 와 다르다 — «V0 = 메아리» 성질의 예외인지 미분해.
            src.append((r["clip"], f"gid{r['gid']}", r["created_at"][:10], "B_db_diff", r["input_sp_ours"], tags, 1)); seen.add(r["clip"])
        elif r["input_sp_ours"] in ("", "DB 행 없음") and (r["method"] in ("커버", "agentic 리믹스") or (sw or 0) > 0.5):
            if tags.strip().lower() in ours:
                continue
            key = f"{r['account']}|{r['title'] or r['created_at'][:16]}"
            known = 1 if r["method"] in ("커버", "agentic 리믹스") else 0
            src.append((r["clip"], key, r["created_at"][:10], "C_no_input", None, tags, known)); seen.add(r["clip"])

    agg = collections.defaultdict(lambda: {"clips": set(), "songs": set(), "first": "9999", "src": collections.Counter(), "known": 0})
    for clip, song, day, s, inp, tags, known in src:
        iw, ip = (words(inp), phrases(inp)) if inp else (set(), set())
        il = (inp or "").lower()
        for kind, items in (("word", words(tags) - iw), ("phrase", {p for p in phrases(tags) - ip if p not in il})):
            for t in items:
                a = agg[(t, kind)]
                a["clips"].add(clip); a["songs"].add(song); a["src"][s] += 1; a["known"] = max(a["known"], known)
                if day and day < a["first"]:
                    a["first"] = day
    con = {t.lower(): n for t, n in db.execute("select suno_term, attested_count from expr_concepts")}
    out = [(t, k, len(a["clips"]), len(a["songs"]), a["first"], json.dumps(dict(a["src"]), ensure_ascii=False),
            a["known"], con.get(t)) for (t, k), a in agg.items()]
    print(f"출처 클립 {len(src)} = " + str(collections.Counter(x[3] for x in src)) + f" · 낱말·구절 {len(out)}")
    if dry:
        return out
    db.execute("""create table if not exists suno_emitted_terms(
        term text, kind text, n_clips int, n_songs int, first_seen text, sources text,
        author_known int, attested_count int, layer text default 'suno_emitted',
        note text default 'Suno 가 쓰는 말 = Suno 가 알아듣는 말 [추정 · 입력 실측 전]',
        build text, primary key(term, kind))""")
    db.execute("delete from suno_emitted_terms")
    db.executemany("insert into suno_emitted_terms(term,kind,n_clips,n_songs,first_seen,sources,author_known,attested_count,build) "
                   "values(?,?,?,?,?,?,?,?,'v1.2 2026-10-16 census V6_CENSUS_20261016 (B 복원)')", out)
    # 범주 «녹음·믹스·공간·처리»(encore 213228 · LEO «레코딩; 이런 거 없었잖아») — 낱말 경계 정규식, 사람 손 분류 아님
    cols = [r[1] for r in db.execute("pragma table_info(suno_emitted_terms)")]
    if "category" not in cols:
        db.execute("alter table suno_emitted_terms add column category text")
    db.create_function("rx", 2, lambda p, s: 1 if s and re.search(p, s) else 0)
    db.execute("update suno_emitted_terms set category = case when rx(?, term) then 'recording_production' end", (REC,))
    # 시작일 주석(encore 213530 · LEO 증언 «수노 6.0 이전엔 그런 게 없었으니까» — 데이터 대조 아님)
    #   ⛔녹음 상황어는 반증 조건이 이미 걸렸다: v6 이전 Suno 녹음 인식 프롬프트(tracks.suno_prompt 79 · 적재 2026-03-28)
    #     에 51건 — 「생성 tags 재작성」은 v6 부터지만 「Suno 가 그 말을 썼다」는 v6 이전부터다.
    db.execute("""create table if not exists suno_emitted_meta(k text primary key, v text)""")
    db.execute("delete from suno_emitted_meta where k='b_excluded'")  # v1.1 의 철회된 근거 — 남기지 않는다(경위는 b_restored 에)
    db.executemany("insert or replace into suno_emitted_meta values(?,?)", [
        ("v6_before", "v6(2026-09-10) 이전 «생성 시 Suno 자생 tags» 없음 — 출처 LEO 증언 10-16(encore 213530) · 데이터 대조 아님 · "
                      "반증 조건 = 09-10 이전 생성 클립에서 입력에 없는 Suno tags 가 나오면 고침"
                      " · ⚠10-16 21:4x 반증 후보: PG suno_clip_style v6 이전 8,716(입력 있음) 중 Suno SP ≠ 우리 입력 1,142 · Suno 쪽 새 낱말 ≥3 = 337(chirp-crow 224·fenix 112 · 02~08월) — 단 songs.style_prompt 가 생성 당시 값인지 미확인(updated_at > 클립 생성 1,139/1,142 · 잘림 444) · ⛔21:55 sunomusic 215544 «40/40 사후 수정»은 22:01 `220109` 에서 저자 철회(gid 충돌 20 · 04-17 이관 판 차이 20) ⇒ 그 40 은 증언의 근거도 반증도 아님 · 감사 로그상 생성 뒤 SP 수정은 96건/93곡(대부분 role_leomusic2 6월 · 9월 이후 0) ⇒ v6 이전 1,142 는 여전히 **미판정**(감사 로그 시작 04-18 이전 이관분 섞임 · encore 220236)"),
        ("b_restored", "v1.2(10-16 22:0x): 출처 B(140클립·70곡) 복원 — v1.1 제외 근거(sunomusic 215544)가 저자 철회(220109) · 감사 로그상 생성 뒤 SP 수정 0(sunomusic 실측 · 내 role 은 로그 열람 권한 없음) · ⚠그중 Variety 0 인데 다름 30 = 미분해"),
        ("semicolon_form", "세미콜론 블록 꼴 = v6 와 함께 시작 [LEO 증언] · v6 이전 Suno 녹음 인식 프롬프트 79 중 ; 0 건과 정합"),
        ("recording_category", "⛔«v6 와 함께 시작» 아님 — v6 이전 Suno 녹음 인식 프롬프트(tracks 79)에 녹음 상황어 51건"
                               "(mix·recording·saturation·tape·close-mic·polished) · first_seen 09-10 은 이 층(생성 tags)의 시작일일 뿐 · "
                               "attested 사전 0 은 Suno 가 안 쓴 게 아니라 우리 사전 추출이 못 담은 것"),
    ])
    db.commit()
    print("적재", db.execute("select count(*) from suno_emitted_terms").fetchone()[0],
          "· recording_production", db.execute("select count(*) from suno_emitted_terms where category='recording_production'").fetchone()[0])
    return out


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
