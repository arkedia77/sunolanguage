#!/usr/bin/env python3
"""
W029 국악색 배치 — 서술형 팔레트 선조회 실측기 (leomusic-trot 08-14 23:45 질의 Q2~Q6)

★설계 원칙 (내 반복 오류형 3가지에 대한 방어):
  1) 「내가 떠올린 철자의 0건은 '없음'이 아니라 '안 봄'」 → 항목마다 철자 변이를 다발로 넣고,
     0이 나오면 **역방향 확인**(코퍼스가 실제로 쓰는 이웃 철자)을 같이 출력한다.
  2) 층을 행 안에 박는다 → source별로 쪼개 센다.
       suno_sp_full   = Suno 재분석 **출력층**(Suno가 스스로 그렇게 묘사함)
       leomusic_sp_full = 우리가 넣은 **입력층**(우리가 그렇게 썼음. 렌더 성공 여부는 여기서 안 나옴)
       stems_sp / *_entity = 위 두 층의 파생·부분집합 → 별도 표기, 합산 금지
  3) 곡 수와 행 수를 따로 낸다 (08-11 「23행 ≠ 23곡」 사고 재발 방지).

사용: python3 scripts/w029_gukak_palette_probe_v1.py
출력: data/exchange/w029_gukak_palette_attestation.json + 표준출력 요약
"""
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "reanalysis_v2" / "lexical_index.sqlite"
OUT = REPO / "data" / "exchange" / "w029_gukak_palette_attestation.json"

# 층 구분 — 합산하지 않는다
OUTPUT_LAYER = ("suno_sp_full", "stems_sp")          # Suno가 쓴 문장
INPUT_LAYER = ("leomusic_sp_full",)                   # 우리가 쓴 문장
DERIVED = ("sp_entity", "bracket_entity", "stems_bracket")  # 파싱 파생(부분집합)

QUERIES = {
    "Q2_대금형": {
        "질의문_원문": ["a breathy bamboo flute",
                        "an airy wooden flute with wide vibrato",
                        "breathy flute with slow bends"],
        "구성단위": ["bamboo flute", "wooden flute", "breathy", "airy",
                     "wide vibrato", "slow bends", "flute"],
        "역방향_이웃": ["flute", "woodwind", "recorder", "pan flute", "shakuhachi",
                        "breathy vocal", "airy synth", "bamboo"],
    },
    "Q3_태평소형": {
        "질의문_원문": ["a piercing double-reed", "a reedy double-reed horn",
                        "nasal reed horn"],
        "구성단위": ["double-reed", "double reed", "reedy", "piercing", "nasal",
                     "reed horn"],
        "역방향_이웃": ["oboe", "shawm", "bagpipe", "reed", "horn", "brass",
                        "nasal", "piercing"],
    },
    "Q4_장구형": {
        "질의문_원문": ["a hand-struck barrel drum", "an hourglass hand drum",
                        "two-toned hand drum"],
        "구성단위": ["hand-struck", "barrel drum", "hourglass", "hand drum",
                     "two-toned"],
        "역방향_이웃": ["taiko", "frame drum", "hand percussion", "djembe", "conga",
                        "bongo", "tabla", "darbuka", "log drum"],
    },
    "Q5_가락_민요": {
        "질의문_원문": ["pentatonic melody", "pentatonic phrasing",
                        "call and response vocals"],
        "구성단위": ["pentatonic", "call and response", "call-and-response"],
        "역방향_이웃": ["modal", "minor pentatonic", "antiphonal", "response vocals"],
    },
    "Q6_장단": {
        "질의문_원문": ["9/8", "compound 9/8", "triplet feel"],
        "구성단위": ["9/8", "triplet", "compound meter", "swung", "shuffle"],
        "역방향_이웃": ["6/8", "12/8", "4/4", "3/4", "7/8", "5/4", "polyrhythm",
                        "syncopated"],
    },
    "기확인_대조군": {  # 재질의 아님 — 내 계수기가 그쪽 기지값을 재현하는지 검산용
        "질의문_원문": ["a bowed string with vocal-like glissando",
                        "a plucked string resembling a gayageum"],
        "구성단위": ["resembling", "plucked string", "bowed string", "glissando"],
        "역방향_이웃": [],
    },
}


