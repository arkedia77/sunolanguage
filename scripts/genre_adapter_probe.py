#!/usr/bin/env python3
"""장르 어댑터 실측 프로브 — encore 정규화표(design_intent)를 sunolang 관측층에 대본다.

배경:
  encore `genre_design_normalize_v0`(08-03)는 16그룹 정규식으로 5,754클립을 묶었으나
  라벨 출처가 **design_intent(SP 지정값=요청)**다. encore 스스로 캘리브레이션 경고를 냈고,
  「'같은 장르 안'을 라벨 문자열로 정의하면 깨진다 → 관측지표로 묶으라」고 지적했다.

sunolang이 가진 것:
  reanalysis_v2/lexical_index.sqlite에 같은 곡의 **요청 SP(leomusic_sp_full)**와
  **관측 SP(suno_sp_full = Suno 재분석 원문)**가 함께 있다. 즉 요청↔관측 대조쌍.
  Suno가 스스로 쓴 장르 문자열(slot='genre')은 '관측 라벨'이다.

측정 3종:
  M1 커버리지  — encore 16규칙을 관측 라벨에 그대로 적용했을 때 unmapped 율
  M2 드리프트  — 같은 곡의 요청그룹 vs 관측그룹 일치율 (encore 표의 프록시 오차 상한)
  M3 문법분해  — Suno 관측 라벨의 슬롯 구조(코어/영향/발성/그루브) 실측 빈도

산출: data/exchange/genre_adapter_probe_result.json
"""
import json
import re
import sqlite3
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
ENCORE = ROOT / "data" / "exchange" / "encore_20260803" / "genre_design_normalize_v0.json"
OUT = ROOT / "data" / "exchange" / "genre_adapter_probe_result.json"

# ── Suno 관측 라벨 문법 슬롯 (실측 기반 — 상위 40 라벨 육안 확인 후 작성) ────────
SLOT_PATTERNS = {
    # 발성 기술자: 성역·성별이 '장르 문자열 안'에 들어와 있는 구간
    "voice": re.compile(
        r"\b(?:featuring|with)\s+(?:a\s+)?"
        r"(?:(?:soft|powerful|breathy|clear|warm|smooth|husky|delicate)\s+)*"
        r"(?:baritone|tenor|soprano|alto|mezzo|male|female|androgynous|duet)"
        r"[^,.]*?\bvocal(?:ist|s)?\b", re.I),
    # 영향/융합 구간
    "influence": re.compile(
        r"\b(?:with\s+(?:strong\s+|subtle\s+|light\s+)?"
        r"(?:elements?\s+of|influences?\s+(?:of|from)?|hints?\s+of|touches?\s+of)"
        r"|with\s+[\w\- ]+?\s+influences?"
        r"|\band\s+[\w\- ]+?\s+fusion)\b", re.I),
    # 그루브/템포 기술자
    "groove": re.compile(
        r"\bwith\s+a\s+[\w\- ]*?(?:groove|shuffle|swing|pulse|bounce|beat|feel|tempo)\b", re.I),
    # 용도/기능 기술자 (educational, instructional 등)
    "function": re.compile(
        r"\b(?:educational|instructional|meditative|devotional|ceremonial|commercial|jingle)\b", re.I),
}

SCENE = re.compile(r"\bK-\s?(?=Pop|Indie|Rock|Hip|Ballad|R&B|Trot|Folk)", re.I)


def load_encore_rules():
    d = json.loads(ENCORE.read_text())
    return [(r["group"], re.compile(r["pattern"], re.I)) for r in d["rules"]], d


def classify(label, rules):
    """encore 규칙을 선언 순서대로 적용 — 첫 일치 그룹 (encore 원본 의미론 유지)."""
    if not label or not label.strip():
        return "_no_label"
    for group, pat in rules:
        if pat.search(label):
            return group
    return "unmapped"


def strip_slots(label):
    """관측 라벨에서 비(非)장르 슬롯을 벗겨 '장르 코어'만 남긴다."""
    found = {}
    core = label
    for name, pat in SLOT_PATTERNS.items():
        m = pat.search(core)
        if m:
            found[name] = m.group(0).strip()
            core = core[:m.start()] + " " + core[m.end():]
    core = re.sub(r"\s*[,;]\s*$", "", core)
    core = re.sub(r"\s+", " ", core).strip(" ,.;-")
    return core, found


