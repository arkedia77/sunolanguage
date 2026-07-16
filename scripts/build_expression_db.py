#!/usr/bin/env python3
"""표현 레이어 v0 빌더 — 설계: docs/expression_layer_design.md

사전 v3.2에서 원자 어휘(코어)를 추출해 sunolang.db expr_* 테이블에 적재하고,
data/expressions/authored/*.json (저작 레지스터 정본)과
data/expressions/inbound_aliases_seed.json (역방향 별칭)을 합류시킨다.

사용:
  python3 scripts/build_expression_db.py --export-worklist   # 저작용 워크리스트 생성
  python3 scripts/build_expression_db.py --build             # DB 적재(스키마+개념+저작분+별칭+FTS)
  python3 scripts/build_expression_db.py --coverage          # 저작 커버리지 리포트
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT_PATH = ROOT / "rag" / "suno_dictionary_v3.json"
DB_PATH = ROOT / "sunolang.db"
AUTHORED_DIR = ROOT / "data" / "expressions" / "authored"
WORKLIST_DIR = ROOT / "data" / "expressions" / "worklists"
ALIAS_SEED = ROOT / "data" / "expressions" / "inbound_aliases_seed.json"

# 사전 카테고리 → 표현 레이어 카테고리
CATEGORY_MAP = {
    "instrument_phrases": "instrument",
    "drum_vocab": "drums",
    "technique_patterns": "technique",
    "production_vocab": "production",
    "mood_emotion": "mood",
    "tempo_rhythm": "tempo_rhythm",
    "dynamics_structure": "dynamics",
    "timbre_texture": "timbre",
    "vocal_expressions": "vocal",
    "vocal_chorus": "vocal_chorus",
    "harmony_vocab": "harmony",
}

REGISTERS = [
    ("suno_native", "suno", "정본 — Suno가 자기 말로 쓰는 어휘 (SP 작성용)"),
    ("music_theory_en", "human_expert", "음악이론·실무 정식 용어 (음악가/전문가)"),
    ("plain_ko", "human_ko", "한국어 일상어 설명 (비전공자가 소리를 떠올릴 수 있게)"),
    ("plain_en", "human_en", "영어 일상어 설명"),
    ("llm_prompt", "external_llm", "타 음악생성 AI 프롬프트 토큰 (MusicGen/Stable Audio류)"),
    ("tags", "machine", "기계 교환용 파셋 태그 배열(JSON)"),
]

AUTHORED_FIELDS = ["music_theory_en", "plain_ko", "plain_en", "llm_prompt", "tags"]

# 에이전트 저작 배치 분할 (406 원자 + 시드 extras → 5그룹)
WORKLIST_GROUPS = {
    "g1_instrument_drums": ["instrument", "drums"],
    "g2_technique": ["technique"],
    "g3_production_timbre": ["production", "timbre"],
    "g4_mood_tempo_dynamics": ["mood", "tempo_rhythm", "dynamics", "genre"],
    "g5_vocal_harmony": ["vocal", "vocal_chorus", "harmony"],
}


def slugify(term: str) -> str:
    s = term.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s or "unknown"


def extract_atoms():
    """컴파운드 키 분해 → 원자별 {카테고리: count합} 집계 → 교차 카테고리 dedup.

    반환: {norm_term: {"suno_term": str, "primary_category": str,
                       "attested_count": int, "source_categories": [str,...]}}
    attested_count는 컴파운드 중복 합산 근사치(salience 순서용) — 설계 §2.
    """
    d = json.loads(DICT_PATH.read_text())
    dict_version = str(d.get("version", "?"))
    per_atom = {}  # norm_term -> {category: count}
    display = {}   # norm_term -> 원표기
    for dict_cat, cat in CATEGORY_MAP.items():
        for key, val in d[dict_cat].items():
            cnt = val.get("count", 0) if isinstance(val, dict) else 0
            if key.startswith("["):
                try:
                    terms = json.loads(key)
                except json.JSONDecodeError:
                    terms = [key]
            else:
                terms = [key]
            for t in terms:
                t = t.strip()
                if not t:
                    continue
                # slug 기준 병합: 'drop ' vs 'drop', 하이픈/공백 변형을 한 원자로
                norm = slugify(t)
                per_atom.setdefault(norm, {})
                per_atom[norm][cat] = per_atom[norm].get(cat, 0) + cnt
                if norm not in display or len(t) < len(display[norm]):
                    display[norm] = t
    atoms = {}
    for norm, cats in per_atom.items():
        primary = max(cats, key=cats.get)
        atoms[norm] = {
            "suno_term": display[norm],
            "primary_category": primary,
            "attested_count": sum(cats.values()),
            "source_categories": sorted(cats),
            "origin": "dictionary",
        }
    # 별칭 시드 extra_concepts 합류 (사전 상위 원자 밖이지만 attested 확인분 — 설계 §4)
    if ALIAS_SEED.exists():
        seed = json.loads(ALIAS_SEED.read_text())
        for ec in seed.get("extra_concepts", []):
            norm = slugify(ec["suno_term"])
            if norm in atoms:
                continue
            atoms[norm] = {
                "suno_term": ec["suno_term"],
                "primary_category": ec["category"],
                "attested_count": ec.get("attested_count", 0),
                "source_categories": [ec["category"]],
                "origin": "alias_seed",
            }
    return atoms, dict_version


def concept_id_of(atom):
    return f"{atom['primary_category']}:{slugify(atom['suno_term'])}"


def cmd_export_worklist():
    atoms, dict_version = extract_atoms()
    WORKLIST_DIR.mkdir(parents=True, exist_ok=True)
    by_cat = {}
    for a in atoms.values():
        by_cat.setdefault(a["primary_category"], []).append(a)
    total = 0
    for group, cats in WORKLIST_GROUPS.items():
        entries = []
        for c in cats:
            entries += sorted(by_cat.get(c, []), key=lambda x: -x["attested_count"])
        out = {
            "group": group,
            "dict_version": dict_version,
            "entries": [
                {"suno_term": e["suno_term"], "category": e["primary_category"],
                 "attested_count": e["attested_count"],
                 "source_categories": e["source_categories"]}
                for e in entries
            ],
        }
        p = WORKLIST_DIR / f"{group}.json"
        p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
        total += len(entries)
        print(f"{group}: {len(entries)}원자 → {p.relative_to(ROOT)}")
    print(f"총 {total}원자 / {len(atoms)} unique")


def load_authored():
    """저작 정본 로드. 반환: {norm_term: {field: value, '_confidence': str, '_file': str}}"""
    authored = {}
    if not AUTHORED_DIR.exists():
        return authored
    for p in sorted(AUTHORED_DIR.glob("*.json")):
        data = json.loads(p.read_text())
        for e in data.get("entries", []):
            norm = slugify(e["suno_term"])
            if norm in authored:
                print(f"  [warn] 중복 저작 {norm} ({p.name}) — 선착 유지", file=sys.stderr)
                continue
            e["_file"] = p.name
            authored[norm] = e
    return authored


def cmd_build():
    atoms, dict_version = extract_atoms()
    authored = load_authored()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS expr_registers (
      register TEXT PRIMARY KEY,
      audience TEXT NOT NULL,
      description TEXT
    );
    CREATE TABLE IF NOT EXISTS expr_concepts (
      concept_id TEXT PRIMARY KEY,
      category TEXT NOT NULL,
      suno_term TEXT NOT NULL UNIQUE,
      attested_count INTEGER NOT NULL DEFAULT 0,
      source_categories TEXT,           -- JSON array
      dict_version TEXT,
      origin TEXT NOT NULL DEFAULT 'dictionary',  -- dictionary | alias_seed
      is_dead_zone INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    CREATE INDEX IF NOT EXISTS idx_expr_concepts_category ON expr_concepts(category);
    CREATE TABLE IF NOT EXISTS expr_expressions (
      id INTEGER PRIMARY KEY,
      concept_id TEXT NOT NULL REFERENCES expr_concepts(concept_id),
      register TEXT NOT NULL REFERENCES expr_registers(register),
      text TEXT NOT NULL,
      method TEXT NOT NULL,             -- canonical | authored_llm | glossary
      confidence TEXT DEFAULT 'high',   -- high | medium | low
      notes TEXT,
      UNIQUE(concept_id, register)
    );
    CREATE TABLE IF NOT EXISTS expr_inbound_aliases (
      id INTEGER PRIMARY KEY,
      alias_text TEXT NOT NULL,
      alias_lang TEXT NOT NULL,         -- ko | en
      kind TEXT NOT NULL,               -- dead_zone | ko_glossary | blocked
      target_concept_id TEXT REFERENCES expr_concepts(concept_id),
      replacement_note TEXT,
      source TEXT,
      UNIQUE(alias_text, kind)
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS expr_fts USING fts5(
      concept_id UNINDEXED, register, text
    );
    """)
    # 재적재: 파생 테이블 비우고 정본에서 재구성 (설계 §7 — DB는 파생물)
    cur.execute("DELETE FROM expr_fts")
    cur.execute("DELETE FROM expr_expressions")
    cur.execute("DELETE FROM expr_inbound_aliases")
    cur.execute("DELETE FROM expr_concepts")
    cur.execute("DELETE FROM expr_registers")
    cur.executemany("INSERT INTO expr_registers VALUES (?,?,?)", REGISTERS)

    n_expr = 0
    for norm, a in sorted(atoms.items()):
        cid = concept_id_of(a)
        cur.execute(
            "INSERT INTO expr_concepts (concept_id, category, suno_term, attested_count,"
            " source_categories, dict_version, origin) VALUES (?,?,?,?,?,?,?)",
            (cid, a["primary_category"], a["suno_term"], a["attested_count"],
             json.dumps(a["source_categories"]), dict_version, a["origin"]))
        rows = [(cid, "suno_native", a["suno_term"], "canonical", "high", None)]
        au = authored.get(norm)
        if au:
            conf = au.get("confidence", "high")
            for f in AUTHORED_FIELDS:
                v = au.get(f)
                if v is None or v == "" or v == []:
                    continue
                text = json.dumps(v, ensure_ascii=False) if f == "tags" else str(v).strip()
                rows.append((cid, f, text, "authored_llm", conf, au.get("notes")))
        cur.executemany(
            "INSERT INTO expr_expressions (concept_id, register, text, method, confidence, notes)"
            " VALUES (?,?,?,?,?,?)", rows)
        n_expr += len(rows)

    # 인바운드 별칭 시드
    n_alias = 0
    if ALIAS_SEED.exists():
        seed = json.loads(ALIAS_SEED.read_text())
        term_to_cid = {slugify(a["suno_term"]): concept_id_of(a) for a in atoms.values()}
        for al in seed.get("aliases", []):
            target = al.get("target_suno_term")
            cid = term_to_cid.get(slugify(target)) if target else None
            if target and cid is None:
                print(f"  [warn] 별칭 타깃 미존재: {al['alias_text']} → {target}", file=sys.stderr)
            cur.execute(
                "INSERT OR IGNORE INTO expr_inbound_aliases"
                " (alias_text, alias_lang, kind, target_concept_id, replacement_note, source)"
                " VALUES (?,?,?,?,?,?)",
                (al["alias_text"], al["alias_lang"], al["kind"], cid,
                 al.get("replacement_note"), al.get("source")))
            n_alias += cur.rowcount

    # FTS: 전 레지스터 + 별칭(역방향 검색용, register='alias')
    cur.execute("""INSERT INTO expr_fts (concept_id, register, text)
                   SELECT concept_id, register, text FROM expr_expressions""")
    cur.execute("""INSERT INTO expr_fts (concept_id, register, text)
                   SELECT COALESCE(target_concept_id,''), 'alias', alias_text
                   FROM expr_inbound_aliases""")
    conn.commit()
    n_concepts = cur.execute("SELECT COUNT(*) FROM expr_concepts").fetchone()[0]
    print(f"적재 완료: 개념 {n_concepts} / 표현 {n_expr} / 별칭 {n_alias} / dict v{dict_version}")
    conn.close()


def cmd_coverage():
    atoms, _ = extract_atoms()
    authored = load_authored()
    missing = [a["suno_term"] for n, a in sorted(atoms.items()) if n not in authored]
    partial = []
    for n, a in sorted(atoms.items()):
        au = authored.get(n)
        if au:
            gaps = [f for f in AUTHORED_FIELDS if not au.get(f)]
            if gaps:
                partial.append((a["suno_term"], gaps))
    print(f"원자 {len(atoms)} / 저작 {len(authored)} / 미저작 {len(missing)} / 부분 {len(partial)}")
    if missing:
        print("미저작:", ", ".join(missing[:40]) + (" ..." if len(missing) > 40 else ""))
    for term, gaps in partial[:20]:
        print(f"  부분: {term} — 누락 {gaps}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--export-worklist", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    args = ap.parse_args()
    if args.export_worklist:
        cmd_export_worklist()
    elif args.build:
        cmd_build()
    elif args.coverage:
        cmd_coverage()
    else:
        ap.print_help()
