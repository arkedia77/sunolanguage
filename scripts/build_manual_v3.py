#!/usr/bin/env python3
"""v3 entity + templates → 매뉴얼 장별 초안 생성 (책 원자재)"""

import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SP_ENTITIES = BASE / "data/reanalysis_v2/sp_entities_v3.json"
BR_ENTITIES = BASE / "data/reanalysis_v2/bracket_entities_v3.json"
TEMPLATES = BASE / "data/reanalysis_v2/templates_v3.json"
MERGED = BASE / "data/reanalysis_v2/merged_4values.json"
DICTIONARY = BASE / "rag/suno_dictionary.json"
MATRIX = BASE / "data/reanalysis_v2/slot_genre_matrix.json"
OUTPUT_DIR = BASE / "docs/manual_v3"

CHAPTER_MAP = {
    "ch1_classification": {
        "title": "1장: Suno의 분류 체계",
        "slots": ["genre", "tempo_key_time"],
        "description": "Suno가 음악을 분류할 때 사용하는 장르 태깅 체계와 템포/키/박자 표기법"
    },
    "ch2_two_channels": {
        "title": "2장: 두 채널 시스템 — SP 산문 vs 가사 브래킷",
        "slots": None,
        "description": "SP(Style Prompt)의 산문체 묘사와 가사 내 [] 브래킷 지시의 역할 분담"
    },
    "ch3_slot_templates": {
        "title": "3장: 슬롯별 구문 템플릿",
        "slots": ["instrument", "drums", "vocal_main", "vocal_chorus",
                  "arrangement", "mixing", "effect_electronic", "effect_sound",
                  "harmony", "absence", "mastering"],
        "description": "각 슬롯이 SP에서 어떤 문장 구조로 표현되는지 — 템플릿과 실제 예문"
    },
    "ch4_genre_matrix": {
        "title": "4장: 장르별 슬롯 매트릭스",
        "slots": None,
        "description": "장르별로 어떤 슬롯이 채워지고, 어떤 어휘가 선호되는지 히트맵"
    },
    "ch5_absence": {
        "title": "5장: Suno가 묘사하지 않는 것",
        "slots": ["absence", "mastering"],
        "description": "코드 진행 0건, mastering 2건, dynamic markings 0건 — 구조적 공백의 의미"
    }
}


def load_all():
    with open(SP_ENTITIES) as f:
        sp = json.load(f)
    with open(BR_ENTITIES) as f:
        br = json.load(f)
    with open(TEMPLATES) as f:
        templates = json.load(f)
    with open(MERGED) as f:
        merged = json.load(f)
    with open(DICTIONARY) as f:
        dictionary = json.load(f)

    songs = {s["song_id"]: s for s in merged}
    return sp, br, templates, songs, dictionary


def normalize_entity(entity):
    if isinstance(entity, str):
        return entity
    if isinstance(entity, list):
        return ", ".join(str(x) for x in entity)
    if isinstance(entity, dict):
        parts = []
        for k in ["bpm", "key", "time_signature"]:
            v = entity.get(k)
            if v:
                parts.append(f"{k}={v}")
        return " / ".join(parts) if parts else str(entity)
    return str(entity)


def build_entity_stats(entities, source_label):
    """entity별 통계: 출현수, 장르분포, 변이형, 인용문"""
    slot_entities = defaultdict(lambda: defaultdict(lambda: {
        "count": 0, "genres": [], "songs": [], "sentences": [], "modifiers": []
    }))

    for e in entities:
        slot = e.get("slot", "")
        raw_entity = e.get("entity", "")
        if not raw_entity:
            continue
        entity = normalize_entity(raw_entity)
        d = slot_entities[slot][entity]
        d["count"] += 1
        genre = e.get("genre", "")
        if genre:
            d["genres"].append(genre)
        sid = e.get("song_id")
        if sid:
            d["songs"].append(sid)
        sent = e.get("sentence") or e.get("bracket") or ""
        if sent:
            d["sentences"].append({"text": sent, "song_id": sid, "genre": genre})
        mods = e.get("modifiers", [])
        if mods:
            d["modifiers"].extend(mods)

    return slot_entities


