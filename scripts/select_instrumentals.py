#!/usr/bin/env python3
"""I배치 선곡: 전체 인스트루멘탈 89곡에서 장르 커버리지 극대화해서 선택."""
import json
import subprocess
from collections import Counter, defaultdict

# ⛔2026-10-04 fail-closed — 이 스크립트는 **돌지 않는다.**
#   sunomusic `20261004_223342` 실측: mukl `~/.ssh/authorized_keys` 의 purple 키에
#   `command="/Users/mushin/leobridge/outbound_relay.sh"` 가 **강제**돼 있다.
#   ⇒ purple 에서 `ssh mushin@100.75.69.61 <명령>` 을 하면 그 명령 대신 **Slack 발신 중계가 돈다**
#     (leomusic3 에서 Slack 채널이 생긴 사고와 같은 경로. admin 수리분).
#   ★경고 주석은 실행을 막지 못한다 — 그래서 **여기서 멈춘다**(09-26 이후 이 세션에서 배운 fail-closed 규율).
#   바른 길: 필요한 조회·전송을 **sunomusic 에 요청 통**으로 내면 mukl 안에서 처리해 돌려준다.
#   admin 이 purple 에 셸 키를 따로 발급하면 `SUNOMUSIC_SSH_OK=1` 로 풀 수 있다(내 판단 사항 아님).
import os as _os, sys as _sys
if not _os.environ.get("SUNOMUSIC_SSH_OK"):
    _sys.exit(
        "⛔ 막혔습니다 — purple→mushin@100.75.69.61 ssh 는 Slack 발신 중계로 강제됩니다"
        "(sunomusic 20261004_223342 실측).\n"
        "   돌리면 조회·전송 대신 Slack 발신이 일어납니다(leomusic3 사고와 같은 경로).\n"
        "   ▶ 필요한 것은 sunomusic 에 요청 통으로 내십시오 — mukl 안에서 처리해 회신합니다.\n"
        "   ▶ admin 이 purple 에 셸 키를 발급했다면 SUNOMUSIC_SSH_OK=1 로 다시 실행하십시오."
    )

# 현재 265곡 장르
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
merged = json.load(open(_ROOT / "data/reanalysis_v2/merged_4values.json"))
existing_genres = Counter(s.get("genre") or "미정" for s in merged)

# 08-23: 172.30.1.77 ping 불통 → tailscale 고정 주소로 교체 (구: mushin@172.30.1.77)
# ⛔2026-10-04 경고 — 이 주소로의 ssh 는 **다른 머신에서 금지**일 수 있다.
#   sunomusic `20261004_222913` 정정: `mushin@100.75.69.61` 경유는 **mukl 이 자기 자신에 접속할 때만** 맞고,
#   다른 머신의 키는 **Slack 발신 전용**이라 셸이 안 열린다 — leomusic3 에서 **Slack 채널이 생기는 사고**가 났다(admin 수리).
#   ★이 스크립트는 그 정정 이전(08-23)에 쓰였고 purple 에서 그 주소를 쓴다 ⇒ **돌리기 전에 sunomusic 에 확인할 것.**
#   자료가 필요하면 sunomusic 에 요청해 mukl 안에서 꺼내는 쪽이 안전하다.
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
