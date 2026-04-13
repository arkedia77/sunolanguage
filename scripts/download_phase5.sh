#!/bin/bash
# Phase 5: 23곡 YouTube 다운로드 + Demucs 스템 분리
# 사용법: bash scripts/download_phase5.sh

set -e

MP3_DIR="/Users/leo/sunolanguage/data/mp3_phase5"
STEMS_DIR="/Users/leo/sunolanguage/data/stems_phase5"
DATA_FILE="/Users/leo/sunolanguage/data/phase5_genre_expansion.json"

mkdir -p "$MP3_DIR" "$STEMS_DIR"

# JSON에서 트랙 정보 추출
TRACKS=$(python3 -c "
import json
with open('$DATA_FILE') as f:
    data = json.load(f)
for i, t in enumerate(data['tracks']):
    # id는 131부터
    tid = 131 + i
    safe_title = t['title'].replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace(\"'\", '')
    safe_artist = t['artist'].replace(' ', '_').replace('/', '_').replace('&', 'and').replace('(', '').replace(')', '').replace(\"'\", '')
    print(f'{tid}|{safe_artist}_{safe_title}|{t[\"youtube_query\"]}')
")

TOTAL=$(echo "$TRACKS" | wc -l | tr -d ' ')
COUNT=0

echo "=== Phase 5: $TOTAL곡 다운로드 + Demucs ==="
echo ""

while IFS='|' read -r ID NAME QUERY; do
    COUNT=$((COUNT + 1))
    OUTFILE="$MP3_DIR/${ID}_${NAME}.mp3"
    STEM_OUT="$STEMS_DIR/${ID}_${NAME}"

    # 이미 스템 있으면 스킵
    if [ -d "$STEM_OUT" ] && [ "$(ls "$STEM_OUT"/*.wav 2>/dev/null | wc -l)" -ge 4 ]; then
        echo "[$COUNT/$TOTAL] $ID $NAME — 스킵 (스템 있음)"
        continue
    fi

    echo "[$COUNT/$TOTAL] $ID $NAME"

    # 1. 다운로드 (이미 있으면 스킵)
    if [ ! -f "$OUTFILE" ]; then
        echo "  ↓ 다운로드: $QUERY"
        yt-dlp -x --audio-format mp3 --audio-quality 0 \
            -o "$OUTFILE" \
            "ytsearch1:$QUERY" 2>&1 | grep -E "Downloading|Destination|already" || true
    else
        echo "  ↓ MP3 있음, 스킵"
    fi

    # 2. Demucs 스템 분리
    if [ -f "$OUTFILE" ]; then
        echo "  ♪ Demucs 분리 중..."
        demucs --two-stems=drums "$OUTFILE" -o "/tmp/demucs_phase5" -n htdemucs 2>&1 | tail -1 || true
        demucs "$OUTFILE" -o "/tmp/demucs_phase5" -n htdemucs 2>&1 | tail -1 || true

        # Demucs 출력 폴더 찾기
        DEMUCS_OUT=$(find /tmp/demucs_phase5/htdemucs/ -maxdepth 1 -name "${ID}_*" -type d 2>/dev/null | head -1)
        if [ -n "$DEMUCS_OUT" ] && [ -d "$DEMUCS_OUT" ]; then
            mkdir -p "$STEM_OUT"
            cp "$DEMUCS_OUT"/*.wav "$STEM_OUT/" 2>/dev/null || true
            echo "  ✓ 스템 저장: $STEM_OUT"
            ls -lh "$STEM_OUT"/*.wav 2>/dev/null | awk '{print "    " $5 " " $NF}'
        else
            echo "  ✗ Demucs 출력 없음"
        fi
    else
        echo "  ✗ MP3 다운로드 실패"
    fi

    echo ""
done <<< "$TRACKS"

echo "=== 완료 ==="
echo "MP3: $(ls "$MP3_DIR"/*.mp3 2>/dev/null | wc -l | tr -d ' ')개"
echo "스템 폴더: $(ls -d "$STEMS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')개"
