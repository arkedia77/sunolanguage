#!/usr/bin/env python3
"""인박스 미처리 스캐너 — ★컷오프를 사람이 눈대중으로 정하지 않게 한다.

왜 만드나(2026-08-09 실사고):
  fableself 통지가 22:57:09에 왔는데 내가 스캔 컷오프를 `>= 08-07T23:00`으로 잡아 **3분 차로 놓쳤다.**
  컷오프를 「방금 통지받은 메시지 시각」에서 눈대중으로 뽑은 것이 원인이다.
  그 상태로 오너에게 **「신규 수신 없음」이라고 보고**했다 — 없음이 아니라 **안 본 것**이었다.
  ★내 상시 규율이 「「없음」과 「안 봄」을 구분해 기재한다」인데 내가 어겼다.

설계(=`send_msg.py`와 같은 사상: 규율이 아니라 경로를 막는다):
  ⑴ **컷오프를 인자로 받지 않는다.** 워터마크는 `processed/`의 최신 created_at에서 **기계가 뽑는다.**
  ⑵ 루트 잔류 전건을 훑고 **워터마크 이후**를 미처리로 낸다. 역사적 잔류(워터마크 이전)는 따로 센다.
  ⑶ 시각 필드가 없거나 파싱 안 되는 건은 ★**버리지 않고 `unparsed`로 올린다**
     (「판정 불가」를 「없음」으로 접으면 이 스크립트가 만든 사고가 원래 사고와 같아진다).

사용:
  python3 scripts/inbox_scan.py          미처리 목록
  python3 scripts/inbox_scan.py --all    역사적 잔류까지 요약
"""
import json
import sys
from pathlib import Path

ME = "sunolanguage"
BOX = Path("/Users/purple/projects/agent-comm/projects") / ME / "messages"


def stamp(d, path):
    """created_at·sent_at·timestamp 중 있는 것. 없으면 파일명 stamp(YYYYMMDD_HHMMSS)로 폴백."""
    for k in ("created_at", "sent_at", "timestamp"):
        v = d.get(k)
        if isinstance(v, str) and len(v) >= 16:
            return v[:19].replace(" ", "T"), k
    parts = path.name.split("_")
    for i, p in enumerate(parts):
        if len(p) == 8 and p.isdigit() and i + 1 < len(parts) and parts[i + 1][:6].isdigit():
            t = parts[i + 1][:6]
            return f"{p[:4]}-{p[4:6]}-{p[6:]}T{t[:2]}:{t[2:4]}:{t[4:]}", "filename"
    return None, None


def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        return {"__error__": str(e)}


def main():
    proc = BOX / "processed"
    # ⑴ 워터마크 = 처리분 중 최신 시각. 사람이 정하지 않는다.
    marks = []
    for p in proc.glob("*.json"):
        d = load(p)
        s, _ = stamp(d, p)
        if s:
            marks.append(s)
    watermark = max(marks) if marks else ""

    new, old, unparsed = [], [], []
    for p in sorted(BOX.glob("*.json")):
        d = load(p)
        if "__error__" in d:
            unparsed.append((p.name, d["__error__"]))
            continue
        s, src = stamp(d, p)
        if not s:
            unparsed.append((p.name, "시각 필드·파일명 stamp 모두 없음"))
            continue
        row = (s, d.get("from", "?"), str(d.get("reply_needed")), src, p.name)
        (new if s > watermark else old).append(row)

    print(f"워터마크(처리분 최신) = {watermark or '(없음)'}   ※기계 산출, 인자 아님")
    print(f"루트 잔류 {len(new)+len(old)+len(unparsed)} = 미처리 {len(new)} / "
          f"워터마크 이전 {len(old)} / ★판정불가 {len(unparsed)}")
    if new:
        print("\n■ 미처리 (워터마크 이후)")
        for s, f, r, src, n in sorted(new):
            print(f"  {s}  from={f:<14} reply={r:<5} [{src}]\n     {n[:100]}")
    else:
        print("\n■ 미처리 0건 — ★워터마크 이후 기준. 이전 잔류는 위 카운트 참조(‘없음’ 아님)")
    if unparsed:
        print("\n■ ★판정 불가 — 버리지 않고 올림 (직접 확인 필요)")
        for n, why in unparsed:
            print(f"  {n[:90]}  ← {why}")
    if "--all" in sys.argv and old:
        print(f"\n■ 워터마크 이전 잔류 {len(old)}건 (역사적 미이관분, 최근 10)")
        for s, f, r, src, n in sorted(old, reverse=True)[:10]:
            print(f"  {s}  from={f:<14} {n[:80]}")


if __name__ == "__main__":
    main()
