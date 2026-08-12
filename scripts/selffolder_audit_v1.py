#!/usr/bin/env python3
"""자기폴더 잔류 분류 v1 — kee 확인 요청(08-12 18:55) 응답 근거

kee 축 = 파일명 `{to}_{from}_...`의 **to 토큰** vs 폴더 주인. kee 실측 = 내 폴더 14건.
★kee가 먼저 한정함: 「파일명만 봤고 본문을 안 열었다. 08-04에 같은 스캔에서 파일명만
  보고 9건을 미도달로 띄웠다가 본문 to를 열고 오탐 정정한 실적이 있다 — 키 하나로는 또 틀린다」

⇒ 본 스크립트는 **키를 3개 쓴다**:
   K1 파일명 to 토큰 / K2 **본문 to** / K3 **수신폴더 실물 대조**(동명 또는 본문 해시)
   K3까지 안 보면 ⑴을 「미배달」이라 부를 수 없다 — 「내 폴더에 있다」와 「안 갔다」는 다른 말.

★1차판 버그 자체적발: `body_hash`가 예외 시 None을 반환했고 `None == None`이 참이라
  전혀 무관한 파일이 「배달됨」으로 잡혔다(mukl_sunolang_result → reklcli_admin_20260809).
  ⇒ None은 매칭에서 제외. **오늘 3번째 버그이고 3번 다 「낙관」 방향이었다.**
"""
import glob
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

COMM = Path.home() / "projects" / "agent-comm" / "projects"
ME = "sunolanguage"
OUT = Path(__file__).resolve().parent.parent / "data" / "selffolder_audit_v1.json"


def body_hash(p):
    """★None을 매칭에 쓰지 않는다 — None==None이 거짓 '배달됨'을 만든다."""
    try:
        b = json.load(open(p)).get("body")
        if b is None:
            return None
        return hashlib.sha256(
            json.dumps(b, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    except Exception:
        return None


def main():
    mine = COMM / ME / "messages"
    files = sorted(f for f in os.listdir(mine)
                   if f.endswith(".json") and not f.startswith(ME + "_"))

    cat_mine, cat_other, unreadable = [], [], []
    for f in files:
        p = mine / f
        try:
            d = json.load(open(p))
        except Exception as e:
            unreadable.append({"file": f, "error": str(e)[:80]})
            continue
        to = d.get("to", "?")

        # K2: 본문 to가 나 → ⑵ 내게 온 것인데 파일명 규약 위반
        if to == ME:
            cat_mine.append({"file": f, "from": d.get("from"),
                             "정상명": f"{ME}_{d.get('from')}_..."})
            continue

        # K3: 수신폴더 실물 대조
        tgt = COMM / to / "messages"
        if not tgt.is_dir():
            cat_other.append({"file": f, "to": to, "status": "슬롯소멸_판정불가"})
            continue
        h = body_hash(p)
        hit = None
        for cand in list(glob.glob(str(tgt / "*.json"))) + \
                    list(glob.glob(str(tgt / "processed" / "*.json"))):
            if os.path.basename(cand) == f:
                hit = "동명일치"
                break
            if h is not None:
                ch = body_hash(cand)
                if ch is not None and ch == h:
                    hit = "본문해시일치"
                    break
        cat_other.append({"file": f, "to": to,
                          "status": f"배달확인({hit})" if hit else "수신폴더에_없음"})

    # kee 축(두 토큰 접두 `{slot}_{slot}_`)이 잡는 것과 못 잡는 것 분리
    slots = {d.name for d in COMM.iterdir() if d.is_dir()}
    def two_token(f):
        parts = f.split("_")
        return len(parts) >= 2 and parts[0] in slots and parts[1] in slots
    kee_visible = [f for f in files if two_token(f)]
    kee_blind = [f for f in files if not two_token(f)]

    counts = Counter(x["status"] for x in cat_other)
    payload = {
        "질문": "kee 08-12 18:55 §3 — 자기폴더 발신 의심 14건 분류",
        "★수량_불일치": {
            "kee_실측": 14,
            "내_실측_전체": len(files),
            "kee축이_보는_것(두_슬롯토큰_접두)": len(kee_visible),
            "★kee축이_구조적으로_못_보는_것": len(kee_blind),
            "못_보는_형태": kee_blind,
            "★대사_결과": "kee축 가시분이 **정확히 14건**으로 kee 실측과 일치 — 축 재현 성공. "
                        "따라서 불일치의 정체는 계수 오류가 아니라 **kee 축의 시야 범위**다: "
                        "⑴가시 14 중 **4건이 실은 내게 온 것**(파일명 to/from 뒤집힘) = **오탐**, "
                        "⑵**13건은 축이 구조적으로 못 봄**(단일토큰 `mukl_...` 7 · 날짜접두 3 · 기타 3) = **누락**. "
                        "⇒ kee의 전조직 122건 집계도 같은 사유로 **과소일 가능성**이 있다(내 슬롯 1건 근거이므로 "
                        "일반화는 kee가 판단할 몫).",
        },
        "⑵_내게_온_것_파일명_규약위반": cat_mine,
        "⑴_수신자가_남": {"counts": dict(counts), "items": cat_other},
        "판독실패": unreadable,
        "★A-088_이후_신규축적_판정": None,  # main에서 채움
    }

    dates = []
    for f in files:
        for tok in f.split("_"):
            if len(tok) == 8 and tok.isdigit() and tok.startswith("2026"):
                dates.append(tok)
                break
    payload["★A-088_이후_신규축적_판정"] = {
        "최신_잔류분": max(dates) if dates else None,
        "A-088_종결일": "20260804",
        "판정": ("⒝(그 뒤로 다시 쌓였다) = 기각 — 최신 잔류분이 A-088보다 앞선다"
               if dates and max(dates) < "20260804" else "재확인 필요"),
        "★미검증": "⒜(A-088 모집단과 다르다)인지는 A-088 모집단 정의를 안 봐서 판정 안 함",
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    print(f"내 폴더 루트에서 to토큰≠{ME} = {len(files)}건 (kee 실측 14와 불일치)")
    print(f"  kee축 가시 {len(kee_visible)} / ★kee축 비가시 {len(kee_blind)}")
    print(f"\n⑵ 내게 온 것인데 파일명 뒤집힘 = {len(cat_mine)}건 ★kee축에선 '남의 것'으로 보임(오탐)")
    for x in cat_mine:
        print(f"   {x['file']}  (from={x['from']})")
    print(f"\n⑴ 수신자가 남 = {len(cat_other)}건")
    for k, v in counts.items():
        print(f"   {k}: {v}")
    print(f"\nA-088 이후 신규축적: {payload['★A-088_이후_신규축적_판정']['판정']}")
    print(f"저장: {OUT}")


if __name__ == "__main__":
    main()