def count_term(conn, term):
    """LIKE 부분일치. 층별 (행수, 곡수) + 예문 2개."""
    pat = f"%{term.lower()}%"
    rows = conn.execute(
        "SELECT source, song_id, sentence FROM entries "
        "WHERE lower(sentence) LIKE ?", (pat,)
    ).fetchall()
    by_layer = defaultdict(lambda: {"행": 0, "곡": set(), "예": []})
    for src, sid, sent in rows:
        if src in OUTPUT_LAYER:
            key = "출력층"
        elif src in INPUT_LAYER:
            key = "입력층"
        else:
            key = "파생(부분집합)"
        d = by_layer[key]
        d["행"] += 1
        if sid:
            d["곡"].add(sid)
        if len(d["예"]) < 2:
            snippet = sent.strip()
            m = re.search(re.escape(term), snippet, re.I)
            if m:
                s = max(0, m.start() - 60)
                snippet = ("…" if s else "") + snippet[s:m.end() + 60] + "…"
            d["예"].append({"song_id": sid, "source": src, "문장": snippet})
    return {k: {"행": v["행"], "곡": len(v["곡"]), "예": v["예"]}
            for k, v in by_layer.items()}


def main():
    conn = sqlite3.connect(DB)
    total_songs = conn.execute(
        "SELECT COUNT(DISTINCT song_id) FROM entries WHERE song_id IS NOT NULL"
    ).fetchone()[0]
    src_counts = dict(conn.execute(
        "SELECT source, COUNT(*) FROM entries GROUP BY source").fetchall())

    result = {
        "생성": "scripts/w029_gukak_palette_probe_v1.py",
        "질의": "leomusic-trot W029 선조회 (2026-08-14T23:45)",
        "인덱스": {
            "경로": "data/reanalysis_v2/lexical_index.sqlite",
            "재빌드": "2026-08-14 (★직전 판본은 06-12/496곡 기준이라 스테일이었음 — "
                     "그대로 조회했으면 0건이 '없음'이 아니라 '안 봄'이 될 뻔함)",
            "고유_song_id": total_songs,
            "source별_행수": src_counts,
        },
        "층_정의": {
            "출력층": "Suno 재분석 SP — Suno가 스스로 쓴 묘사. attested의 통상 의미",
            "입력층": "우리가 Suno에 넣은 SP — '우리가 썼다'일 뿐 렌더 성공 아님",
            "파생": "위 두 층에서 파싱한 엔티티/브라켓 — 부분집합. 합산 금지",
        },
        "항목": {},
    }

    for qname, spec in QUERIES.items():
        entry = {"질의문_원문": {}, "구성단위": {}, "역방향_이웃": {}}
        for bucket in ("질의문_원문", "구성단위", "역방향_이웃"):
            for term in spec[bucket]:
                entry[bucket][term] = count_term(conn, term)
        result["항목"][qname] = entry

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))

    # 표준출력 요약
    print(f"인덱스: {total_songs}곡 / {sum(src_counts.values())}행  (재빌드 08-14)")
    for qname, entry in result["항목"].items():
        print(f"\n=== {qname} ===")
        for bucket in ("질의문_원문", "구성단위", "역방향_이웃"):
            if not entry[bucket]:
                continue
            print(f"  [{bucket}]")
            for term, layers in entry[bucket].items():
                if not layers:
                    print(f"    {term:34s} → 0건 (전 층)")
                    continue
                parts = [f"{k} {v['곡']}곡/{v['행']}행" for k, v in sorted(layers.items())]
                print(f"    {term:34s} → " + " · ".join(parts))
    print(f"\n✔ {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
