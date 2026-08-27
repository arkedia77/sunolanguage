#!/usr/bin/env python3
"""agent-comm 메시지 발신기 — ★시각은 시스템 시계에서만 만든다.

표준: ARI ⓐ「발신 시각 = 기계 생성 강제」(온보딩 표준 §4, kee 발효 08-03).
규칙: `created_at`·파일명 스탬프를 **now 1회 호출**에서 파생하고 **인자로 받지 않는다.**

배경(실피해 2건):
  ⑴kee 08-02 손기재 +97분·날짜 하루 앞섬 → sunolanguage가 지시 선후를 오독해 작업 정지
  ⑵sunolanguage 08-04 손기재 +155분(자칭 15:30 / 실제 12:55) — kee 적발

부수 규약(같은 날 실증분):
  - 경로: `projects/{to}/messages/{to}_{from}_{stamp}_{키워드}.json`  ★받는 쪽 폴더(A-078)
  - 발신 후 `git show origin/main:{경로}` 로 **push 후 실물 확인**(A-088)
  - `git add -A` 금지 — 공유 작업 트리라 남의 미커밋 파일을 담는다

사용:
  python3 scripts/send_msg.py <to> <키워드> <body.json경로> [--subject "..."] [--reply-needed]
"""
import json, os, re, sys
from datetime import datetime

FROM = "sunolanguage"
ROOT = "/Users/purple/projects/agent-comm"


def _body_hash(body):
    """★발신 검증은 「내가 떠올린 문구가 있나」로 하지 않는다 — 그 방식이 2026-08-11 하루에만
    거짓음성 2건을 냈다(`안 잰 것`↔`안_잰_것`, `도달 임계`↔`임계 분량`).
    검색어를 내가 짓는 한 못 찾은 것과 없는 것이 계속 섞인다. → **본문 해시 대조**로 바꾼다.
    사용: 발신 시 찍힌 해시와, push 후 origin 본문의 해시가 같은지만 본다."""
    import hashlib
    return hashlib.sha256(json.dumps(body, ensure_ascii=False,
                                     sort_keys=True).encode()).hexdigest()[:16]


def _schema_version():
    """★판번호는 손으로 적지 않는다 — 정본(CHANNEL_RULES.md 1행)에서 발신 시점에 읽는다.

    실피해: 이 파일이 `v5.5`를 하드코딩하고 있었고 실측은 `v5.11`이었다(6개정 스테일).
    ⇒ 내가 보낸 모든 메시지가 틀린 판번호를 달고 나갔다. kee 08-12 §1 부수건과 동형이며,
    「존재하고, 파싱되고, 내용만 다르다」는 가장 조용한 파손이다(킷 R-P6 ⓕ).

    ★못 읽으면 옛값으로 조용히 떨어지지 않고 **발신을 멈춘다** — 그 폴백이 곧 이 결함이다.
    """
    src = os.path.join(ROOT, "CHANNEL_RULES.md")
    with open(src, encoding="utf-8") as fh:
        head = fh.readline()
    m = re.search(r"\bv\d+\.\d+\b", head)
    if not m:
        raise SystemExit(f"발신 중단 — {src} 1행에서 판번호를 못 읽었다: {head!r}\n"
                         "★임의 값으로 채우지 않는다. 정본 형식이 바뀌었으면 이 함수를 고칠 것.")
    return m.group(0)


def _reject_envelope(body, bodyfile):
    """★body 파일에 봉투 키를 넣으면 body가 이중 중첩된다 — 2026-08-27 실피해 6건.

    발신기는 body 파일을 **본문 그대로** 싣는다(`msg["body"] = body`). 그런데 내가
    `{"type":..,"priority":..,"body":{..}}` 형태로 넣어서 `body.body.*`가 됐고,
    받는 쪽이 기대하는 `body.0_한줄` 경로가 통째로 비었다. `type`도 전부 기본값
    `report`로 나갔다(내가 넣은 `reply`/`request`/`notice`는 안쪽에 묻혔다).

    ★「존재하고, 파싱되고, 내용만 다르다」 계열이라 **발신 성공이 근거가 안 된다.**
    경고가 아니라 **거부**다 — 경고면 내가 무시한다(A-068 cc 가드와 같은 사상).
    """
    if not isinstance(body, dict):
        return
    ENV = {"type", "priority", "status", "action_required", "schema_version",
           "from", "to", "created_at", "subject", "reply_needed"}
    hit = ENV & set(body)
    if "body" in body and hit:
        raise SystemExit(
            f"\n[send_msg] ❌ 거부 — body 파일이 **봉투 형태**입니다: {bodyfile}\n"
            f"  발견한 봉투 키: {sorted(hit)} + 'body'\n"
            "  ★이대로 보내면 `body.body.*`로 이중 중첩되고, 받는 쪽이 보는 `body.0_한줄`은 **빈 값**이 됩니다.\n"
            "  처리: body 파일에는 **본문만** 넣으십시오(`{\"0_한줄\": ..., \"1_...\": ...}`).\n"
            "   ⑴`type`/`priority`는 이 발신기가 정합니다(type=report 고정 · priority=P2).\n"
            "   ⑵회신 요구는 `--reply-needed` 플래그로.\n"
            "  ★우회 옵션 없습니다.\n")

def send(to, keyword, body, subject, reply_needed=False, priority="P2", msg_type="report"):
    now = datetime.now().astimezone()          # ★단 1회 호출 — 여기서만 시각이 나온다
    stamp = now.strftime("%Y%m%d_%H%M%S")
    msg = {
        "schema_version": _schema_version(), "from": FROM, "to": to, "type": msg_type,
        "status": "open", "priority": priority,
        "action_required": bool(reply_needed),
        "created_at": now.isoformat(),          # ★파일명과 동일 now에서 파생
        "subject": subject, "body": body,
        "reply_needed": bool(reply_needed),
        "timestamp_source": "scripts/send_msg.py — datetime.now().astimezone() 1회 호출로 created_at·파일명 동시 파생(손기재 불가)",
    }
    rel = f"projects/{to}/messages/{to}_{FROM}_{stamp}_{keyword}.json"
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(msg, open(path, "w"), ensure_ascii=False, indent=1)
    print(f"WROTE  {rel}")
    print(f"       body_sha256[:16]={_body_hash(body)}  ★push 후 origin 본문 해시와 대조할 것")
    print(f"       created_at={msg['created_at']}  (파일명 stamp={stamp} — 동일 now)")
    print(f"NEXT   git add \"{rel}\" && commit && push && git show origin/main:\"{rel}\" >/dev/null")
    return rel


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 3:
        print(__doc__); sys.exit(1)
    to, keyword, bodyfile = a[0], a[1], a[2]
    subject = a[a.index("--subject") + 1] if "--subject" in a else f"[{FROM}→{to}] {keyword}"
    _body = json.load(open(bodyfile))
    _reject_envelope(_body, bodyfile)
    send(to, keyword, _body, subject, "--reply-needed" in a)
