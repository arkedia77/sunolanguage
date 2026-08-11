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
import json, os, sys
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


def send(to, keyword, body, subject, reply_needed=False, priority="P2", msg_type="report"):
    now = datetime.now().astimezone()          # ★단 1회 호출 — 여기서만 시각이 나온다
    stamp = now.strftime("%Y%m%d_%H%M%S")
    msg = {
        "schema_version": "v5.5", "from": FROM, "to": to, "type": msg_type,
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
    send(to, keyword, json.load(open(bodyfile)), subject, "--reply-needed" in a)
