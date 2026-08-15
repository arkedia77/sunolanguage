#!/usr/bin/env python3
"""코퍼스 커넥터 — 코퍼스 외부 인터페이스 3포트 단일 진입점.

설계 정본: docs/corpus_connector_design.md
  OUT     표현 레이어 → 버전드 crosswalk publish (status: live)
  IN      외부 레퍼런스 → reference_matcher 매칭 (status: blocked — 기계귀 게이트)
  CONSUME encore 경로C handoff serializer (status: blocked — fresh run 대기)

공용: data/connector/manifest.json (포트 상태·버전 선언) + sunolang.db:connector_runs (실행 로그).

사용:
  python3 scripts/corpus_connector.py status                 # 매니페스트 포트 현황
  python3 scripts/corpus_connector.py out publish [--dry-run] [--major]
  python3 scripts/corpus_connector.py in match --help        # 스캐폴드(게이트)
  python3 scripts/corpus_connector.py consume handoff --emit-schema
"""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "sunolang.db"
DICT_PATH = ROOT / "rag" / "suno_dictionary_v3.json"
CONNECTOR_DIR = ROOT / "data" / "connector"
MANIFEST_PATH = CONNECTOR_DIR / "manifest.json"
SUBSCRIBERS_PATH = CONNECTOR_DIR / "subscribers.json"
OUT_DIR = CONNECTOR_DIR / "out"
CONSUME_DIR = CONNECTOR_DIR / "consume"
EXPORTER = ROOT / "scripts" / "expression_search.py"

# 구독자 기본 선언 — 활용포인트 + 파생(derivations). 재발행 시 재사용.
# 항4(fableself 07-17): 번들 파생 = **무손실만**(sort/filter/subset). 의미 변환은 소비 어댑터 몫.
#   파생 로직 소유 = 선언한 팀(구독 레지스트리), 실행 = 커넥터(기계 적용).
LOSSLESS_KINDS = {"sort", "filter", "subset"}
SUBSCRIBER_DEFAULTS = {
    "leomusic": {"activation": "SP 작성 시 suno_native 정본 + plain_ko로 의도 확인. dead-zone 별칭 가드로 미반응어 차단.",
                 "derivations": []},
    "leomusic2": {"activation": "SP 재료 검색: plain_ko→concept→suno_native attested. llm_prompt 레지스터로 타 AI 교차.",
                  "derivations": []},
    "leomusic3": {"activation": "tags 레지스터(파셋) + taxonomy 정렬 파생을 기계귀 임베딩 라벨공간 정렬에 활용.",
                  # leomusic3가 선언한 무손실 파생(정렬 스펙) — 커넥터는 기계 적용만
                  "derivations": [{"name": "taxonomy_sorted", "kind": "sort",
                                   "key": ["category", "concept_id"],
                                   "fields": ["concept_id", "category", "suno_term", "reg:tags"]}]},
    "leomusic-trot": {"activation": "장르 특화 어휘 대조. W008/W012 '로컬0≠전코퍼스' 회피목록 검증에 attested_count 병용.",
                      "derivations": []},
    # encore=레오뮤직 소속 A&R·발주 주체(LEO 08-15). 발주 前 '이 요구가 Suno에서 실제로 나오는 말인가' 판정용.
    "encore": {"activation": "발주 前 표현 가능성 확인: plain_ko→concept→suno_native attested로 요구를 Suno 네이티브 어휘에 접지. "
                             "dead_zone/blocked 별칭은 발주서에서 제외(미반응어 가드). "
                             "타 엔진 발주 시 llm_prompt 레지스터를 교차 참조 — ★단 attested는 Suno 관측이며 타 엔진 uptake는 미검증(Lyria 절대조성 사례: self-report≠render).",
               "derivations": []},
}