def format_entry(entity_name, stats, songs_db, rank):
    """매뉴얼 엔트리 포맷"""
    count = stats["count"]
    genre_counts = Counter(stats["genres"]).most_common(5)
    mod_counts = Counter(stats["modifiers"]).most_common(5)
    unique_songs = len(set(stats["songs"]))

    status = "confirmed" if count >= 10 else "plausible" if count >= 3 else "single_occurrence"

    lines = [f"### {rank}. {entity_name}"]
    lines.append(f"- **출현**: {count}회 ({unique_songs}곡)")
    lines.append(f"- **검증**: {status}")

    if genre_counts:
        genre_str = ", ".join(f"{g}({c})" for g, c in genre_counts)
        lines.append(f"- **장르 분포**: {genre_str}")

    if mod_counts:
        mod_str = ", ".join(f"`{m}`({c})" for m, c in mod_counts)
        lines.append(f"- **주요 수식어**: {mod_str}")

    quotes = []
    seen = set()
    for s in stats["sentences"]:
        if s["song_id"] in seen or not s["text"]:
            continue
        seen.add(s["song_id"])
        song = songs_db.get(s["song_id"], {})
        title = song.get("title", f"#{s['song_id']}")
        quotes.append(f"  - #{s['song_id']:04d} *{title}* [{s['genre']}]\n    > {s['text'][:200]}")
        if len(quotes) >= 3:
            break

    if quotes:
        lines.append("- **인용문**:")
        lines.extend(quotes)

    return "\n".join(lines)


def build_ch1(sp_stats, templates, songs_db):
    """1장: Suno의 분류 체계"""
    lines = ["# 1장: Suno의 분류 체계\n"]
    lines.append("> Suno가 음악을 들었을 때 가장 먼저 출력하는 것: 장르 태그와 템포/키/박자.\n")

    # genre 슬롯
    lines.append("## 1.1 장르 태깅")
    genre_ents = sp_stats["genre"]
    sorted_genres = sorted(genre_ents.items(), key=lambda x: x[1]["count"], reverse=True)
    lines.append(f"\n총 {len(sorted_genres)}개 장르 표현, {sum(e['count'] for _, e in sorted_genres)}회 출현\n")

    for i, (name, stats) in enumerate(sorted_genres[:30], 1):
        lines.append(format_entry(name, stats, songs_db, i))
        lines.append("")

    # tempo_key_time 슬롯
    lines.append("\n## 1.2 템포 · 키 · 박자")
    tkt_ents = sp_stats["tempo_key_time"]
    sorted_tkt = sorted(tkt_ents.items(), key=lambda x: x[1]["count"], reverse=True)
    lines.append(f"\n총 {len(sorted_tkt)}개 표현, {sum(e['count'] for _, e in sorted_tkt)}회 출현\n")

    for i, (name, stats) in enumerate(sorted_tkt[:20], 1):
        lines.append(format_entry(name, stats, songs_db, i))
        lines.append("")

    # genre 템플릿
    lines.append("\n## 1.3 장르 문장 템플릿")
    genre_tmpl = templates.get("sp", {}).get("genre", {})
    if genre_tmpl:
        lines.append(f"\n고유 템플릿 {genre_tmpl.get('unique_templates', 0)}개\n")
        for t in genre_tmpl.get("top", [])[:10]:
            lines.append(f"- `{t['template']}` ({t['count']}회)")
            if t.get("examples"):
                lines.append(f"  - 예: {t['examples'][0]}")

    return "\n".join(lines)


