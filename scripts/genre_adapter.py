#!/usr/bin/env python3
"""장르 어댑터 v0 — 코어(sunolang 관측 좌표) + 어댑터(encore v0 호환).

R-P4(양자택일 금지)에 따라 **둘 다 보유**한다.
  · 코어    = 라벨 하나를 '다중 장르 집합 + 부속 슬롯'으로 여는 좌표계 (sunolang 관측층 기준)
  · 어댑터  = encore v0 16그룹으로의 투영. 원본 재현(v0) 과 다중배정(multi) 두 모드.

실측 근거(전부 재현 가능, 산출 JSON 동봉):
  genre_adapter_probe   M1 관측 라벨에 encore 규칙 커버리지 100%(unmapped 0)
                        M3 관측 라벨 454 → 고유 원문 226 → 슬롯제거 코어 171
  genre_adapter_split   요청↔관측 그룹 완전일치 27.2%, 순위충돌 보정 40.4%
                        V1 요청라벨 출처검증 97.6% design_intent 확인
  genre_collapse_test   관측 엔트로피 2.601 < 요청 3.698 (수축), K접두 16.3%→94.6%
  genre_axis_test       ★축분리 가설 기각. 살아남은 것 = 복합성 격차
                        설계 복합 30.9%(1.3개/라벨) vs 관측 복합 85.0%(2.23개/라벨)

설계 원칙:
  ⑴ encore v0를 고치지 않는다 — 먼저 **바이트 단위로 재현**하고(계약검증), 그 위에 얹는다.
  ⑵ 단일배정은 관측층에서 정보를 버리므로 다중배정을 기본 제공. 단 v0 모드는 그대로 남긴다.
  ⑶ 슬롯 추출(voice/influence/groove/function)은 '추출된 스팬'일 뿐이며,
     그것이 곧 '별도 축'이라는 주장은 axis_test에서 기각됐다. 축이라 부르지 않는다.

사용:
  python3 scripts/genre_adapter.py --verify          계약검증(encore v0 재현)
  python3 scripts/genre_adapter.py --demo            분해 예시
  from genre_adapter import GenreAdapter
"""
import json
import re
import sys
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENCORE_V0 = ROOT / "data" / "exchange" / "encore_20260803" / "genre_design_normalize_v0.json"

# 부속 슬롯 — 관측 라벨에서 실제로 추출되는 스팬. 축 유형론 주장 아님(axis_test 기각분).
SLOTS = {
    "voice": re.compile(
        r"\b(?:featuring|with)\s+(?:a\s+)?"
        r"(?:(?:soft|powerful|breathy|clear|warm|smooth|husky|delicate)\s+)*"
        r"(?:baritone|tenor|soprano|alto|mezzo|male|female|androgynous|duet)"
        r"[^,.]*?\bvocal(?:ist|s)?\b", re.I),
    "influence": re.compile(
        r"\b(?:with\s+(?:strong\s+|subtle\s+|light\s+)?"
        r"(?:elements?\s+of|influences?\s+(?:of|from)?|hints?\s+of|touches?\s+of)"
        r"|with\s+[\w\- ]+?\s+influences?"
        r"|\band\s+[\w\- ]+?\s+fusion)\b", re.I),
    "groove": re.compile(
        r"\bwith\s+a\s+[\w\- ]*?(?:groove|shuffle|swing|pulse|bounce|beat|feel|tempo)\b", re.I),
    "function": re.compile(
        r"\b(?:educational|instructional|meditative|devotional|ceremonial|commercial|jingle)\b", re.I),
}
SCENE = re.compile(r"\b([KJCT])[-\s]?(?=Pop|Indie|Rock|Hip|Ballad|R&B|Trot|Folk|Rap)", re.I)


