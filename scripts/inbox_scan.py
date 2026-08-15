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
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ME = "sunolanguage"
BOX = Path("/Users/purple/projects/agent-comm/projects") / ME / "messages"
REPO = Path("/Users/purple/projects/agent-comm")


# ─────────────────────────────────────────────────────────────
# git 도착 시각 (2026-08-15 추가) — ★판정축에서 「남이 쓴 값」을 뺀다
#
# 왜: 08-13에 「내 판정이 남이 쓴 값에 의존하면 남의 손기재가 곧 내 실명이다」를 룰로 적어 놓고,
#   워터마크는 여전히 발신자의 `created_at`에서 뽑고 있었다. 그때 붙인 방어 ⑴「미래 시각 제외」는
#   ★**시한부였다** — 실제 시간이 그 가짜 시각을 지나가면 미래가 아니게 되어 워터마크로 채택된다.
#   실측(08-15): leomusic-trot이 자인한 손 외삽 +45분 값(`00:40`, 실제 커밋 08-14 23:55)이
#   다음 날 스캔에서 **정상 워터마크로 승격**돼 있었다. (이번엔 그 구간 도착분이 0건이라 실피해는 없었다 —
#   ★막은 것은 방어 ⑴이 아니라 방어 ⑵ 해시 원장이다.)
#
# ⇒ 워터마크를 **git 도착 시각**(해당 경로의 최초 커밋 시각)에서 뽑는다. 이 값은 발신자가 못 쓴다.
#   `created_at`은 **자기신고값**으로 화면에만 남기고, 둘이 크게 어긋나면 드리프트로 표시한다.
def git_arrivals():
    """basename → 최초 커밋 시각(ISO). 실패하면 빈 dict(폴백=created_at)."""
    try:
        out = subprocess.run(
            # ★`core.quotepath=false` 필수 — 한글·★ 파일명이 8진 이스케이프로 나와
            #   basename이 안 맞고 **조용히 폴백**한다(첫 판에서 실제로 그랬다. 화면엔 「git 도착」이
            #   찍히는데 값은 자기신고였다 = 라벨이 거짓말을 함).
            ["git", "-c", "core.quotepath=false", "log", "--diff-filter=A", "--reverse",
             "--date=iso-strict", "--format=@%ad", "--name-only",
             "--", f"projects/{ME}/messages/"],
            cwd=REPO, capture_output=True, text=True, timeout=60, check=True).stdout
    except Exception:
        return {}
    arrivals, cur = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = line[1:20]   # "@2026-08-14T23:54:42+09:00" → 초까지 19자
        elif line.strip() and cur:
            name = line.rsplit("/", 1)[-1]
            arrivals.setdefault(name, cur)   # --reverse라 첫 등장이 최초 도착
    return arrivals


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