def build_ch2(sp_stats, br_stats, templates, songs_db):
    """2장: 두 채널 시스템"""
    lines = ["# 2장: 두 채널 시스템 — SP 산문 vs 가사 브래킷\n"]
    lines.append("> Suno는 하나의 음악을 두 가지 언어로 묘사한다: SP의 산문체 분석과 가사 안의 [] 브래킷 지시.\n")

    # SP vs BR 통계 비교
    sp_total = sum(sum(e["count"] for e in slot.values()) for slot in sp_stats.values())
    br_total = sum(sum(e["count"] for e in slot.values()) for slot in br_stats.values())

    lines.append("## 2.1 채널 비교\n")
    lines.append(f"| 구분 | SP 산문 | 가사 브래킷 |")
    lines.append(f"|------|--------|-----------|")
    lines.append(f"| 총 entity | {sp_total} | {br_total} |")
    lines.append(f"| 슬롯 종류 | {len(sp_stats)} | {len(br_stats)} |")

    # 슬롯별 양 채널 비교
    lines.append("\n## 2.2 슬롯별 채널 분포\n")
    all_slots = sorted(set(list(sp_stats.keys()) + list(br_stats.keys())))
    lines.append("| 슬롯 | SP | 브래킷 | SP 비율 |")
    lines.append("|------|---:|------:|-------:|")
    for slot in all_slots:
        sp_c = sum(e["count"] for e in sp_stats.get(slot, {}).values())
        br_c = sum(e["count"] for e in br_stats.get(slot, {}).values())
        total = sp_c + br_c
        ratio = f"{sp_c/(total)*100:.0f}%" if total > 0 else "-"
        lines.append(f"| {slot} | {sp_c} | {br_c} | {ratio} |")

    # 동일 entity 양쪽 출현 분석
    lines.append("\n## 2.3 양쪽 채널 모두 등장하는 표현\n")
    overlap_count = 0
    overlap_examples = []
    for slot in all_slots:
        sp_ents = set(sp_stats.get(slot, {}).keys())
        br_ents = set(br_stats.get(slot, {}).keys())
        both = sp_ents & br_ents
        overlap_count += len(both)
        for e in sorted(both, key=lambda x: sp_stats[slot][x]["count"], reverse=True)[:3]:
            sp_n = sp_stats[slot][e]["count"]
            br_n = br_stats[slot][e]["count"]
            overlap_examples.append(f"- **{e}** ({slot}): SP {sp_n}회 / 브래킷 {br_n}회")

    lines.append(f"총 {overlap_count}개 표현이 양쪽 채널에 모두 출현\n")
    for ex in overlap_examples[:15]:
        lines.append(ex)

    # 브래킷 전용 표현
    lines.append("\n## 2.4 브래킷에만 나타나는 표현 (SP 부재)\n")
    br_only = []
    for slot in all_slots:
        sp_ents = set(sp_stats.get(slot, {}).keys())
        br_ents = set(br_stats.get(slot, {}).keys())
        only = br_ents - sp_ents
        for e in sorted(only, key=lambda x: br_stats[slot][x]["count"], reverse=True)[:3]:
            br_only.append((e, slot, br_stats[slot][e]["count"]))
    br_only.sort(key=lambda x: x[2], reverse=True)
    for e, slot, c in br_only[:15]:
        lines.append(f"- **{e}** ({slot}): 브래킷 {c}회")

    return "\n".join(lines)


def build_ch3(sp_stats, br_stats, templates, songs_db):
    """3장: 슬롯별 구문 템플릿"""
    slots_order = ["instrument", "drums", "vocal_main", "vocal_chorus",
                   "arrangement", "mixing", "effect_electronic", "effect_sound",
                   "harmony", "absence", "mastering"]

    lines = ["# 3장: 슬롯별 구문 템플릿\n"]
    lines.append("> 각 슬롯이 SP에서 어떤 문장 구조로 표현되는지 — 템플릿 패턴과 대표 엔트리.\n")

    for slot in slots_order:
        ents = sp_stats.get(slot, {})
        sorted_ents = sorted(ents.items(), key=lambda x: x[1]["count"], reverse=True)
        total = sum(e["count"] for _, e in sorted_ents)

        lines.append(f"\n## 3.{slots_order.index(slot)+1} {slot.upper()}")
        lines.append(f"\nentity {len(sorted_ents)}종 / {total}회 출현\n")

        # 템플릿
        tmpl = templates.get("sp", {}).get(slot, {})
        if tmpl and tmpl.get("top"):
            lines.append(f"**구문 템플릿** (고유 {tmpl.get('unique_templates', 0)}개):\n")
            for t in tmpl["top"][:5]:
                lines.append(f"- `{t['template']}` ({t['count']}회)")
                if t.get("examples"):
                    lines.append(f"  - {t['examples'][0]}")
            lines.append("")

        # 브래킷 쪽 템플릿
        br_tmpl = templates.get("lyrics_brackets", {}).get(slot, {})
        if br_tmpl and br_tmpl.get("top"):
            lines.append(f"**브래킷 패턴** (고유 {br_tmpl.get('unique_templates', 0)}개):\n")
            for t in br_tmpl["top"][:5]:
                lines.append(f"- `{t['template']}` ({t['count']}회)")
            lines.append("")

        # 상위 엔트리
        lines.append(f"**상위 엔트리**:\n")
        for i, (name, stats) in enumerate(sorted_ents[:15], 1):
            lines.append(format_entry(name, stats, songs_db, i))
            lines.append("")

    return "\n".join(lines)


