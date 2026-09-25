"""종단 점검 — 서버가 떠 있는 상태에서 실행.

  .venv/bin/python mvp/songcard/e2e_test.py [--base http://127.0.0.1:8787] [--audio 파일.mp3]

사연 접수 → (중복 접수 차단) → 비공개 확인 → 파이프라인 단계(가사 발주·수령·생성 발주·접수·오디오·게시)
→ 카드 재생(Range) → 공유 전환 → 재요청 중복 차단 → 샘플 파이프라인 차단 까지 한 번에 본다.
⚠ 오디오는 --audio 로 준 파일을 붙인다(기본=샘플 mp3). 실생성 오디오가 아니면 결과 source 는 live 여도
   «실생성 연동 검증»이 아니라 «경로 검증»이다 — 출력에 그렇게 찍는다.
"""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
ok = fail = 0


def call(base, method, path, body=None, headers=None):
    req = urllib.request.Request(base + path, method=method, headers={"Content-Type": "application/json", **(headers or {})},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read()
            return r.status, data, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1
    print(("✅" if cond else "❌"), name, extra)


def pipe(*args):
    r = subprocess.run([PY, str(HERE / "pipeline.py"), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8787")
    ap.add_argument("--audio", default=str(HERE.parents[1] / "data/aware/audio/30201_t1.mp3"))
    ap.add_argument("--key", default=None)
    a = ap.parse_args()
    B = a.base
    import secrets
    key = a.key or "e2e-" + secrets.token_hex(6)

    body = {"occasion": "birthday", "recipient": "테스트", "sender": "e2e", "story": "종단 점검용 가상 사연입니다. 실제 인물 아님.",
            "memory": "", "message": "생일 축하해", "genre": "acoustic", "vocal": "female", "client_key": key}
    s1, d1, _ = call(B, "POST", "/api/requests", body)
    s2, d2, _ = call(B, "POST", "/api/requests", body)
    r1, r2 = json.loads(d1), json.loads(d2)
    check("사연 접수 201", s1 == 201, r1.get("request_id"))
    check("같은 client_key 재전송 → 새로 안 만듦", s2 == 200 and r2["request_id"] == r1["request_id"] and r2["created"] is False)
    rid, t, share = r1["request_id"], r1["owner_token"], r1["share_token"]

    s, _, _ = call(B, "GET", f"/api/cards/{share}")
    check("비공개 카드 — 토큰 없으면 404", s == 404)
    s, d, _ = call(B, "GET", f"/api/requests/{rid}?t={t}")
    check("오너 상태 조회", s == 200 and json.loads(d)["status"] == "received")
    s, d, _ = call(B, "POST", "/api/requests", {**body, "story": "짧음", "client_key": key + "x"})
    check("검증 — 짧은 사연 거절", s == 400, json.loads(d)["error"])

    lyr = HERE / "var" / f"{rid}_lyrics.txt"
    lyr.parent.mkdir(exist_ok=True)
    lyr.write_text("(종단 점검용 자리표시 가사 — 실제 가사 아님)\n생일 축하해\n", encoding="utf-8")
    steps = [
        ("lyrics-order", rid),
        ("lyrics-in", rid, "--file", str(lyr), "--by", "e2e-placeholder", "--title", "점검용 노래"),
        ("gen-order", rid),
        ("gen-ack", rid),
        ("audio-in", rid, "--file", a.audio, "--uuid", "e2e-no-uuid", "--select"),
        ("publish", rid),
    ]
    for st in steps:
        rc, out = pipe(*st)
        check(f"pipeline {st[0]}", rc == 0, out.splitlines()[-1] if out else "")
    rc, out = pipe("gen-ack", rid)
    check("상태기계 — 순서 어긴 단계 거절", rc != 0, out.splitlines()[-1])

    s, d, _ = call(B, "GET", f"/api/cards/{share}?t={t}")
    card = json.loads(d)
    check("카드 완성 ready·오디오·가사", s == 200 and card["status"] == "ready" and card["audio"] and card["lyrics"])
    s, d, h = call(B, "GET", card["audio"] + f"?t={t}", headers={"Range": "bytes=0-1023"})
    check("오디오 Range 206", s == 206 and len(d) == 1024, h.get("Content-Range"))
    s, _, _ = call(B, "GET", card["audio"])
    check("비공개 오디오 — 토큰 없으면 404", s == 404)

    s, _, _ = call(B, "POST", f"/api/requests/{rid}/share", {"t": t, "visibility": "link"})
    s2, d2, _ = call(B, "GET", f"/api/cards/{share}")
    check("공유 전환 후 링크만으로 열림", s == 200 and s2 == 200)
    check("공유 카드에 사연·SP·토큰 비노출", all(k not in json.loads(d2) for k in ("story", "sp", "owner_token")))

    s1, d1, _ = call(B, "POST", f"/api/requests/{rid}/redo", {"t": t, "what": "lyrics", "note": "2절에 이름", "redo_key": "rk1"})
    s2, d2, _ = call(B, "POST", f"/api/requests/{rid}/redo", {"t": t, "what": "vocal", "note": "다른 키", "redo_key": "rk2"})
    check("재요청 접수", s1 == 201)
    check("열린 재요청 있으면 두 번째는 새로 안 만듦", s2 == 200 and json.loads(d2)["created"] is False)

    samples = json.loads(call(B, "GET", "/api/samples")[1])
    check("샘플 카드 3종", len(samples) >= 3 and all(x["source"] == "sample" and x["sample_note"] for x in samples))
    rc, out = pipe("gen-order", samples[0]["request_id"])
    check("샘플은 실생성 파이프라인 차단", rc != 0, out.splitlines()[-1])

    # 점검용 요청이 «실제 제작» 완성 카드로 남지 않게 닫는다
    pipe("fail", rid, "--note", "e2e 점검용 — 실제 제작 아님")
    print(f"\n{ok} 통과 / {fail} 실패 · request_id={rid} (점검 후 failed 로 닫음)")
    print("⚠ 오디오=기존 파일 부착 → «경로 검증»이지 «실생성 연동 검증» 아님")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