def abs_min(a, b):
    """두 ISO 시각(초 단위 문자열)의 차이를 분으로. 파싱 실패는 0(=드리프트 아님)으로 접는다."""
    try:
        ta = datetime.fromisoformat(a[:19])
        tb = datetime.fromisoformat(b[:19])
    except Exception:
        return 0
    return int(abs((ta - tb).total_seconds()) // 60)


def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        return {"__error__": str(e)}


# ─────────────────────────────────────────────────────────────
# 해시 원장 (2026-08-11 추가)
#
# 왜: 워터마크는 **「새로 온 것」만 잡고 「바뀐 것」은 못 잡는다.**
#   루트 잔류 395건·processed 90건 중 누가 수정돼도 이 스캐너는 지금 침묵한다.
#   agent-comm은 공유 클론이라 같은 파일명으로 갱신 push가 원리적으로 가능하다(G-K5 race).
#
# ★단, 붙이기 전에 재봤다 — **현 데이터에서 해시로 잡히는 건 0건이다**:
#   ⓐ루트 내 내용 중복 0 ⓑ루트↔processed 동일 내용 0
#   ⓒ`git log --name-only` 실측 = 수신함 파일 전건 **커밋 1회 = 생성 후 수정 이력 0건**
#   ⇒ 이건 **회고 탐지 장치가 아니라 앞으로의 변경을 잡는 장치**다. 실적 0을 실적으로 적지 않는다.
#
# ★첫 실행은 「변경 없음」이 아니라 **「기준선 생성 — 이번엔 변경 탐지 안 함」**으로 낸다.
#   비교 대상이 없는 것을 「없음」으로 접으면 send_msg·컷오프에서 낸 오류형을 여기서 재현한다.
# ─────────────────────────────────────────────────────────────
LEDGER = Path(__file__).resolve().parent.parent / "data" / "inbox_hash_ledger.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def hash_audit(box):
    """현재 스냅샷을 원장과 대조. (보고줄 리스트, 새 스냅샷) 반환."""
    snap = {}
    for p in box.glob("*.json"):
        snap[p.name] = {"h": sha(p), "loc": "root"}
    for p in (box / "processed").glob("*.json"):
        snap[p.name] = {"h": sha(p), "loc": "processed"}

    if not LEDGER.exists():
        return (["★기준선 생성 — 원장이 없어 **이번 실행은 변경 탐지를 하지 않았다**",
                 f"  (「변경 없음」이 아니라 「아직 못 봄」. 다음 실행부터 {len(snap)}건 대조)"],
                snap, set())

    prev = json.loads(LEDGER.read_text())
    lines, changed, moved, moved_dirty, gone, added = [], [], [], [], [], []
    for name, cur in snap.items():
        old = prev.get(name)
        if old is None:
            added.append(name)
        elif old["h"] != cur["h"]:
            (moved_dirty if old["loc"] != cur["loc"] else changed).append(name)
        elif old["loc"] != cur["loc"]:
            moved.append(name)
    gone = [n for n in prev if n not in snap]

    if changed:
        lines.append(f"★★내용 변경 {len(changed)}건 — **같은 파일명인데 해시가 다르다. 다시 읽을 것**")
        lines += [f"    {n[:88]}" for n in changed[:10]]
    if moved_dirty:
        lines.append(f"★★이관 중 내용 변경 {len(moved_dirty)}건 — **옮기면서 바뀐 것**")
        lines += [f"    {n[:88]}" for n in moved_dirty[:10]]
    if gone:
        lines.append(f"★소실 {len(gone)}건 — 원장에 있었는데 지금 없다")
        lines += [f"    {n[:88]}" for n in gone[:10]]
    if not (changed or moved_dirty or gone):
        lines.append("변경·소실 0")
    # ★평시 카운트는 이상 유무와 무관하게 **항상** 낸다 — 이상이 있을 때 정상분이 화면에서
    #   사라지면 「몇 건을 대조했는지」를 못 보고, 그 상태의 「0건」은 신뢰할 수 없다.
    lines.append(f"대조 {len(prev)}→{len(snap)}건 · 정상 이관 {len(moved)} · 신규 {len(added)}")
    return lines, snap, {n for n in added if snap[n]["loc"] == "root"}


def main():
    proc = BOX / "processed"

    # ★해시 원장을 **먼저** 본다 — 시각 비의존 축이라 워터마크가 오염돼도 살아남는다.
    #   (08-13 실피해: 아래 「워터마크 오염」 주석 참조)
    lines, snap, fresh = hash_audit(BOX)

    # ⑴ 워터마크 = 처리분 중 최신 시각. 사람이 정하지 않는다.
    # ★단 **미래 시각은 워터마크로 안 쓴다** (08-13 실피해 1건) —
    #   발신자가 `created_at`을 손기재하면 미래 시각이 들어오고, 그걸 이관하는 순간
    #   내 워터마크가 그 미래로 점프해 **그 사이에 온 정상 메시지가 통째로 「워터마크 이전」으로 묻힌다.**
    #   실측: leomusic2가 11:16 커밋분에 `created_at=12:30`(+80분 미래)을 적었고,
    #   그 뒤 도착한 leomusic 11:23·leomusic3 11:27 **제출 2건이 「미처리 0」으로 찍혔다.**
    #   ⇒ 이 스캐너가 막으려던 사고(08-09 컷오프 눈대중)를 **다른 입구로 재현**했다.
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    arrivals = git_arrivals()

    def axis(name, selfstamp):
        """판정에 쓰는 시각 = git 도착 시각 우선, 없으면 자기신고 폴백."""
        return arrivals.get(name) or selfstamp

    marks, future, drift = [], [], []
    for p in proc.glob("*.json"):
        d = load(p)
        s, _ = stamp(d, p)
        if not s:
            continue
        g = arrivals.get(p.name)
        if g and s > g and abs_min(s, g) >= 10:
            drift.append((s, g, p.name))
        t = axis(p.name, s)
        (future if t > now else marks).append((t, p.name))
    watermark = max(m[0] for m in marks) if marks else ""

    new, old, unparsed = [], [], []
    for p in sorted(BOX.glob("*.json")):
        d = load(p)
        if "__error__" in d:
            unparsed.append((p.name, d["__error__"]))
            continue
        s, src = stamp(d, p)
        if not s and p.name not in arrivals:
            unparsed.append((p.name, "시각 필드·파일명 stamp 모두 없음"))
            continue
        g = arrivals.get(p.name)
        if s and g and s > g and abs_min(s, g) >= 10:
            drift.append((s, g, p.name))
        t = axis(p.name, s)
        row = (t, d.get("from", "?"), str(d.get("reply_needed")),
               ("git" if g else src), p.name)
        # ★원장에 없던 파일(=신규)은 **시각과 무관하게** 미처리로 올린다.
        #   시각 축 하나로만 판정하면 그 축이 오염될 때 통째로 눈이 먼다.
        (new if (t > watermark or p.name in fresh) else old).append(row)

    # ★커버리지를 같이 낸다 — 「git 도착」이라고 찍어 놓고 실제로는 폴백인 상태를 못 보면
    #   그 라벨이 거짓말이 된다(첫 판에서 quotepath 이스케이프로 전건 폴백했는데 라벨은 git이었다).
    total_files = len(list(BOX.glob("*.json"))) + len(list(proc.glob("*.json")))
    hit = sum(1 for p in list(BOX.glob("*.json")) + list(proc.glob("*.json"))
              if p.name in arrivals)
    src_label = f"git 도착 {hit}/{total_files}건" + ("" if hit else " ★전건 폴백=자기신고")
    print(f"워터마크(처리분 최신·{src_label}) = {watermark or '(없음)'}   ※기계 산출, 인자 아님")
    if future:
        print(f"★★미래 시각 {len(future)}건 — 워터마크에서 제외함 (지금={now})")
        for s, n in sorted(future, reverse=True)[:5]:
            print(f"    {s}  {n[:80]}")
    if drift:
        # ★발신자 자기신고와 실제 도착이 10분 이상 어긋난 건. 판정엔 안 쓰지만 **보이게** 둔다 —
        #   채널 차원의 손기재 재발을 여기서 먼저 본다(08-13 leomusic2 +80분·08-15 leomusic-trot +45분).
        # ★방향을 건다: **자기신고 > 실제도착**(=미래로 앞당겨 적음)만 센다.
        #   반대 방향(작성 후 나중에 커밋)은 정상이고 실제로 130건이나 되어, 방향을 안 걸면
        #   경보가 노이즈에 묻힌다(첫 판에서 실측). 워터마크를 오염시키는 건 앞당긴 쪽뿐이다.
        # 총건수는 **항상** 낸다. 다만 열거는 최근 14일분만 — 역사분(대부분)이 매 스캔 화면을
        # 덮으면 오늘의 신호가 그 안에 묻힌다. 「0건」이 아니라 「역사분」이라고 적는다.
        cut = (datetime.now().astimezone() - timedelta(days=14)).isoformat(timespec="seconds")
        recent = [d for d in drift if d[1] >= cut]
        print(f"★자기신고가 실제 도착보다 앞선 건 {len(drift)}건 (≥10분) — 판정은 git 도착 시각으로 함"
              f" · 최근 14일 {len(recent)}건")
        for s, g, n in sorted(recent or [], key=lambda x: -abs_min(x[0], x[1]))[:5]:
            print(f"    자기신고 {s} / 실제도착 {g}  (Δ{abs_min(s, g)}분)  {n[:60]}")
        if not recent:
            print("    (열거 없음 = 최근 14일 0건. 나머지는 역사분 — ★「없음」 아님)")
    print(f"루트 잔류 {len(new)+len(old)+len(unparsed)} = 미처리 {len(new)} / "
          f"워터마크 이전 {len(old)} / ★판정불가 {len(unparsed)}")
    if new:
        print("\n■ 미처리 (워터마크 이후 ∪ ★원장 신규)")
        for s, f, r, src, n in sorted(new):
            tag = " ★신규(원장)" if n in fresh else ""
            print(f"  {s}  from={f:<14} reply={r:<5} [{src}]{tag}\n     {n[:100]}")
    else:
        print("\n■ 미처리 0건 — ★워터마크 이후 ∪ 원장 신규 기준. 이전 잔류는 위 카운트 참조(‘없음’ 아님)")
    if unparsed:
        print("\n■ ★판정 불가 — 버리지 않고 올림 (직접 확인 필요)")
        for n, why in unparsed:
            print(f"  {n[:90]}  ← {why}")
    if "--all" in sys.argv and old:
        print(f"\n■ 워터마크 이전 잔류 {len(old)}건 (역사적 미이관분, 최근 10)")
        for s, f, r, src, n in sorted(old, reverse=True)[:10]:
            print(f"  {s}  from={f:<14} {n[:80]}")

    # ★해시 대조 결과 출력 (산출은 위에서 이미 했다)
    print("\n■ 해시 대조 (워터마크는 '새 것'만 본다 — 여기는 '바뀐 것'을 본다)")
    for l in lines:
        print(f"  {l}")
    if "--no-write" not in sys.argv:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(snap, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