def build_ch4(matrix_path):
    """4장: 장르별 슬롯 매트릭스"""
    with open(matrix_path) as f:
        matrix_data = json.load(f)

    matrix = matrix_data["matrix"]
    slots = matrix_data["slots"]

    lines = ["# 4장: 장르별 슬롯 매트릭스\n"]
    lines.append(f"> {len(matrix)}개 장르 × {len(slots)}개 슬롯 히트맵. 장르마다 어떤 슬롯을 채우고, 어떤 어휘를 선호하는지.\n")

    # 요약 테이블
    lines.append("## 4.1 히트맵 요약\n")
    short = {"genre": "GNR", "instrument": "INS", "drums": "DRM",
             "vocal_main": "VOC", "vocal_chorus": "CHR", "arrangement": "ARR",
             "mixing": "MIX", "effect_electronic": "EFX", "effect_sound": "SFX",
             "tempo_key_time": "TMP", "harmony": "HAR", "absence": "ABS",
             "mastering": "MST"}

    header = "| 장르 | 곡수 | " + " | ".join(short[s] for s in slots) + " | 채움 |"
    sep = "|" + "|".join(["---"] * (len(slots) + 3)) + "|"
    lines.append(header)
    lines.append(sep)

    for row in matrix[:30]:
        cells = []
        for s in slots:
            v = row["slots"][s]["per_song"]
            if v == 0:
                cells.append("·")
            elif v < 1:
                cells.append(f".{int(v*10)}")
            else:
                cells.append(f"{v:.1f}")
        fill = f"{row['slots_filled']}/{row['slots_total']}"
        lines.append(f"| {row['genre']} | {row['song_count']} | " +
                     " | ".join(cells) + f" | {fill} |")

    # 장르별 상세 (상위 10개)
    lines.append("\n## 4.2 장르별 상세\n")
    for row in matrix[:10]:
        genre = row["genre"]
        lines.append(f"### {genre} ({row['song_count']}곡)\n")
        for s in slots:
            sd = row["slots"][s]
            if sd["count"] == 0:
                continue
            top = ", ".join(f"`{e['entity']}`({e['freq']})" for e in sd["top_entities"][:3])
            lines.append(f"- **{s}** [{sd['count']}회, 곡당 {sd['per_song']}]: {top}")
        lines.append("")

    # 갭 분석
    gaps = matrix_data.get("gaps", [])
    if gaps:
        lines.append(f"\n## 4.3 구조적 공백 ({len(gaps)}건)\n")
        lines.append("다음 장르×슬롯 조합은 3곡 이상 존재하지만 해당 슬롯 entity가 0건:\n")
        for g in gaps[:30]:
            lines.append(f"- **{g['genre']}** × {g['missing_slot']} ({g['song_count']}곡)")

    return "\n".join(lines)