class GenreAdapter:
    def __init__(self, encore_path=ENCORE_V0):
        self.meta = json.loads(Path(encore_path).read_text())
        self.rules = [(r["group"], re.compile(r["pattern"], re.I)) for r in self.meta["rules"]]
        self.version = self.meta["version"]

    # ── 어댑터 A: encore v0 원본 재현 (선언순서 첫일치 단일배정) ──────────────
    def encore_v0(self, label):
        if not label or not label.strip():
            return "_no_label"
        for g, p in self.rules:
            if p.search(label):
                return g
        return "unmapped"

    # ── 어댑터 B: 다중배정 (스팬 비겹침 — 포섭 적중 제거) ─────────────────────
    def _spans(self, label):
        out = {}
        for g, p in self.rules:
            m = p.search(label)
            if m:
                out[g] = (m.start(), m.end())
        return out

    def encore_multi(self, label):
        """한 라벨이 실제로 담은 장르 그룹 집합. 'K-Pop'이 kpop·pop_general에
        동시 적중하는 포섭은 넓은 스팬 우선으로 흡수한다."""
        if not label or not label.strip():
            return []
        sp = self._spans(label)
        keep, taken = [], []
        for g, (a, b) in sorted(sp.items(), key=lambda x: (x[1][0], -(x[1][1] - x[1][0]))):
            if all(b <= c or a >= d for c, d in taken):
                keep.append(g)
                taken.append((a, b))
        return keep

    # ── 코어: 좌표 분해 ───────────────────────────────────────────────────────
    def to_axes(self, label, layer="unknown"):
        raw = (label or "").strip()
        core = raw
        slots = {}
        for name, pat in SLOTS.items():
            m = pat.search(core)
            if m:
                slots[name] = m.group(0).strip()
                core = core[:m.start()] + " " + core[m.end():]
        core = re.sub(r"\s+", " ", core).strip(" ,.;-")
        sc = SCENE.search(raw)
        return {
            "raw": raw,
            "layer": layer,                      # requested(design_intent) | observed(suno) | unknown
            "scene": (sc.group(1).upper() if sc else None),
            "core_text": core,
            "genres": self.encore_multi(core) or self.encore_multi(raw),
            "encore_v0_group": self.encore_v0(raw),
            "slots": slots,
        }

    # ── 같은 층 안에서만 비교 가능 (교차층 비교는 드리프트 측정용) ─────────────
    def same_stratum(self, a, b, level="genres"):
        """'같은 장르 안' 판정. level=genres → 다중집합 동일, level=primary → 최상위 1개."""
        A, B = self.to_axes(a), self.to_axes(b)
        if A["layer"] != B["layer"] and "unknown" not in (A["layer"], B["layer"]):
            raise ValueError("층이 다른 라벨은 같은 지층으로 묶지 않는다 (요청 vs 관측)")
        if level == "primary":
            return bool(A["genres"]) and bool(B["genres"]) and A["genres"][0] == B["genres"][0]
        return set(A["genres"]) == set(B["genres"]) and bool(A["genres"])


# ── 계약검증: 내 재구현이 encore v0 배정을 그대로 재현하는가 ───────────────────
def verify(ad):
    """encore가 보낸 labels_by_group을 정답지로 삼아 재현율을 잰다.
    여기서 어긋나면 내가 encore 의미론을 오독한 것 — 개선 제안 이전에 이게 먼저다."""
    ok = bad = 0
    mism = []
    for truth_group, labs in ad.meta["labels_by_group"].items():
        if truth_group in ("_no_label",):
            continue
        for lab, n in labs.items():
            mine = ad.encore_v0(lab)
            if truth_group == "unmapped":
                good = (mine == "unmapped")
            else:
                good = (mine == truth_group)
            if good:
                ok += n
            else:
                bad += n
                if len(mism) < 15:
                    mism.append({"label": lab, "encore_says": truth_group, "mine": mine, "n": n})
    tot = ok + bad
    return {"reproduced": ok, "mismatched": bad, "total_clips": tot,
            "fidelity_pct": round(100.0 * ok / tot, 2) if tot else None,
            "mismatch_examples": mism}


def main():
    ad = GenreAdapter()
    if "--verify" in sys.argv:
        v = verify(ad)
        print(f"[계약검증] encore v0 재현율 {v['fidelity_pct']}%  "
              f"({v['reproduced']}/{v['total_clips']} 클립, 불일치 {v['mismatched']})")
        for m in v["mismatch_examples"]:
            print(f"   ✗ {m['label'][:52]:<52} encore={m['encore_says']:<14} mine={m['mine']} (n={m['n']})")
        out = ROOT / "data" / "exchange" / "genre_adapter_verify.json"
        out.write_text(json.dumps(v, ensure_ascii=False, indent=1))
        print(f"→ {out.relative_to(ROOT)}")
        return

    if "--demo" in sys.argv:
        samples = [
            ("K-Pop ballad featuring a baritone male vocal", "observed"),
            ("K-Pop City Pop with elements of Funk and Jazz Fusion", "observed"),
            ("K-Hip Hop with a boom bap influence", "observed"),
            ("Lo-fi Indie Pop / Dream Pop", "requested"),
            ("trot", "requested"),
            ("K-Pop educational pop track", "observed"),
        ]
        for lab, layer in samples:
            a = ad.to_axes(lab, layer)
            print(f"\n[{layer}] {lab}")
            print(f"   scene={a['scene']}  encore_v0={a['encore_v0_group']}")
            print(f"   genres(다중)={a['genres']}")
            print(f"   core='{a['core_text']}'")
            if a["slots"]:
                for k, v in a["slots"].items():
                    print(f"   slot.{k}: {v}")
        return

    print(__doc__)


if __name__ == "__main__":
    main()
