#!/usr/bin/env python3
"""I배치 선곡: 전체 인스트루멘탈 89곡에서 장르 커버리지 극대화해서 선택."""
import json
import subprocess
from collections import Counter, defaultdict

# 현재 265곡 장르
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
merged = json.load(open(_ROOT / "data/reanalysis_v2/merged_4values.json"))
existing_genres = Counter(s.get("genre") or "미정" for s in merged)

# 08-23: 172.30.1.77 ping 불통 → tailscale 고정 주소로 교체 (구: mushin@172.30.1.77)
cmd = ["ssh", "mushin@100.75.69.61",
       "sqlite3 -json ~/projects/leomusic-cli/leomusic.db "
       "\"SELECT global_id, batch, genre, subgenre, bpm, title, substr(style_prompt,1,100) AS sp_head "
       "FROM songs WHERE (lyrics IS NULL OR lyrics = '' OR lyrics LIKE '%[instrumental]%' OR lyrics LIKE '%Instrumental%') "
       "AND style_prompt IS NOT NULL ORDER BY genre, global_id\""]
rows = json.loads(subprocess.check_output(cmd, text=True))
print(f"총 인스트 후보: {len(rows)}곡")

# 장르 그룹
by_genre = defaultdict(list)
for r in rows:
    by_genre[r.get("genre") or "미정"].append(r)

# 선정 기준:
# (A) 신규 장르 (현 265곡에 없음) → 전수
# (B) 기존 장르라도 인스트 유니크 샘플 → 최대 3곡/장르
selected = []
new_genres = []
reinforced = []
for g, items in by_genre.items():
    in_existing = existing_genres.get(g, 0) > 0
    pick = items if not in_existing else items[:3]
    for it in pick:
        selected.append(it)
        (reinforced if in_existing else new_genres).append(it)

print(f"\n신규 장르 인스트 ({len(new_genres)}곡) — 커버리지 확장:")
for r in new_genres:
    print(f"  [{r['genre']}] {r['global_id']} {r['title']}")
print(f"\n기존 장르 인스트 보강 ({len(reinforced)}곡)")
for r in reinforced[:15]:
    print(f"  [{r['genre']}] {r['global_id']} {r['title']}")
print(f"... (총 {len(reinforced)})")
print(f"\n최종 선정: {len(selected)}곡")

out = {
    "selected_count": len(selected),
    "new_genre_count": len(new_genres),
    "reinforce_count": len(reinforced),
    "songs": selected,
}
open(_ROOT / "data/reanalysis_v2/instrumental_selection.json",'w').write(
    json.dumps(out, ensure_ascii=False, indent=2))
print("out: data/reanalysis_v2/instrumental_selection.json")
