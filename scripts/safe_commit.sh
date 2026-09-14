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
# ★경로는 기본값 그대로이고, **시험을 위해서만** 오버라이드를 연다(2026-09-14).
#   ⛔이 도구는 「거짓 보고」 수리를 했는데 **하드코딩된 cd 때문에 스크래치에서 시험이 안 됐다**
#     — 시험할 수 없는 수리는 「고쳤다」가 아니다(오늘만 도구 수리 다섯 번째).
cd "${AGENT_COMM_REPO:-$HOME/projects/agent-comm}" || exit 1
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

BEFORE=$(git rev-parse HEAD)
if [ "$#" -gt 0 ]; then
  AGENT_ID="$ME" git -c user.name="$ME" -c user.email="$ME@leomusic.os" commit -m "$MSG" -- "$@"
else
  AGENT_ID="$ME" git -c user.name="$ME" -c user.email="$ME@leomusic.os" commit -m "$MSG"
fi
rc=$?
# ★2026-09-14 수리 — 이 표시가 «거짓 보고»를 하고 있었다.
#   ⛔실물: 오늘 10:1x 커밋이 실패했는데 아래 표시는 그대로 돌아 **그 시점 HEAD(남의 커밋)**의
#     파일 2건을 「이 커밋에 실린 파일」로 찍었다 ⇒ 화면만 보면 **내 커밋에 남의 파일이 실린 것**으로
#     읽힌다(어제 실제 사고가 그 모양이었으므로 오독의 대가가 크다).
#   ★rc를 «받아 놓고 쓰지 않은» 것이 원인이다 — 성공 출력은 도달의 증거가 아니다.
#   ⇒ ⑴실패면 아무것도 안 찍는다 ⑵성공이면 HEAD가 «방금 내가 만든» 커밋인지
#     (직전 HEAD와 다른가 · author가 나인가) 확인한 뒤에만 목록을 찍는다.
if [ "$rc" -ne 0 ]; then
  echo "⛔커밋 실패(rc=$rc) — 아무것도 실리지 않았습니다. staged는 그대로입니다." >&2
  exit $rc
fi
NEW=$(git rev-parse HEAD)
NEW_AU=$(git log -1 --format=%an "$NEW")
if [ "$NEW" = "$BEFORE" ]; then
  echo "⛔HEAD가 안 움직였습니다($NEW) — 커밋이 실제로 만들어지지 않았습니다." >&2
  exit 1
fi
if [ "$NEW_AU" != "$ME" ]; then
  echo "⛔HEAD author=$NEW_AU (내가 아님) — 그 사이 남의 커밋이 올라왔습니다. 목록을 찍지 않습니다." >&2
  exit 1
fi
echo "── 이 커밋($NEW · author=$NEW_AU)에 실린 파일 ──"
git -c core.quotepath=false show --name-only --pretty=format: "$NEW" | grep -v '^$'
exit $rc
