#!/usr/bin/env python3
"""
책 집필 중 상시 사용 lexical 검색기 (sqlite FTS5).

사용:
  # 인덱스 빌드 (최초/데이터 갱신 시)
  python3 scripts/lexical_search_cli.py build

  # 검색
  python3 scripts/lexical_search_cli.py q "fingerpicked"
  python3 scripts/lexical_search_cli.py q "warm" --slot=instrument
  python3 scripts/lexical_search_cli.py q "vinyl crackle" --source=sp --limit=5
  python3 scripts/lexical_search_cli.py q "chord progression" --count
  python3 scripts/lexical_search_cli.py q '"close mic"' --genre="K-Pop"
  python3 scripts/lexical_search_cli.py q "syncopated" --kit=bass --role=execute
  python3 scripts/lexical_search_cli.py q "*" --kit=guitar --layer=lead --count

출력: 매칭 문장(slot/source/genre/song_id 메타 포함).
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "reanalysis_v2"
PROMPTS = REPO / "data" / "prompts"
DB = DATA / "lexical_index.sqlite"

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'of', 'is',
    'with', 'for', 'by', 'its', 'it', 'as', 'are', 'was', 'has', 'be',
    'from', 'this', 'that', 'which', 'into', 'each', 'both', 'while',
}
SECTION_RE = re.compile(
    r'^(Intro|Verse|Chorus|Bridge|Outro|Pre-Chorus|Hook|Section|'
    r'Instrumental|Refrain|Interlude|Build|Climax|Main|Drop|Guitar Solo)\b', re.I
)
SOURCE_COL = {
    'sp_entity': 'sp', 'suno_sp_full': 'sp', 'leomusic_sp_full': 'sp',
    'bracket_entity': 'bracket',
    'stems_sp': 'stems_sp',
    'stems_bracket': 'stems_bracket',
}


def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s\-]', ' ', text)
    return [w for w in text.split() if len(w) >= 2 and w not in STOPWORDS]


def build_index():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 일반 테이블 + FTS5 virtual (contentless 아님 — 검색 후 메타 조회용)
    c.execute("""
        CREATE TABLE entries (
            id INTEGER PRIMARY KEY,
            source TEXT,
            slot TEXT,
            song_id INTEGER,
            genre TEXT,
            sentence TEXT,
            entity TEXT,
            modifiers TEXT,
            pattern TEXT,
            kit TEXT,
            layer TEXT,
            role TEXT,
            role_details TEXT
        )
    """)
    c.execute("""
        CREATE VIRTUAL TABLE entries_fts USING fts5(
            sentence, entity, modifiers, pattern,
            content='entries', content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        )
    """)
    c.execute("""
        CREATE TRIGGER entries_ai AFTER INSERT ON entries BEGIN
            INSERT INTO entries_fts(rowid, sentence, entity, modifiers, pattern)
            VALUES (new.id, new.sentence, new.entity, new.modifiers, new.pattern);
        END
    """)

    def fmt(val):
        if val is None:
            return ""
        if isinstance(val, (list, tuple, dict)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)

    rows = []
    rid = 0

    # v3 entity JSON 두 개
    for fname, src_label in (("sp_entities_v3.json", "sp_entity"),
                             ("bracket_entities_v3.json", "bracket_entity")):
        p = DATA / fname
        if not p.exists():
            continue
        arr = json.loads(p.read_text())
        for e in arr:
            rid += 1
            text = e.get("sentence") or e.get("bracket") or ""
            rows.append((
                rid, src_label, e.get("slot", ""),
                e.get("song_id"), e.get("genre", ""),
                text,
                fmt(e.get("entity", "")),
                fmt(e.get("modifiers", [])),
                fmt(e.get("pattern", "") or e.get("delivery", "") or e.get("action", "")),
                e.get("kit", "") or "",
                e.get("layer", "") or "",
                e.get("role", "") or "",
                fmt(e.get("role_details", [])),
            ))

    # raw SP (Suno 재분석) — 문장 단위로 추가하면 중복이 많으므로 곡 전체 문단을 한 행으로
    merged = json.loads((DATA / "merged_4values.json").read_text())
    for s in merged:
        sid = s.get("song_id")
        genre = s.get("genre", "")
        for sr in s.get("suno_reanalysis", []):
            sp = sr.get("sp") or ""
            if sp:
                rid += 1
                rows.append((rid, "suno_sp_full", "", sid, genre, sp, "", "", "", "", "", "", ""))
        lo = s.get("leomusic_original") or {}
        if lo.get("sp"):
            rid += 1
            rows.append((rid, "leomusic_sp_full", "", sid, genre, lo["sp"], "", "", "", "", "", "", ""))

    # stems from prompts/*.json
    if PROMPTS.exists():
        for pf in sorted(PROMPTS.glob("*.json")):
            pdata = json.loads(pf.read_text())
            if pdata.get("status") != "ok":
                continue
            sid = pdata.get("id")
            genre = pdata.get("genre", "")
            stem_type = None
            for stem_name, stem in pdata.get("stems", {}).items():
                if not isinstance(stem, dict) or stem.get("status") != "ok":
                    continue
                stem_type = stem_name
                tags = stem.get("tags", "")
                if tags:
                    for sent in re.split(r'(?<=[.!?])\s+', tags):
                        sent = sent.strip().rstrip('.')
                        if not sent or len(sent) < 10:
                            continue
                        rid += 1
                        rows.append((rid, "stems_sp", "", sid, genre, sent,
                                     "", "", "", "", "", "", ""))
                prompt = stem.get("prompt", "")
                if prompt:
                    brackets = re.findall(r'\[([^\]]+)\]', prompt)
                    for b in brackets:
                        rid += 1
                        slot = "section" if SECTION_RE.match(b) else ""
                        rows.append((rid, "stems_bracket", slot, sid, genre, b,
                                     "", "", "", "", "", "", ""))

    c.executemany(
        "INSERT INTO entries("
        "id,source,slot,song_id,genre,sentence,entity,modifiers,pattern,"
        "kit,layer,role,role_details) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )

    # 일반 인덱스
    c.execute("CREATE INDEX idx_slot ON entries(slot)")
    c.execute("CREATE INDEX idx_source ON entries(source)")
    c.execute("CREATE INDEX idx_genre ON entries(genre)")
    c.execute("CREATE INDEX idx_song ON entries(song_id)")
    c.execute("CREATE INDEX idx_kit ON entries(kit)")
    c.execute("CREATE INDEX idx_layer ON entries(layer)")
    c.execute("CREATE INDEX idx_role ON entries(role)")

    # --- words / phrases / word_phrase_map ---
    c.execute("""
        CREATE TABLE words (
            id INTEGER PRIMARY KEY,
            word TEXT UNIQUE NOT NULL,
            freq_total INTEGER DEFAULT 0,
            freq_sp INTEGER DEFAULT 0,
            freq_bracket INTEGER DEFAULT 0,
            freq_stems_sp INTEGER DEFAULT 0,
            freq_stems_bracket INTEGER DEFAULT 0
        )
    """)
    c.execute("CREATE INDEX idx_word ON words(word)")

    c.execute("""
        CREATE TABLE phrases (
            id INTEGER PRIMARY KEY,
            phrase TEXT NOT NULL,
            source TEXT NOT NULL,
            song_id INTEGER,
            genre TEXT,
            slot TEXT
        )
    """)
    c.execute("CREATE INDEX idx_phrase ON phrases(phrase)")
    c.execute("CREATE INDEX idx_phrase_source ON phrases(source)")

    c.execute("""
        CREATE TABLE word_phrase_map (
            word_id INTEGER NOT NULL,
            phrase_id INTEGER NOT NULL,
            position INTEGER,
            PRIMARY KEY (word_id, phrase_id, position),
            FOREIGN KEY (word_id) REFERENCES words(id),
            FOREIGN KEY (phrase_id) REFERENCES phrases(id)
        )
    """)

    word_freq = {}
    phrases_list = []
    word_phrase_links = []

    for row in rows:
        rid_r, source, slot, sid, genre, sentence, entity, *_ = row
        text = entity if entity else sentence
        if not text:
            continue
        col = SOURCE_COL.get(source, 'sp')
        phrase_idx = len(phrases_list)
        phrases_list.append((text, source, sid, genre, slot))

        words = tokenize(text)
        for pos, w in enumerate(words):
            if w not in word_freq:
                word_freq[w] = {'sp': 0, 'bracket': 0, 'stems_sp': 0, 'stems_bracket': 0}
            word_freq[w][col] += 1
            word_phrase_links.append((w, phrase_idx, pos))

    word_id_map = {}
    for i, w in enumerate(sorted(word_freq.keys()), 1):
        word_id_map[w] = i

    c.executemany(
        "INSERT INTO words(id, word, freq_total, freq_sp, freq_bracket, "
        "freq_stems_sp, freq_stems_bracket) VALUES(?,?,?,?,?,?,?)",
        [(word_id_map[w], w, sum(f.values()), f['sp'], f['bracket'],
          f['stems_sp'], f['stems_bracket'])
         for w, f in sorted(word_freq.items())]
    )

    c.executemany(
        "INSERT INTO phrases(id, phrase, source, song_id, genre, slot) VALUES(?,?,?,?,?,?)",
        [(i + 1, p[0], p[1], p[2], p[3], p[4]) for i, p in enumerate(phrases_list)]
    )

    c.executemany(
        "INSERT OR IGNORE INTO word_phrase_map(word_id, phrase_id, position) VALUES(?,?,?)",
        [(word_id_map[w], pidx + 1, pos) for w, pidx, pos in word_phrase_links]
    )

    conn.commit()
    print(f"✔ 인덱스 빌드 완료: {DB} ({len(rows):,} entries)")
    c.execute("SELECT source, COUNT(*) FROM entries GROUP BY source")
    for src, n in c.fetchall():
        print(f"    {src:22s} {n:6d}")
    c.execute("SELECT COUNT(*) FROM words")
    print(f"    {'words':22s} {c.fetchone()[0]:6d} unique")
    c.execute("SELECT COUNT(*) FROM phrases")
    print(f"    {'phrases':22s} {c.fetchone()[0]:6d}")
    c.execute("SELECT COUNT(*) FROM word_phrase_map")
    print(f"    {'word→phrase links':22s} {c.fetchone()[0]:6d}")
    conn.close()


def query(args):
    if not DB.exists():
        print(f"인덱스 없음 — 먼저 실행: python3 {Path(__file__).name} build", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # FTS5 MATCH — 따옴표 유지 (구문 검색 지원). '*'는 전체 매칭으로 취급.
    fts_match = args.query
    use_fts = fts_match != "*"
    where = []
    params = []
    if use_fts:
        where.append("entries_fts MATCH ?")
        params.append(fts_match)
    if args.slot:
        where.append("e.slot = ?")
        params.append(args.slot)
    if args.source:
        where.append("e.source = ?")
        params.append(args.source)
    if args.genre:
        where.append("e.genre LIKE ?")
        params.append(f"%{args.genre}%")
    if args.song_id is not None:
        where.append("e.song_id = ?")
        params.append(args.song_id)
    if args.kit:
        where.append("e.kit = ?")
        params.append(args.kit)
    if args.layer:
        where.append("e.layer = ?")
        params.append(args.layer)
    if args.role:
        where.append("e.role = ?")
        params.append(args.role)

    where_sql = " AND ".join(where) if where else "1=1"
    join_sql = "JOIN entries_fts f ON f.rowid = e.id" if use_fts else ""
    order_sql = "ORDER BY rank" if use_fts else "ORDER BY e.id"

    if args.count:
        sql = (
            f"SELECT COUNT(*) FROM entries e {join_sql} "
            f"WHERE {where_sql}"
        )
        c.execute(sql, params)
        print(c.fetchone()[0])
        return

    sql = (
        "SELECT e.source, e.slot, e.song_id, e.genre, e.sentence, "
        "e.entity, e.modifiers, e.kit, e.layer, e.role "
        f"FROM entries e {join_sql} "
        f"WHERE {where_sql} "
        f"{order_sql} LIMIT ?"
    )
    params.append(args.limit)
    c.execute(sql, params)

    n = 0
    for src, slot, sid, genre, sentence, entity, modifiers, kit, layer, role in c.fetchall():
        n += 1
        head = f"[{src}]"
        if slot:
            head += f"[{slot}]"
        if kit:
            head += f"[{kit}/{layer or '-'}/{role or '-'}]"
        head += f" song#{sid}  ({genre})"
        print(head)
        print(f"    {sentence[:240]}")
        if entity and entity not in ('""', '[]'):
            print(f"    entity={entity}  mods={modifiers}")
        print()
    print(f"--- {n} matches (limit={args.limit}) ---")


def word_query(args):
    if not DB.exists():
        print(f"인덱스 없음 — 먼저 실행: python3 {Path(__file__).name} build", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    word = args.word.lower().strip()

    c.execute("SELECT id, freq_total, freq_sp, freq_bracket, freq_stems_sp, freq_stems_bracket "
              "FROM words WHERE word = ?", (word,))
    row = c.fetchone()
    if not row:
        if args.like:
            c.execute("SELECT word, freq_total, freq_sp, freq_bracket, freq_stems_sp, freq_stems_bracket "
                       "FROM words WHERE word LIKE ? ORDER BY freq_total DESC LIMIT ?",
                       (f"%{word}%", args.limit))
            matches = c.fetchall()
            if not matches:
                print(f"'{word}' 포함 단어 없음")
                return
            print(f"'{word}' 포함 단어 {len(matches)}개:")
            for w, ft, fsp, fbr, fss, fsb in matches:
                print(f"  {w:30s}  total={ft:4d}  sp={fsp:4d}  bracket={fbr:4d}  stems_sp={fss:4d}  stems_bracket={fsb:4d}")
            return
        print(f"'{word}' 미발견. --like 옵션으로 부분 검색 가능")
        return

    wid, ft, fsp, fbr, fss, fsb = row
    print(f"단어: {word}")
    print(f"  빈도: total={ft}  sp={fsp}  bracket={fbr}  stems_sp={fss}  stems_bracket={fsb}")

    c.execute("""
        SELECT p.phrase, p.source, p.genre
        FROM word_phrase_map m JOIN phrases p ON m.phrase_id = p.id
        WHERE m.word_id = ?
        ORDER BY p.source, p.phrase
        LIMIT ?
    """, (wid, args.limit))
    phrases = c.fetchall()
    if phrases:
        print(f"\n  연결 구문 ({len(phrases)}개):")
        for phrase, src, genre in phrases:
            print(f"    [{src:15s}] ({genre[:20] if genre else '-':20s}) {phrase[:120]}")

    conn.close()


def word_top(args):
    if not DB.exists():
        print(f"인덱스 없음", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    col = f"freq_{args.source}" if args.source else "freq_total"
    valid_cols = {'freq_total', 'freq_sp', 'freq_bracket', 'freq_stems_sp', 'freq_stems_bracket'}
    if col not in valid_cols:
        print(f"잘못된 source: {args.source}. 사용: sp/bracket/stems_sp/stems_bracket")
        return

    where = f"WHERE {col} > 0" if args.source else ""
    c.execute(f"SELECT word, freq_total, freq_sp, freq_bracket, freq_stems_sp, freq_stems_bracket "
              f"FROM words {where} ORDER BY {col} DESC LIMIT ?", (args.limit,))

    print(f"{'word':30s} {'total':>6s} {'sp':>6s} {'brkt':>6s} {'st_sp':>6s} {'st_br':>6s}")
    print("-" * 80)
    for w, ft, fsp, fbr, fss, fsb in c.fetchall():
        print(f"{w:30s} {ft:6d} {fsp:6d} {fbr:6d} {fss:6d} {fsb:6d}")
    conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="sqlite FTS5 인덱스 빌드")

    qp = sub.add_parser("q", help="쿼리")
    qp.add_argument("query", help="FTS5 검색어 (따옴표로 구문 검색: '\"close mic\"')")
    qp.add_argument("--slot", help="슬롯 제한 (instrument/drums/tempo_key_time/...)")
    qp.add_argument("--source", help="소스 제한 (sp_entity/bracket_entity/suno_sp_full/leomusic_sp_full/stems_sp/stems_bracket)")
    qp.add_argument("--genre", help="장르 LIKE 제한")
    qp.add_argument("--song-id", type=int, help="특정 곡")
    qp.add_argument("--kit", help="악기 family (guitar/bass/keys/synth/strings/brass/other)")
    qp.add_argument("--layer", help="텍스처 층 (lead/rhythm/bass/pad/fill/unspecified)")
    qp.add_argument("--role", help="기능 (execute/groove_lock/support/fill/layer_on/lead_out/sustain)")
    qp.add_argument("--limit", type=int, default=15, help="결과 상한 (기본 15)")
    qp.add_argument("--count", action="store_true", help="매칭 개수만 출력")

    wqp = sub.add_parser("wq", help="단어 검색 (words 테이블)")
    wqp.add_argument("word", help="검색할 단어")
    wqp.add_argument("--like", action="store_true", help="부분 매칭 (LIKE)")
    wqp.add_argument("--limit", type=int, default=30, help="결과 상한")

    wtp = sub.add_parser("wtop", help="빈도 상위 단어")
    wtp.add_argument("--source", help="소스 제한 (sp/bracket/stems_sp/stems_bracket)")
    wtp.add_argument("--limit", type=int, default=50, help="결과 상한")

    args = ap.parse_args()
    if args.cmd == "build":
        build_index()
    elif args.cmd == "wq":
        word_query(args)
    elif args.cmd == "wtop":
        word_top(args)
    else:
        query(args)


if __name__ == "__main__":
    main()