def _project(concept, fields):
    """개념에서 선언된 필드만 투영. 'reg:X'=레지스터 X 값. 무손실(필드 선택은 서브셋)."""
    if not fields:
        return concept
    out = {}
    for f in fields:
        if f.startswith("reg:"):
            out[f[4:]] = (concept.get("registers") or {}).get(f[4:])
        else:
            out[f] = concept.get(f)
    return out


def apply_derivation(concepts, deriv):
    """무손실 파생만 실행. 의미 변환 kind는 거부(None) — 항4 경계."""
    kind = deriv.get("kind")
    if kind not in LOSSLESS_KINDS:
        return None
    fields = deriv.get("fields")
    if kind == "sort":
        rows = sorted(concepts, key=lambda c: tuple(str(c.get(k, "")) for k in deriv["key"]))
    elif kind == "filter":
        cats = set(deriv.get("categories", []))
        rows = [c for c in concepts if not cats or c.get("category") in cats]
    else:  # subset — 필드 투영만
        rows = list(concepts)
    return [_project(c, fields) for c in rows]


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def corpus_snapshot(conn) -> dict:
    """코어(사전+DB) 관측 상태를 고정. 버전 바인딩의 기준 — 설계 §4."""
    d = json.loads(DICT_PATH.read_text())
    dict_version = str(d.get("version", "?"))
    tracks = int(d.get("corpus", {}).get("tracks_count", 0))
    n_concepts = conn.execute("SELECT COUNT(*) FROM expr_concepts").fetchone()[0]
    created = str(d.get("created_at", "")).replace("-", "")[:8] or "unknown"
    # v0.2(fableself 경미②): 스냅샷 객체엔 스냅샷 고유 시각(dict_created)만 — 매니페스트 생성시각은 최상위 manifest_generated_at로 분리
    return {
        "snapshot_id": f"cs-{dict_version}-{tracks}-{created}",
        "dict_version": dict_version,
        "corpus_tracks": tracks,
        "expr_concepts": n_concepts,
        "dict_created_at": str(d.get("created_at", "")),
    }