def build_ch5(sp_stats, dictionary, songs_db):
    """5장: Suno가 묘사하지 않는 것"""
    lines = ["# 5장: Suno가 묘사하지 않는 것\n"]
    lines.append("> 437곡의 Suno 재분석에서 체계적으로 빠진 것들. 구조적 공백은 Suno의 한계이자 SP 작성의 핵심 가이드.\n")

    # mastering
    lines.append("## 5.1 마스터링 — 2건\n")
    mast = sp_stats.get("mastering", {})
    if mast:
        for name, stats in sorted(mast.items(), key=lambda x: x[1]["count"], reverse=True):
            lines.append(format_entry(name, stats, songs_db, 1))
    else:
        lines.append("SP에서 mastering 관련 표현 0건.")
    lines.append(f"\n> Suno는 마스터링을 거의 묘사하지 않는다. limiter 0건, compressor 0건, loudness 0건. "
                 f"master bus 언급이 전부인 2건만 존재.\n")

    # harmony (코드 진행)
    lines.append("## 5.2 코드 진행 — 0건\n")
    lines.append("Suno는 `key of X` (652회)는 지정하지만, 구체적 코드명(Am7, Cmaj7 등)은 0건, "
                 "코드 진행 표기(I-IV-V-I 등)도 0건.")
    lines.append("\n- `key of` 패턴: 652회 출현")
    lines.append("- 구체적 코드명 (Am, Cm7, Gmaj7 등): **0건**")
    lines.append("- 진행 표기 (I-IV-V, ii-V-I 등): **0건**")
    lines.append("\n> 화성은 '조성' 수준에서만 인식. 세부 코드는 Suno의 묘사 영역 밖.\n")

    # dynamic markings
    lines.append("## 5.3 다이내믹 마킹 — 0건\n")
    lines.append("pp, mf, ff, crescendo, diminuendo 같은 클래식 다이내믹 마킹은 0건.")
    lines.append("Suno는 대신 `builds`, `swells`, `drops` 같은 자연어 표현을 사용.\n")

    # absence 슬롯
    lines.append("## 5.4 absence 슬롯 — 명시적 부재 지시\n")
    abs_ents = sp_stats.get("absence", {})
    sorted_abs = sorted(abs_ents.items(), key=lambda x: x[1]["count"], reverse=True)
    lines.append(f"\n{len(sorted_abs)}종 / {sum(e['count'] for _, e in sorted_abs)}회\n")
    for i, (name, stats) in enumerate(sorted_abs, 1):
        lines.append(format_entry(name, stats, songs_db, i))
        lines.append("")

    # suno_does_not_use
    doesnt_use = dictionary.get("suno_does_not_use", {})
    if doesnt_use:
        lines.append("\n## 5.5 Suno Dead Zone — 입력해도 무시되는 표현\n")
        lines.append("Dead Budget 실험(10곡 라운드트립)에서 발견된 '데드존' 표현들:\n")
        if isinstance(doesnt_use, dict):
            for category, items in doesnt_use.items():
                if isinstance(items, list):
                    lines.append(f"\n**{category}**:")
                    for item in items[:10]:
                        if isinstance(item, dict):
                            lines.append(f"- `{item.get('term', item)}` — {item.get('note', '')}")
                        else:
                            lines.append(f"- `{item}`")
                elif isinstance(items, dict):
                    lines.append(f"\n**{category}**: {json.dumps(items, ensure_ascii=False)[:200]}")

    return "\n".join(lines)


def main():
    print("Loading all data...")
    sp, br, templates, songs_db, dictionary = load_all()
    print(f"  SP: {len(sp)}, BR: {len(br)}, Songs: {len(songs_db)}")

    sp_stats = build_entity_stats(sp, "sp")
    br_stats = build_entity_stats(br, "br")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chapters = [
        ("ch1_classification.md", build_ch1(sp_stats, templates, songs_db)),
        ("ch2_two_channels.md", build_ch2(sp_stats, br_stats, templates, songs_db)),
        ("ch3_slot_templates.md", build_ch3(sp_stats, br_stats, templates, songs_db)),
        ("ch4_genre_matrix.md", build_ch4(MATRIX)),
        ("ch5_absence.md", build_ch5(sp_stats, dictionary, songs_db)),
    ]

    for filename, content in chapters:
        path = OUTPUT_DIR / filename
        with open(path, "w") as f:
            f.write(content)
        line_count = content.count("\n")
        print(f"  {filename}: {line_count} lines")

    print(f"\nAll chapters saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
