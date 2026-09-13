#!/usr/bin/env bash
# safe_commit.sh — 공유 클론(agent-comm)에서 «내 것만» 커밋한다.
#
# ★왜 도구인가: 2026-09-13 내 커밋 832154065e에 leomusic 파일 4건이 섞여
#   그쪽 발신통이 조기 배달됐다. 기전 = 공유 클론은 인덱스가 하나인데
#   `git add`로 내 것만 담고 `git commit`을 «경로 없이» 돌린 것.
# ⛔leomusic 실측(같은 날): **`--only`를 쓴 쪽에서도 못 막혔다** —
#   `--only`는 「내 커밋이 남의 것을 삼키는 것」만 막고
#   「남의 커밋이 내 staged를 삼키는 것」은 못 막는다. ⇒ 받는 쪽은 자기를 못 지킨다.
# ⇒ 그래서 «조심»이 아니라 **커밋 직전에 staged를 세어 보고 남의 것이 있으면 경로를 강제**한다.
# ⛔macOS 기본 bash는 3.2라 `mapfile`이 없다(양성통제에서 잡힘) — while-read로 짠다.
set -u
cd ~/projects/agent-comm || exit 1
ME="${AGENT_ID:-sunolanguage}"
MSG="${1:?사용: safe_commit.sh \"커밋 메시지\" [경로...]}"
shift || true

N=0; FN=0; FOREIGN=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  N=$((N+1))
  case "$f" in
    projects/$ME/*) ;;
    */messages/*_${ME}_*.json) ;;
    *) FN=$((FN+1)); FOREIGN="$FOREIGN
    $f" ;;
  esac
done <<< "$(git -c core.quotepath=false diff --cached --name-only)"

if [ "$N" -eq 0 ]; then echo "⛔staged 0건 — 커밋할 것이 없습니다"; exit 1; fi
echo "■ staged ${N}건 · 내 범위 $((N-FN)) · ★남의 것 ${FN}"
if [ "$FN" -gt 0 ]; then
  echo "⛔남의 파일이 인덱스에 있습니다 — 경로를 못 박아 커밋합니다(남의 것은 안 건드림):$FOREIGN"
  if [ "$#" -eq 0 ]; then
    echo "⛔경로 인자가 없습니다. 내 파일 경로를 인자로 주십시오."
    exit 2
  fi
fi

if [ "$#" -gt 0 ]; then
  AGENT_ID="$ME" git -c user.name="$ME" -c user.email="$ME@leomusic.os" commit -m "$MSG" -- "$@"
else
  AGENT_ID="$ME" git -c user.name="$ME" -c user.email="$ME@leomusic.os" commit -m "$MSG"
fi
rc=$?
echo "── 이 커밋에 실린 파일 ──"
git -c core.quotepath=false show --name-only --pretty=format: HEAD | grep -v '^$'
exit $rc
