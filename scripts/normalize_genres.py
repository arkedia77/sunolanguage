#!/usr/bin/env python3
"""장르명 정규화: 중복 장르를 통합하고 genre_analysis.json 업데이트"""

import json
from collections import defaultdict

# 정규화 매핑 (변형 → 표준명)
GENRE_MAP = {
    "lo-fi hip hop": "lo-fi hip-hop",
    "lofi hip-hop": "lo-fi hip-hop",
    "lo-fi hip-hop": "lo-fi hip-hop",
    "hip hop": "hip-hop",
    "hip-hop": "hip-hop",
    "pop rock": "pop-rock",
    "pop-rock": "pop-rock",
    "boom bap": "boom-bap",
    "boom-bap": "boom-bap",
}

def merge_genre_fields(genres_data, names):
    """여러 장르의 필드를 병합"""
    merged_terms = set()
    merged_fields = defaultdict(set)

    for name in names:
        if name not in genres_data:
            continue
        entry = genres_data[name]
        fields = entry.get("fields", {})
        for field_name, terms in fields.items():
            for term in terms:
                merged_fields[field_name].add(term)
                merged_terms.add(term)

    return {
        "total_unique_terms": len(merged_terms),
        "fields": {k: sorted(list(v)) for k, v in merged_fields.items()}
    }

def normalize():
    with open("data/parsed/genre_analysis.json") as f:
        data = json.load(f)

    print(f"정규화 전: {len(data)}개 장르")

    # 역매핑: 표준명 → [변형들]
    standard_to_variants = defaultdict(set)
    for variant, standard in GENRE_MAP.items():
        standard_to_variants[standard].add(variant)

    # 병합 실행
    normalized = {}
    merged_genres = set()

    for standard, variants in standard_to_variants.items():
        all_names = variants | {standard}
        existing = [n for n in all_names if n in data]
        if len(existing) > 1:
            print(f"  통합: {existing} → {standard}")
            normalized[standard] = merge_genre_fields(data, existing)
            merged_genres.update(existing)

    # 통합되지 않은 장르는 그대로 복사
    for genre, entry in data.items():
        if genre not in merged_genres:
            normalized[genre] = entry
        elif genre in GENRE_MAP.values() and genre not in normalized:
            normalized[genre] = entry

    print(f"정규화 후: {len(normalized)}개 장르")

    # 저장
    with open("data/parsed/genre_analysis_normalized.json", "w") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    # 통합 결과 요약
    print("\n=== 통합 결과 ===")
    for standard in sorted(standard_to_variants.keys()):
        if standard in normalized:
            print(f"  {standard}: {normalized[standard]['total_unique_terms']}개 용어")

if __name__ == "__main__":
    normalize()
