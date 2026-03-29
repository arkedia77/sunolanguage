#!/bin/bash
# sunolang: 100곡 YouTube 다운로드 + Demucs 스템 분리 배치 스크립트
# 사용법: bash batch_download_stems.sh [start_id] [end_id]
# 예: bash batch_download_stems.sh 1 100

MP3_DIR="$HOME/sunolanguage/data/raw/mp3"
STEMS_DIR="$HOME/sunolanguage/data/raw/stems"
DB="$HOME/sunolanguage/sunolang.db"
LOG="$HOME/sunolanguage/data/raw/batch_log.txt"

START=${1:-2}  # 1번은 이미 완료
END=${2:-100}

mkdir -p "$MP3_DIR" "$STEMS_DIR"

echo "=== 배치 시작: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

for id in $(seq $START $END); do
    # DB에서 트랙 정보 가져오기
    info=$(sqlite3 "$DB" "SELECT id, title, artist FROM tracks WHERE id=$id;")
    if [ -z "$info" ]; then
        echo "[$id] 트랙 없음, 스킵" >> "$LOG"
        continue
    fi

    title=$(echo "$info" | cut -d'|' -f2)
    artist=$(echo "$info" | cut -d'|' -f3)
    # 파일명 안전하게 변환
    safe_name=$(printf "%03d_%s_%s" "$id" "$artist" "$title" | tr '/' '_' | tr ':' '_' | tr '"' '_' | tr "'" '_' | tr ' ' '_' | cut -c1-80)
    mp3_file="$MP3_DIR/${safe_name}.mp3"
    stem_dir="$STEMS_DIR/htdemucs/${safe_name}"

    # 이미 스템 분리 완료된 곡은 스킵
    if [ -d "$stem_dir" ] && [ -f "$stem_dir/drums.mp3" ]; then
        echo "[$id] $title — 이미 완료, 스킵" >> "$LOG"
        continue
    fi

    # 다운로드 (이미 MP3 있으면 스킵)
    if [ ! -f "$mp3_file" ]; then
        echo "[$id] 다운로드: $artist - $title" >> "$LOG"
        search_query="$artist $title"
        yt-dlp -x --audio-format mp3 --audio-quality 0 \
            -o "$mp3_file" \
            "ytsearch1:$search_query" 2>> "$LOG"

        if [ $? -ne 0 ]; then
            echo "[$id] 다운로드 실패!" >> "$LOG"
            continue
        fi
    fi

    # Demucs 스템 분리
    echo "[$id] Demucs 시작: $safe_name" >> "$LOG"
    demucs --mp3 -n htdemucs -o "$STEMS_DIR" "$mp3_file" 2>> "$LOG"

    if [ $? -eq 0 ]; then
        echo "[$id] 완료: $(date '+%H:%M:%S')" >> "$LOG"
    else
        echo "[$id] Demucs 실패!" >> "$LOG"
    fi
done

echo "=== 배치 종료: $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
echo "완료된 스템: $(ls -d $STEMS_DIR/htdemucs/*/ 2>/dev/null | wc -l)개"
