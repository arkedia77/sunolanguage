#!/bin/zsh
# antisuno R3 — 독립 교차검증 라운드 (검증자: agy = antigravity-cli)
# 브리프: docs/antisuno/survey_brief_r3_crosscheck.md  ★블라인드(우리 값 미제시)
# 생성 0 · 크레딧 0 · 읽기 전용 조사
set -u
ROOT="/Users/purple/sunolanguage"
OUT="$ROOT/data/antisuno/survey3"
BRIEF="$ROOT/docs/antisuno/survey_brief_r3_crosscheck.md"
mkdir -p "$OUT"

# 클러스터 = 엔진군. agy 세션 하나당 1클러스터(문맥 격리 = 교차오염 방지)
typeset -A CLUSTERS
CLUSTERS[limits_langs]="Suno, Udio, ElevenLabs Music, MiniMax Music, Mureka, Stable Audio, ACE-Step, Google Lyria — 문항 1·2 (문자 상한 · 음악 생성 문서의 한국어 명시)"
CLUSTERS[bracket_grammar]="Suno, Udio, ElevenLabs Music, MiniMax Music, ACE-Step, YuE, DiffRhythm, SongBloom, LeVo — 문항 3·4 (가사 채널 괄호 문법 · ★태그 비가창을 공식이 보증하는가)"
CLUSTERS[params_seed]="Udio, ElevenLabs Music, MiniMax Music, Mureka, Stable Audio, ACE-Step, Lyria, MusicGen/JASCO — 문항 5·6 (seed·가중/네거티브 프롬프트·inpaint·BPM/키 독립 파라미터)"

for c in ${(k)CLUSTERS}; do
  echo "▶ $c 시작 $(date +%H:%M:%S)"
  agy --print "$(cat "$BRIEF")

---
# 이번 세션의 클러스터
${CLUSTERS[$c]}

위 브리프의 절대 규칙을 지켜 이 클러스터만 조사하고, 마지막에 JSON 한 덩이만 \`\`\`json 펜스로 출력하세요.
출처 URL을 실제로 열어 확인한 값만 적고, 확인 못 한 칸은 null로 두세요." \
    --print-timeout 900s < /dev/null > "$OUT/raw_$c.txt" 2>&1
  echo "◀ $c 완료 rc=$? · $(wc -c < "$OUT/raw_$c.txt")B → $OUT/raw_$c.txt"
done
echo "전 클러스터 종료. 추출: .venv/bin/python scripts/antisuno_extract_survey.py 로 파싱(경로 survey3)"
