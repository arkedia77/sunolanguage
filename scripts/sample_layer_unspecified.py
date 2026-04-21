#!/usr/bin/env python3
"""
layer=unspecified instrument 엔트리 샘플링.
목적: Suno가 "어떤 층인지"를 명시하지 않고 악기만 서술하는 패턴을 수집해 책 5장
"Suno가 묘사하지 않는 것" 장 보강 근거로 사용.

출력:
  docs/layer_unspecified_samples.md   - 정성 보고서
  data/reanalysis_v2/layer_unspecified_sample.json - 샘플 엔트리 (최대 300개)
"""

import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SP_ENTITIES = ROOT / "data" / "reanalysis_v2" / "sp_entities_v3.json"
OUT_JSON = ROOT / "data" / "reanalysis_v2" / "layer_unspecified_sample.json"
OUT_MD = ROOT / "docs" / "layer_unspecified_samples.md"

random.seed(42)


def load_unspecified(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        e for e in data
        if e.get("slot") == "instrument" and e.get("layer") == "unspecified"
    ]


def bucket_entry(e: dict) -> str:
    """pattern/modifiers 조합 기준 분류. effects는 보조 요소라 주축에서 제외.

    - name_only: pattern/modifiers/effects 모두 빈 값 (악기 이름만)
    - modifier_only: modifiers만 (pattern 없음, effects 유무 무관)
    - pattern_only: pattern만 (modifiers 없음)
    - pattern_plus_mods: pattern + modifiers 둘 다 (effects 유무 무관) = 풍성한 묘사
    """
    has_pattern = bool(e.get("pattern"))
    has_mods = bool(e.get("modifiers"))
    has_effects = bool(e.get("effects"))

    if not has_pattern and not has_mods and not has_effects:
        return "name_only"
    if has_pattern and has_mods:
        return "pattern_plus_mods"
    if has_pattern and not has_mods:
        return "pattern_only"
    if has_mods and not has_pattern:
        return "modifier_only"
    return "other"


