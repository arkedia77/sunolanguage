#!/usr/bin/env python3
"""
sunolang RAG 인덱스 빌더

정규화된 genre_analysis + vocab_index + parsed_tracks에서
장르별 / 악기별 / 주법별 검색 인덱스를 생성.

출력: rag/ 폴더에 JSON 인덱스 파일들
"""

import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
RAG_DIR = PROJECT_ROOT / "rag"
RAG_DIR.mkdir(parents=True, exist_ok=True)

# 장르 정규화 매핑
GENRE_NORMALIZE = {
    "lo-fi hip hop": "lo-fi hip-hop",
    "lofi hip-hop": "lo-fi hip-hop",
    "hip hop": "hip-hop",
    "pop rock": "pop-rock",
    "boom bap": "boom-bap",
}


def load_data():
    # 정규화된 장르 분석이 있으면 사용
    norm_path = PARSED_DIR / "genre_analysis_normalized.json"
    orig_path = PARSED_DIR / "genre_analysis.json"
    genre_path = norm_path if norm_path.exists() else orig_path

    with open(genre_path) as f:
        genres = json.load(f)
    with open(PARSED_DIR / "vocab_index.json") as f:
        vocab = json.load(f)
    with open(PARSED_DIR / "parsed_tracks.json") as f:
        tracks = json.load(f)
    with open(PARSED_DIR / "audiocards_mapped.json") as f:
        audiocards = json.load(f)
    return genres, vocab, tracks, audiocards


def build_genre_index(genres):
    """장르별 어휘 인덱스: genre → {instruments, techniques, production, mood, ...}"""
    index = {}
    for genre, data in genres.items():
        fields = data.get("fields", {})
        index[genre] = {
            "total_terms": data.get("total_unique_terms", 0),
            "instruments": fields.get("ac_instruments", []),
            "techniques": fields.get("ac_techniques", []),
            "production": fields.get("ac_production", []),
            "mood": fields.get("ac_mood_emotion", []),
            "timbre": fields.get("ac_timbre", []),
            "genre_style": fields.get("ac_genre_style", []),
            "temporal": fields.get("ac_temporal_structure", []),
        }
    return index


def build_instrument_index(genres):
    """악기별 인덱스: instrument → [genres that use it + co-occurring terms]"""
    inst_genres = defaultdict(set)
    inst_techniques = defaultdict(set)

    for genre, data in genres.items():
        fields = data.get("fields", {})
        instruments = fields.get("ac_instruments", [])
        techniques = fields.get("ac_techniques", [])

        for inst in instruments:
            inst_genres[inst].add(genre)
            for tech in techniques:
                inst_techniques[inst].add(tech)

    index = {}
    for inst in sorted(inst_genres.keys()):
        index[inst] = {
            "genres": sorted(inst_genres[inst]),
            "co_techniques": sorted(inst_techniques.get(inst, set())),
            "genre_count": len(inst_genres[inst]),
        }
    return index


def build_technique_index(genres):
    """주법별 인덱스: technique → [genres + co-occurring instruments]"""
    tech_genres = defaultdict(set)
    tech_instruments = defaultdict(set)

    for genre, data in genres.items():
        fields = data.get("fields", {})
        instruments = fields.get("ac_instruments", [])
        techniques = fields.get("ac_techniques", [])

        for tech in techniques:
            tech_genres[tech].add(genre)
            for inst in instruments:
                tech_instruments[tech].add(inst)

    index = {}
    for tech in sorted(tech_genres.keys()):
        index[tech] = {
            "genres": sorted(tech_genres[tech]),
            "co_instruments": sorted(tech_instruments.get(tech, set())),
            "genre_count": len(tech_genres[tech]),
        }
    return index


def build_production_index(genres):
    """프로덕션 용어 인덱스: term → [genres]"""
    prod_genres = defaultdict(set)
    for genre, data in genres.items():
        for term in data.get("fields", {}).get("ac_production", []):
            prod_genres[term].add(genre)
    return {
        term: {"genres": sorted(gs), "genre_count": len(gs)}
        for term, gs in sorted(prod_genres.items())
    }


def build_search_index(genres):
    """통합 검색 인덱스: 모든 용어 → [{genre, field, term}]"""
    entries = []
    for genre, data in genres.items():
        for field, terms in data.get("fields", {}).items():
            for term in terms:
                entries.append({
                    "term": term.lower(),
                    "genre": genre,
                    "field": field,
                })
    # term 기준으로 그룹핑
    grouped = defaultdict(list)
    for e in entries:
        grouped[e["term"]].append({"genre": e["genre"], "field": e["field"]})

    return dict(sorted(grouped.items()))


def main():
    genres, vocab, tracks, audiocards = load_data()
    print(f"Loaded: {len(genres)} genres, {len(tracks)} tracks")

    genre_idx = build_genre_index(genres)
    inst_idx = build_instrument_index(genres)
    tech_idx = build_technique_index(genres)
    prod_idx = build_production_index(genres)
    search_idx = build_search_index(genres)

    outputs = {
        "genre_index.json": genre_idx,
        "instrument_index.json": inst_idx,
        "technique_index.json": tech_idx,
        "production_index.json": prod_idx,
        "search_index.json": search_idx,
    }

    for fname, data in outputs.items():
        path = RAG_DIR / fname
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  {fname}: {len(data)} entries")

    # 요약 메타
    meta = {
        "version": "1.0",
        "source": "genre_analysis_normalized.json",
        "total_genres": len(genre_idx),
        "total_instruments": len(inst_idx),
        "total_techniques": len(tech_idx),
        "total_production_terms": len(prod_idx),
        "total_search_terms": len(search_idx),
        "tracks_count": len(tracks),
    }
    with open(RAG_DIR / "meta.json", "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"\nRAG index built: {meta}")


if __name__ == "__main__":
    main()
