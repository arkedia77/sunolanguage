#!/usr/bin/env python3
"""input_samples_registry_v1.py — 입력 표본 대장 (재현기).

★왜 별도 대장인가:
  merged_4values.json 은 **출력층(suno_reanalysis) 관측 코퍼스**다. 추출·색인 전 경로가
  suno_reanalysis 만 읽는다(parse_slot_entities_v3 · bracket_presets · chunk_builder).
  입력층은 우리가 써넣은 문자열이지 Suno 관측이 아니므로 거기 섞으면 곡수 라벨이 거짓말을 한다.
  ⇒ 짝이 없는 수령분은 여기서 세고, 재분석이 오면 같은 song_id 로 merged 로 승격한다.

★수치는 파일에서 매번 다시 잰다 — 상수로 박지 않는다(08-16 corpus_health_check 교훈:
  소스에 박은 기준선은 필연적으로 늙고, 라벨이 거짓말을 한다).

사용: python3 scripts/input_samples_registry_v1.py [--write]
"""
import json, sys, glob, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "input_samples"
MERGED = ROOT / "data" / "reanalysis_v2" / "merged_4values.json"
OUT = DIR / "REGISTRY.json"

def has_out(r):
    sr = r.get("suno_reanalysis")
    return bool(sr) if not isinstance(sr, list) else len(sr) > 0

def main():
    merged = json.load(open(MERGED))
    merged_ids = {str(r.get("song_id")) for r in merged}
    batches, total, promoted = [], 0, 0
    for f in sorted(glob.glob(str(DIR / "*_v*.json"))):
        d = json.load(open(f))
        recs = d.get("records", [])
        ids = [str(r["song_id"]) for r in recs]
        prom = sorted(set(ids) & merged_ids)
        pairs = sum(1 for r in recs if has_out(r))
        batches.append({
            "file": os.path.basename(f),
            "batch": d.get("batch"),
            "from": (d.get("수령") or {}).get("from"),
            "입력_표본": len(recs),
            "짝": pairs,
            "★승격됨(merged 에도 있음)": len(prom),
            "승격_song_id": prom,
            "song_id_범위": f"{min(ids)}~{max(ids)}" if ids else "",
        })
        total += len(recs); promoted += len(prom)
    reg = {
        "무엇": "입력 표본 대장 — 출력층 미관측 수령분의 계상처. ★코퍼스 곡수(merged_4values)와 절대 합산하지 않는다.",
        "재현": "scripts/input_samples_registry_v1.py",
        "잰_시각": datetime.now().astimezone().isoformat(),
        "코퍼스(출력층 관측)": {"merged_4values 곡": len(merged),
                                "그중 입력층도 보유(짝)": sum(1 for r in merged
                                    if ((r.get("leomusic_original") or {}).get("sp") or "").strip())},
        "입력 표본(짝 0)": {"합계": total, "승격 완료": promoted, "미승격": total - promoted},
        "배치별": batches,
        "⛔이 대장이 못 하는 것": [
            "입력 표본은 Suno 어휘 관측이 아니다 — 사전·색인 기여 0.",
            "승격 판정은 song_id 일치만 본다. 내용 동일성은 승격 시점 인제스트가 본다.",
        ],
    }
    print(json.dumps({k: v for k, v in reg.items() if k != "배치별"}, ensure_ascii=False, indent=1))
    for b in batches:
        print(f"  - {b['batch']:14} 입력표본 {b['입력_표본']:3} · 짝 {b['짝']} · 승격 {b['★승격됨(merged 에도 있음)']} · {b['song_id_범위']}")
    if "--write" in sys.argv:
        json.dump(reg, open(OUT, "w"), ensure_ascii=False, indent=1)
        print(f"\nWROTE {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