def main() -> None:
    entries = load_unspecified(SP_ENTITIES)
    total = len(entries)

    buckets: dict[str, list[dict]] = defaultdict(list)
    kit_counter: Counter = Counter()
    role_counter: Counter = Counter()

    for e in entries:
        buckets[bucket_entry(e)].append(e)
        kit_counter[e.get("kit", "?")] += 1
        role_counter[e.get("role", "?")] += 1

    # sample up to 60 per bucket
    sample: dict[str, list[dict]] = {
        name: random.sample(items, min(60, len(items)))
        for name, items in buckets.items()
    }

    flat_sample = [e for lst in sample.values() for e in lst]
    OUT_JSON.write_text(
        json.dumps(flat_sample, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines: list[str] = []
    lines.append("# layer=unspecified 문장 샘플링 (책 5장 근거)")
    lines.append("")
    lines.append(
        f"**총 layer=unspecified instrument 엔트리**: {total}건 "
        f"(SP instrument 1,663 중 {total / 1663 * 100:.1f}%)"
    )
    lines.append("")
    lines.append("## Kit 분포")
    lines.append("")
    for kit, c in kit_counter.most_common():
        lines.append(f"- `{kit}`: {c} ({c / total * 100:.1f}%)")
    lines.append("")
    lines.append("## Role 분포")
    lines.append("")
    for role, c in role_counter.most_common():
        lines.append(f"- `{role}`: {c} ({c / total * 100:.1f}%)")
    lines.append("")
    lines.append("## 문장 패턴 버킷")
    lines.append("")
    bucket_order = ["name_only", "modifier_only", "pattern_only", "pattern_plus_mods", "other"]
    for name in bucket_order:
        items = buckets.get(name, [])
        if not items:
            continue
        lines.append(
            f"### {name} — {len(items)}건 ({len(items) / total * 100:.1f}%)"
        )
        lines.append("")
        description = {
            "name_only": "악기 이름만. pattern/modifiers/effects 모두 없음. "
                        "Suno가 '무엇'을 말하되 '어떻게'는 말하지 않는 케이스.",
            "modifier_only": "형용사(modifier)만 있고 주법/패턴(pattern) 서술 없음. "
                             "정적 특성은 있으나 동적 움직임 묘사 희박.",
            "pattern_only": "주법/패턴은 있으나 modifier/effects 없음. "
                            "동작은 있지만 톤/질감 서술은 생략.",
            "pattern_plus_mods": "pattern + modifiers 둘 다 있음 (effects 유무 무관). "
                    "가장 '풍성한' 묘사 카테고리. 그럼에도 layer 단서는 여전히 없음 → "
                    "'풍성한 묘사'도 'bass/pad/lead/fill/rhythm' 같은 "
                    "기능 층위는 드러내지 못함.",
            "other": "기타 조합.",
        }[name]
        lines.append(description)
        lines.append("")
        for e in sample[name][:15]:
            sent = e.get("sentence", "").strip()
            kit = e.get("kit", "?")
            role = e.get("role", "?")
            genre = e.get("genre", "?")
            lines.append(
                f"- **[{kit}/{role}]** ({genre}) {sent}"
            )
        lines.append("")

    lines.append("## 해석 (초안)")
    lines.append("")
    lines.append(
        "### 1. 묘사의 풍부함과 층위 서술은 분리되어 있다"
    )
    lines.append(
        "`pattern_plus_mods` 버킷이 58.9%(440/747)로 가장 크다. 이 버킷은 주법(pattern)과 "
        "형용사(modifiers)를 둘 다 갖춘 '가장 풍성한' 묘사 카테고리다. 그럼에도 layer는 "
        "전부 unspecified — Suno가 악기 톤·주법·effects를 다 묘사해도 '이 악기가 "
        "bass인가, pad인가, lead인가, rhythm인가' 같은 **기능 층위 언어는 따라붙지 않는다**. "
        "즉 '정교한 묘사'와 '구조적 서술'이 분리된 상태로 공존한다."
    )
    lines.append("")
    lines.append(
        "### 2. guitar 편중 — 호명되지만 배치되지 않는 악기"
    )
    lines.append(
        "layer unspecified의 74.6%(557/747)가 guitar kit다. Suno는 기타를 "
        "'음악의 주체'로 다루지만 그 기타가 리듬 기타인지, 리드 라인인지, 텍스처 패드인지 "
        "**명명하지 않는다**. 책 5장 명제: **Suno는 호명하되 배치하지 않는다** — "
        "악기의 이름과 주법은 있으나, 혼합(mix) 안에서의 위치는 드러내지 않는다."
    )
    lines.append("")
    lines.append(
        "### 3. modifier_only 22.6% — 형용사는 주되 움직임은 주지 않는 묘사"
    )
    lines.append(
        "169건(22.6%)은 modifiers만 있고 pattern이 비어 있다. 'clean', 'bright', "
        "'warm' 같은 톤 형용사는 있지만 **어떻게 움직이는지**는 서술되지 않는다. "
        "이는 Suno 묘사가 '정적 톤 서술' 쪽으로 기울어 있음을 보여준다."
    )
    lines.append("")
    lines.append(
        "### 4. name_only 5.9% — 완전한 침묵의 호명"
    )
    lines.append(
        "44건은 악기 이름만 던지고 끝난다. 다수가 `synth` kit에서 나오며 "
        "장르 지시 문장(예: 'K-Pop and Synth-pop.')의 잔여물. 순수한 "
        "'호명만'은 드물지만, 장르 선언 문장에서 발생한다는 점이 특이."
    )
    lines.append("")
    lines.append(
        "### 책 5장 활용 포인트"
    )
    lines.append(
        "- **Suno의 묘사 축**: 톤(modifier)·주법(pattern)·effects 3축은 활발 / "
        "**층위(layer)·역할(role)은 빈약**. 이 비대칭이 5장의 핵심 논증."
    )
    lines.append(
        "- **반증 실험 제안**: SP에 `[bass layer]`, `[pad layer]`, `[lead layer]`를 "
        "명시 프롬프트로 넣었을 때 Suno 출력이 실제로 반응하는지 후속 검증."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"total={total}, buckets={{{', '.join(f'{k}:{len(v)}' for k, v in buckets.items())}}}")


if __name__ == "__main__":
    main()