def main():
    rules, encore_meta = load_encore_rules()
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 관측 라벨: Suno 재분석 SP가 스스로 쓴 장르 문장의 entity
    cur.execute("SELECT song_id, entity, genre FROM entries "
                "WHERE slot='genre' AND source='sp_entity' AND entity IS NOT NULL")
    rows = cur.fetchall()

    observed = {}      # song_id -> [관측 라벨...]
    requested = {}     # song_id -> 요청 라벨 (entries.genre = design_intent)
    for sid, ent, req in rows:
        observed.setdefault(sid, []).append(ent.strip())
        if req and req.strip():
            requested[sid] = req.strip()

    # 요청 SP 원문 보유 여부 (대조쌍 성립 곡)
    cur.execute("SELECT DISTINCT song_id FROM entries WHERE source='leomusic_sp_full'")
    has_req_sp = {r[0] for r in cur.fetchall()}

    # ── M1: 커버리지 (관측 라벨 기준) ───────────────────────────────
    obs_groups = collections.Counter()
    unmapped_labels = collections.Counter()
    for sid, labs in observed.items():
        g = classify(labs[0], rules)
        obs_groups[g] += 1
        if g == "unmapped":
            unmapped_labels[labs[0]] += 1

    n_obs = sum(obs_groups.values())
    m1 = {
        "n_songs_observed_label": n_obs,
        "group_counts": dict(obs_groups.most_common()),
        "unmapped_pct": round(100.0 * obs_groups["unmapped"] / n_obs, 1),
        "coverage_pct": round(100.0 * (n_obs - obs_groups["unmapped"] - obs_groups["_no_label"]) / n_obs, 1),
        "encore_coverage_pct_on_design_intent": encore_meta["coverage_pct"],
        "unmapped_examples": dict(unmapped_labels.most_common(15)),
    }

    # ── M2: 요청 → 관측 드리프트 ────────────────────────────────────
    pairs, drift = [], collections.Counter()
    for sid, labs in observed.items():
        if sid not in requested:
            continue
        rg = classify(requested[sid], rules)
        og = classify(labs[0], rules)
        pairs.append({"song_id": sid, "requested": requested[sid], "observed": labs[0],
                      "requested_group": rg, "observed_group": og, "agree": rg == og})
        drift[(rg, og)] += 1

    n_pair = len(pairs)
    n_agree = sum(1 for p in pairs if p["agree"])
    # 요청그룹별 유지율
    per_req = collections.defaultdict(lambda: [0, 0])
    for p in pairs:
        per_req[p["requested_group"]][1] += 1
        if p["agree"]:
            per_req[p["requested_group"]][0] += 1

    m2 = {
        "n_pairs": n_pair,
        "n_with_requested_sp_text": len(has_req_sp & set(observed)),
        "agreement_pct": round(100.0 * n_agree / n_pair, 1) if n_pair else None,
        "top_drift_transitions": [
            {"from": k[0], "to": k[1], "n": v}
            for k, v in drift.most_common(20) if k[0] != k[1]
        ],
        "retention_by_requested_group": {
            k: {"kept": v[0], "n": v[1], "pct": round(100.0 * v[0] / v[1], 1)}
            for k, v in sorted(per_req.items(), key=lambda x: -x[1][1])
        },
    }

    # ── M3: 관측 라벨 문법 분해 ─────────────────────────────────────
    slot_freq = collections.Counter()
    core_freq = collections.Counter()
    scene_n = 0
    core_examples = []
    for sid, labs in observed.items():
        lab = labs[0]
        core, found = strip_slots(lab)
        for k in found:
            slot_freq[k] += 1
        if SCENE.search(lab):
            scene_n += 1
        core_freq[core.lower()] += 1
        if found and len(core_examples) < 12:
            core_examples.append({"song_id": sid, "raw": lab, "core": core, "slots": found})

    # 슬롯을 벗긴 뒤 encore 그룹 재분류 — 코어만으로 분류가 달라지는가
    core_groups = collections.Counter()
    changed = []
    for sid, labs in observed.items():
        lab = labs[0]
        core, _ = strip_slots(lab)
        g_raw, g_core = classify(lab, rules), classify(core, rules)
        core_groups[g_core] += 1
        if g_raw != g_core:
            changed.append({"song_id": sid, "raw": lab, "core": core,
                            "group_raw": g_raw, "group_core": g_core})

    m3 = {
        "n_labels": n_obs,
        "slot_hit_counts": dict(slot_freq.most_common()),
        "slot_hit_pct": {k: round(100.0 * v / n_obs, 1) for k, v in slot_freq.most_common()},
        "k_scene_prefix_n": scene_n,
        "k_scene_prefix_pct": round(100.0 * scene_n / n_obs, 1),
        "distinct_raw_labels": len({l[0] for l in observed.values()}),
        "distinct_cores": len(core_freq),
        "top_cores": dict(core_freq.most_common(25)),
        "decomposition_examples": core_examples,
        "group_changed_after_strip": len(changed),
        "group_change_examples": changed[:10],
    }

    result = {
        "as_of": "2026-08-04",
        "owner": "sunolanguage",
        "purpose": "encore genre_design_normalize_v0를 sunolang 관측층(Suno 재분석 SP)에 대조",
        "encore_input_ref": {"version": encore_meta["version"],
                             "label_source": encore_meta["label_source"],
                             "coverage_pct": encore_meta["coverage_pct"],
                             "n_rules": len(rules)},
        "sunolang_source": {"db": str(DB.relative_to(ROOT)),
                            "label_source": "suno_sp_full 재분석 원문의 genre 문장 (관측)",
                            "requested_label_source": "entries.genre (design_intent)"},
        "M1_coverage_on_observed": m1,
        "M2_requested_to_observed_drift": m2,
        "M3_observed_label_grammar": m3,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))

    print(f"[M1] 관측 라벨 {n_obs}곡 · encore 규칙 커버리지 {m1['coverage_pct']}% "
          f"(encore 자체 design_intent 커버리지 {m1['encore_coverage_pct_on_design_intent']}%)")
    print(f"[M2] 요청↔관측 대조쌍 {n_pair}건 · 그룹 일치 {m2['agreement_pct']}%")
    for t in m2["top_drift_transitions"][:8]:
        print(f"       {t['from']:>14} → {t['to']:<14} {t['n']}")
    print(f"[M3] 라벨 {n_obs} · 고유 원문 {m3['distinct_raw_labels']} → 슬롯제거 코어 {m3['distinct_cores']}")
    for k, v in m3["slot_hit_pct"].items():
        print(f"       slot {k:>10}: {slot_freq[k]:>3}건 ({v}%)")
    print(f"       K-scene 접두: {scene_n}건 ({m3['k_scene_prefix_pct']}%)")
    print(f"       슬롯 제거 후 그룹 변동: {m3['group_changed_after_strip']}건")
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
