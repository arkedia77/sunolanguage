#!/usr/bin/env python3
"""VTT 자막 판독기 — 롤링 중복 제거 + 구간 추출.

★배경: 유튜브 자막은 지난 조사에서 「전량 0건」이었다. 원인은 캡션 부재가 아니라
서명 URL이 IP 바인딩이라 직접 GET이 0바이트를 반환한 것 — 즉 **「없음」이 아니라 「안 봄」**이었다.
yt-dlp로 정상 회수되므로, 그때의 0은 재실행 전까지 **미측정**으로 취급한다.

사용: python3 scripts/vtt_read.py <vtt경로> [시작초] [끝초]
      python3 scripts/vtt_read.py <vtt경로> --grep <정규식>
"""
import re
import sys

CUE = re.compile(r"(\d\d):(\d\d):(\d\d)\.\d+ -->")
TAG = re.compile(r"<[^>]+>")


def parse(path):
    """(초, 텍스트) 목록. 자동자막의 롤링 중복은 직전 줄과 같으면 버린다."""
    cues, last = [], None
    with open(path, encoding="utf-8") as fh:
        blocks = fh.read().split("\n\n")
    for blk in blocks:
        m = CUE.search(blk)
        if not m:
            continue
        sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        body = " ".join(l for l in blk.split("\n")[1:]
                        if l.strip() and "-->" not in l)
        body = TAG.sub("", body).strip()
        if body and body != last:
            cues.append((sec, body))
            last = body
    return cues


def fmt(sec):
    return f"{sec // 60}:{sec % 60:02d}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cues = parse(sys.argv[1])
    if not cues:
        print("★자막 0줄 — 파싱 실패이지 「자막 없음」이 아니다. 파일을 직접 확인할 것.")
        return 2
    print(f"# 자막 {len(cues)}줄 · 총 {fmt(cues[-1][0])}")
    args = sys.argv[2:]
    if args and args[0] == "--grep":
        pat = re.compile(args[1], re.I)
        hit = [(t, x) for t, x in cues if pat.search(x)]
        print(f"# ★스캔 성공 · 히트 {len(hit)}줄 (0이면 「스캔 실패」가 아니라 「히트 없음」)")
        for t, x in hit:
            print(f"{fmt(t)}  {x}")
        return 0
    lo = int(args[0]) if len(args) > 0 else 0
    hi = int(args[1]) if len(args) > 1 else 10 ** 9
    for t, x in cues:
        if lo <= t <= hi:
            print(f"{fmt(t)}  {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