def ensure_runs_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS connector_runs (
      id INTEGER PRIMARY KEY,
      port TEXT NOT NULL,
      snapshot_id TEXT NOT NULL,
      interface_version TEXT NOT NULL,
      artifact_sha256 TEXT,
      status TEXT NOT NULL,
      note TEXT,
      started_at TEXT DEFAULT (datetime('now','localtime')),
      ended_at TEXT
    )""")


def log_run(conn, port, snapshot_id, iv, sha, status, note):
    ensure_runs_table(conn)
    conn.execute(
        "INSERT INTO connector_runs (port, snapshot_id, interface_version,"
        " artifact_sha256, status, note, ended_at) VALUES (?,?,?,?,?,?,datetime('now','localtime'))",
        (port, snapshot_id, iv, sha, status, note))
    conn.commit()


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    # 최초 골격 — 설계 §3 (blocked 포트는 blocker 명기)
    # status enum: live | blocked | deprecated | scaffold
    # blocker(항1 fableself 기준): gate_owner·release_condition·on_release{transition,version_bump}
    return {
        "_provenance": "코퍼스 커넥터 매니페스트 — 정본: docs/corpus_connector_design.md",
        "status_enum": ["live", "blocked", "deprecated", "scaffold"],
        "corpus_snapshot": {},
        "interface_version": "0.0",
        "ports": [
            {"port": "out", "direction": "outbound", "status": "scaffold",
             "payload_schema": "data/connector/schemas/out_crosswalk.schema.json",
             "artifact": None, "artifact_sha256": None,
             "consumers": list(SUBSCRIBER_DEFAULTS), "blocker": None},
            {"port": "in", "direction": "inbound", "status": "blocked",
             "producers": ["external_reference_songs"], "artifact": None,
             "blocker": {
                 "gate_owner": "leomusic3",
                 "reason": "v1 F1~F5 구조피처는 기계귀(CLAP) 도메인 — 텍스트층 단독 도달 불가",
                 "release_condition": "leomusic3 기계귀 협의 통과 → matching_feature_redesign_v1.md F1~F5 배선",
                 "on_release": {"transition": "blocked→live", "version_bump": "minor (신 매칭채널=additive)"},
                 "ownership_on_release": "피처 정의·개정=leomusic3 / 소비·배선=커넥터"}},
            {"port": "consume", "direction": "outbound", "status": "blocked",
             "consumers": ["encore"], "artifact": None,
             "blocker": {
                 "gate_owner": "encore",
                 "reason": "경로C 소비 실주행은 encore 신호 필요(회신스키마 발신완료 07-16)",
                 "release_condition": "encore fresh run 착수 신호",
                 "on_release": {"transition": "blocked→live", "version_bump": "minor (신 소비계약=additive)"},
                 "ownership_on_release": "소비 스키마·요청=encore / serializer 실행=커넥터"}},
        ],
        "runs_log": "sunolang.db:connector_runs",
    }


def save_manifest(m: dict):
    CONNECTOR_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2))


def get_port(m, port):
    for p in m["ports"]:
        if p["port"] == port:
            return p
    raise KeyError(port)


def bump_version(prev_iv: str, snapshot, m_prev, n_concepts, major: bool) -> str:
    """major=True면 major+1.0. 아니면 내용(스냅샷/개념수) 변화 시 minor+1 — 설계 §4."""
    try:
        maj, minr = (int(x) for x in prev_iv.split("."))
    except ValueError:
        maj, minr = 0, 0
    if major:
        return f"{maj + 1}.0"
    prev_snap = (m_prev.get("corpus_snapshot") or {}).get("snapshot_id")
    if prev_snap == snapshot["snapshot_id"] and prev_iv not in ("0.0",):
        return prev_iv  # 스냅샷 동일 → 재발행이라도 버전 유지
    return f"{maj}.{minr + 1}"


def build_crosswalk() -> dict:
    """정본 exporter(expression_search --export) 재사용 — SQL 중복 금지(G-K4)."""
    with tempfile.NamedTemporaryFile("r", suffix=".json", delete=False) as tf:
        tmp = Path(tf.name)
    subprocess.run([sys.executable, str(EXPORTER), "--export", str(tmp)],
                   check=True, capture_output=True, text=True)
    data = json.loads(tmp.read_text())
    tmp.unlink(missing_ok=True)
    return data


def detect_breaking(crosswalk) -> tuple:
    """항2(fableself): 이전 발행분 대비 **삭제·별칭 재타깃** 감지 = 소비자 재검증 트리거.
    additive(신규 개념·별칭)는 breaking 아님. 레지스터 텍스트 편집은 concept 해소 불변이라 제외(정직 명기)."""
    latest = OUT_DIR / "crosswalk_latest.json"
    if not latest.exists():
        return False, {}
    prev = json.loads(latest.read_text())
    prev_ids = {c["concept_id"] for c in prev.get("concepts", [])}
    cur_ids = {c["concept_id"] for c in crosswalk.get("concepts", [])}
    removed = sorted(prev_ids - cur_ids)
    prev_al = {(a["alias_text"], a["kind"]): a.get("target_concept_id") for a in prev.get("inbound_aliases", [])}
    cur_al = {(a["alias_text"], a["kind"]): a.get("target_concept_id") for a in crosswalk.get("inbound_aliases", [])}
    removed_al = sorted(f"{t}/{k}" for (t, k) in (set(prev_al) - set(cur_al)))
    retargeted = sorted(f"{t}/{k}" for (t, k) in (set(prev_al) & set(cur_al)) if prev_al[(t, k)] != cur_al[(t, k)])
    detail = {k: v for k, v in {"removed_concepts": removed, "removed_aliases": removed_al,
                                "retargeted_aliases": retargeted}.items() if v}
    return bool(detail), detail


def cmd_status():
    m = load_manifest()
    snap = m.get("corpus_snapshot") or {}
    print(f"코퍼스 커넥터 — interface v{m.get('interface_version')} / "
          f"snapshot {snap.get('snapshot_id', '(미발행)')}")
    print(f"  코어: dict v{snap.get('dict_version', '?')} · "
          f"{snap.get('corpus_tracks', '?')}트랙 · {snap.get('expr_concepts', '?')}개념")
    print("  포트:")
    for p in m["ports"]:
        line = f"    [{p['status']:>8}] {p['port']:<8} {p['direction']}"
        if p.get("artifact"):
            line += f"  → {p['artifact']}"
        print(line)
        b = p.get("blocker")
        if isinstance(b, dict):
            print(f"               ⛔ [{b.get('gate_owner')}] {b.get('release_condition')}")
            print(f"                  해제 시: {b['on_release']['transition']} / {b['on_release']['version_bump']}")
        elif b:
            print(f"               ⛔ {b}")
    conn = sqlite3.connect(DB_PATH)
    ensure_runs_table(conn)
    rows = conn.execute("SELECT port, interface_version, status, note, ended_at"
                        " FROM connector_runs ORDER BY id DESC LIMIT 5").fetchall()
    if rows:
        print("  최근 실행:")
        for port, iv, st, note, ts in rows:
            print(f"    {ts}  {port}/{st}  v{iv}  {note or ''}")
    conn.close()


def cmd_out_publish(dry_run: bool, major: bool):
    conn = sqlite3.connect(DB_PATH)
    snapshot = corpus_snapshot(conn)
    m = load_manifest()
    iv = bump_version(m.get("interface_version", "0.0"), snapshot, m, snapshot["expr_concepts"], major)

    crosswalk = build_crosswalk()
    n_concepts = len(crosswalk.get("concepts", []))
    n_aliases = len(crosswalk.get("inbound_aliases", []))
    breaking, breaking_detail = detect_breaking(crosswalk)  # 항2 — 삭제/재타깃 감지
    # sha256 = 콘텐츠 해시(타임스탬프 제외) — 소비자 드리프트 감지가 목적이므로 벽시계 배제(설계 §4)
    sha = sha256_of(json.dumps(crosswalk, ensure_ascii=False, sort_keys=True))
    manifest_block = {
        "snapshot_id": snapshot["snapshot_id"],
        "interface_version": iv,
        "generated_at": _now_iso(),
        "source_exporter": "scripts/expression_search.py --export",
        "design": "docs/corpus_connector_design.md",
        "concepts": n_concepts, "inbound_aliases": n_aliases,
        "sha256": sha,
        "breaking_content": breaking,          # True → 소비자 재검증 트리거(minor+플래그)
        "breaking_detail": breaking_detail or None,
    }
    crosswalk = {"_manifest": manifest_block, **crosswalk}
    payload = json.dumps(crosswalk, ensure_ascii=False, indent=1)

    artifact_rel = f"data/connector/out/crosswalk_v{iv}.json"
    artifact = ROOT / artifact_rel
    brk = " ⚠BREAKING(재검증)" if breaking else ""

    if dry_run:
        print(f"[dry-run] OUT publish → v{iv}{brk} / snapshot {snapshot['snapshot_id']}")
        print(f"  개념 {n_concepts} · 별칭 {n_aliases} · sha256 {sha[:16]}…")
        if breaking:
            print(f"  breaking_detail: {breaking_detail}")
        print(f"  산출 예정: {artifact_rel} + 팀번들 {list(SUBSCRIBER_DEFAULTS)}")
        log_run(conn, "out", snapshot["snapshot_id"], iv, sha, "dry_run",
                f"{n_concepts}개념/{n_aliases}별칭{brk}")
        conn.close()
        return

    # 원자적 발행: 임시 → 정본 위치 교체 (설계 §5)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = artifact.with_suffix(".json.tmp")
    tmp.write_text(payload)
    tmp.replace(artifact)
    (OUT_DIR / "crosswalk_latest.json").write_text(payload)

    # 구독 레지스트리 로드 — 팀이 선언한 파생(derivations)은 구독자 소유(항4). 최초엔 기본 시드.
    subs = json.loads(SUBSCRIBERS_PATH.read_text()) if SUBSCRIBERS_PATH.exists() else {}

    # 팀별 번들 — 공유 crosswalk를 path+sha로 참조(313KB×4 중복 금지) + 선언 파생을 기계 적용
    bundles = []
    for team, cfg in SUBSCRIBER_DEFAULTS.items():
        derivs = subs.get(team, {}).get("derivations", cfg["derivations"])  # 소비자 선언 우선
        bundle = {
            "_for": team,
            "_manifest": {**manifest_block, "sha256": sha},
            "crosswalk_artifact": {"path": artifact_rel, "sha256": sha},
            "activation_points": cfg["activation"],
            "derivations_applied": [],
        }
        for dv in derivs:
            result = apply_derivation(crosswalk["concepts"], dv)
            if result is None:
                bundle["derivations_applied"].append({"name": dv.get("name"), "status": "rejected_nonlossless"})
                continue
            bundle[dv["name"]] = result
            bundle["derivations_applied"].append({"name": dv["name"], "kind": dv["kind"], "rows": len(result)})
        bp = OUT_DIR / f"bundle_{team}.json"
        bp.write_text(json.dumps(bundle, ensure_ascii=False, indent=1))
        bundles.append(str(bp.relative_to(ROOT)))

    # 구독 레지스트리 갱신 — 재발행 시 드리프트 팀 식별 + 선언 파생 보존
    for team, cfg in SUBSCRIBER_DEFAULTS.items():
        prev = subs.get(team, {})
        subs[team] = {"format": "bundle+crosswalk_ref",
                      "derivations": prev.get("derivations", cfg["derivations"]),  # 팀 소유 — 보존
                      "last_version": iv, "last_snapshot": snapshot["snapshot_id"],
                      "last_breaking": breaking,
                      "last_delivered_at": _now_iso(),
                      "first_seen": prev.get("first_seen", _now_iso())}
    SUBSCRIBERS_PATH.write_text(json.dumps(subs, ensure_ascii=False, indent=2))

    # 매니페스트 갱신
    m["corpus_snapshot"] = snapshot
    m["interface_version"] = iv
    m["manifest_generated_at"] = _now_iso()   # v0.2 경미② — 매니페스트 생성시각(스냅샷 시각과 분리)
    port = get_port(m, "out")
    port.update({"status": "live", "artifact": artifact_rel, "artifact_sha256": sha,
                 "breaking_content": breaking, "bundles": bundles,
                 "consumers": list(SUBSCRIBER_DEFAULTS)})
    save_manifest(m)
    log_run(conn, "out", snapshot["snapshot_id"], iv, sha, "ok",
            f"{n_concepts}개념/{n_aliases}별칭 → {len(bundles)}팀번들")
    conn.close()
    print(f"OUT publish 완료 → v{iv}{brk} / {snapshot['snapshot_id']}")
    print(f"  {artifact_rel}  (sha256 {sha[:16]}…, 개념 {n_concepts}·별칭 {n_aliases})")
    print(f"  팀번들: {', '.join(SUBSCRIBER_DEFAULTS)}  |  구독 레지스트리 갱신")


def cmd_in(args):
    """IN 포트 — 스캐폴드. v1 F1~F5 구조피처는 기계귀 게이트(설계 §6.2)."""
    conn = sqlite3.connect(DB_PATH)
    snapshot = corpus_snapshot(conn)
    m = load_manifest()
    port = get_port(m, "in")
    print("IN 포트 (레퍼런스 매칭) — status: blocked")
    print(f"  게이트: {port['blocker']}")
    print("  현 가용: v0 텍스트공간 매처(run1~15='검증전'). 90곡 일괄매칭 보류 유지.")
    print("  실행 엔트리(활성 시): scripts/corpus_ingest_runner.py(헬스) → reference_matcher.py"
          " → gap_candidates 등록 → recheck-gaps 루프.")
    print("  v1 활성 조건: leomusic3 기계귀 협의 통과 → matching_feature_redesign_v1.md F1~F5 배선.")
    log_run(conn, "in", snapshot["snapshot_id"], m.get("interface_version", "0.0"),
            None, "blocked", "기계귀 게이트 대기 — 스캐폴드 조회")
    conn.close()


def cmd_consume(args):
    """CONSUME 포트 — encore 경로C handoff serializer 스캐폴드(설계 §6.3)."""
    conn = sqlite3.connect(DB_PATH)
    snapshot = corpus_snapshot(conn)
    m = load_manifest()
    port = get_port(m, "consume")
    out_port = get_port(m, "out")   # 발행된 버전드 crosswalk 앵커 참조용
    # 경로C handoff 스키마 정본(재사용 serializer의 출력 계약) — encore 회신스키마 정합
    schema = {
        "_provenance": "encore 경로C handoff 스키마 — sunolang CONSUME 포트 출력 계약",
        "_status": "scaffold — encore fresh run 대기",
        "snapshot_id": snapshot["snapshot_id"],
        "interface_version": m.get("interface_version", "0.0"),
        "handoff": {
            "request_id": "<encore가 부여>",
            # v0.2(fableself 경미①): 계약 참조는 **버전드 경로+sha** 고정 — latest 포인터 참조 금지(breaking_content 재검증 게이트 우회 방지)
            "crosswalk_ref": {"path": out_port.get("artifact"), "sha256": out_port.get("artifact_sha256"),
                              "note": "crosswalk_latest.json은 인간 편의 심볼릭 전용 — 계약은 버전드+sha로 앵커"},
            "corpus_assets": [
                {"asset_type": "reference_asset|catalog_track|rag_external_track",
                 "asset_id": "<id>", "suno_terms": ["<attested>"]}
            ],
            "text_channel_note": "sunolang=text 어휘 번역 채널. 오디오 정밀부는 leomusic3 기계귀 위임.",
        },
    }
    if getattr(args, "emit_schema", False):
        CONSUME_DIR.mkdir(parents=True, exist_ok=True)
        p = CONSUME_DIR / "pathC_handoff.schema.json"
        p.write_text(json.dumps(schema, ensure_ascii=False, indent=2))
        print(f"경로C handoff 스키마 정본화: {p.relative_to(ROOT)}")
    else:
        print("CONSUME 포트 (encore 경로C) — status: blocked")
        print(f"  게이트: {port['blocker']}")
        print("  스키마 정본화: --emit-schema")
    log_run(conn, "consume", snapshot["snapshot_id"], m.get("interface_version", "0.0"),
            None, "blocked", "encore fresh run 대기 — 스캐폴드")
    conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    p_out = sub.add_parser("out")
    out_sub = p_out.add_subparsers(dest="out_cmd")
    pub = out_sub.add_parser("publish")
    pub.add_argument("--dry-run", action="store_true")
    pub.add_argument("--major", action="store_true", help="스키마 하위호환 깨짐 → major 증분")
    p_in = sub.add_parser("in")
    in_sub = p_in.add_subparsers(dest="in_cmd")
    in_sub.add_parser("match")
    p_con = sub.add_parser("consume")
    con_sub = p_con.add_subparsers(dest="con_cmd")
    hand = con_sub.add_parser("handoff")
    hand.add_argument("--emit-schema", action="store_true")

    args = ap.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "out" and args.out_cmd == "publish":
        cmd_out_publish(args.dry_run, args.major)
    elif args.cmd == "in":
        cmd_in(args)
    elif args.cmd == "consume" and args.con_cmd == "handoff":
        cmd_consume(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
