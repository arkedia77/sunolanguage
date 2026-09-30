"""배포 묶음 만들기 — leoserver(admin)에 넘길 폴더/tar 를 뜬다.

  .venv/bin/python mvp/songcard/make_bundle.py [--out var/bundle] [--tar]

무엇이 들어가나
  server.py · store.py · sp_builder.py · templates.py · pipeline.py · export_card.py · static/
  + `sp_presets.json`(96조합) — ★이것 덕분에 **코퍼스 DB(sunolang.db)를 안 올린다**.

⛔들어가지 않는 것: `sunolang.db` · `var/`(고객 사연·오디오) · `seed_samples.py`·`e2e_test.py`
   (샘플 시드는 내부 음원 경로를 참조하고, 점검기는 서버를 띄운다 — 공개 호스트에 둘 물건이 아니다)

★묶은 뒤 **DB 없이 실제로 뜨는지** 스스로 확인한다(`--check`, 기본 켜짐):
  임시 위치로 복사해 기동 → `/api/options` 200 · 접수(초대 코드) 201 까지 본다.
  ⛔이 확인을 건너뛰면 「DB 불요」는 **말뿐**이 된다 — 09-30 admin 에 그렇게 약속했다.
"""
import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
FILES = ["server.py", "store.py", "sp_builder.py", "templates.py", "pipeline.py",
         "export_card.py", "sp_presets.json"]
DIRS = ["static"]


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def build(out: Path) -> Path:
    if not (HERE / "sp_presets.json").is_file():
        sys.exit("⛔ sp_presets.json 이 없습니다 — 먼저 `sp_builder.py --emit` (DB 있는 곳에서)")
    rc = subprocess.run([PY, str(HERE / "sp_builder.py"), "--verify"]).returncode
    if rc != 0:
        sys.exit("⛔ 프리셋이 DB 재계산과 다릅니다 — 묶지 않습니다(자가 두 벌)")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in FILES:
        shutil.copy2(HERE / f, out / f)
    for d in DIRS:
        shutil.copytree(HERE / d, out / d)
    (out / "RUN.md").write_text(RUN_MD, encoding="utf-8")
    return out


def check(bundle: Path) -> bool:
    """★DB 가 절대 안 닿는 곳에 복사해 띄운다 — 리포 밖 임시 디렉터리."""
    with tempfile.TemporaryDirectory() as td:
        app = Path(td) / "songcard"
        shutil.copytree(bundle, app)
        db_would_be = app.resolve().parents[1] / "sunolang.db"
        print(f"  DB 가 있었을 자리: {db_would_be} — 존재? {db_would_be.exists()}")
        if db_would_be.exists():
            print("  ⚠이 임시 위치에 DB 가 있습니다 — 확인이 무의미하므로 중단")
            return False
        port = _free_port()
        p = subprocess.Popen([PY, str(app / "server.py"), "--port", str(port), "--invite", "chk"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             env={**os.environ, "SONGCARD_VAR": str(Path(td) / "var")})
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(60):
                try:
                    urllib.request.urlopen(base + "/api/options", timeout=1)
                    break
                except Exception:
                    time.sleep(0.1)
            opts = json.loads(urllib.request.urlopen(base + "/api/options", timeout=5).read())
            ok_opt = len(opts["occasions"]) == 12
            body = {"occasion": "birthday", "recipient": "묶음점검", "relation": "친구", "sender": "",
                    "story": "묶음 확인용 가상 사연입니다. 실제 인물 아님.", "memory": "", "message": "",
                    "genre": "ballad", "vocal": "female", "invite": "chk",
                    "client_key": "bundle-check-0001"}
            req = urllib.request.Request(base + "/api/requests", method="POST",
                                         headers={"Content-Type": "application/json"},
                                         data=json.dumps(body).encode())
            with urllib.request.urlopen(req, timeout=5) as r:
                created = r.status == 201
                rid = json.loads(r.read())["request_id"]
            sp = json.loads((Path(td) / "var" / "songcard_store.json").read_text())["requests"][rid]["sp"]
            from_presets = sp.get("from_presets") is True
            print(f"  ✅ DB 없이 기동 · 템플릿 {len(opts['occasions'])}종 · 접수 201={created} · SP=프리셋 경로={from_presets}")
            return ok_opt and created and from_presets
        except Exception as e:
            out = ""
            try:
                p.terminate()
                out = p.communicate(timeout=5)[0]
            except Exception:
                pass
            print(f"  ❌ 확인 실패: {e}\n{out}")
            return False
        finally:
            if p.poll() is None:
                p.terminate()
                p.wait(timeout=10)


RUN_MD = """# songcard — leoserver 구동 안내 (sunolanguage → admin)

의존성 **없음**(시스템 python3 표준 라이브러리만). 코퍼스 DB 불요 — `sp_presets.json` 동봉.

    python3 server.py --base /<접두> --host 127.0.0.1 --port 8787 \\
            --invite <초대코드> [--invite <또다른코드>] --daily-limit 5

- `--invite` 를 **하나도 안 주면 접수가 전부 막힙니다**(fail-closed — 설정 누락이 공개 구멍이 되지 않게).
- 저장 위치를 옮기려면 `SONGCARD_VAR=/경로` (기본=이 폴더의 `var/`).
  ⚠`var/` 에는 **고객 사연 원문**이 들어갑니다 — 외부 백업·로그 수집 대상에서 빼 주십시오.
- 앱이 직접 붙이는 헤더: 전 응답 `X-Robots-Tag: noindex, nofollow` · `Cache-Control: no-store` ·
  `/robots.txt` 전체 Disallow. 프록시에서 `/api/*` 는 캐시하지 말아 주십시오(상태 폴링 5초).
- 프록시가 접두를 떼든 붙인 채 넘기든 **둘 다 받습니다**.
- 필요 메서드 GET·POST뿐(업로드·WebSocket·SSE 없음). 오디오는 Range 206 지원.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE / "var" / "bundle"))
    ap.add_argument("--tar", action="store_true", help="tar.gz 로도 뜬다")
    ap.add_argument("--no-check", action="store_true", help="⛔DB 없이 뜨는지 확인을 건너뛴다")
    a = ap.parse_args()
    out = build(Path(a.out))
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"묶음 {out} — 파일 {sum(1 for f in out.rglob('*') if f.is_file())}개 · {size:,}바이트")
    ok = True if a.no_check else check(out)
    if a.tar:
        tp = out.with_suffix(".tar.gz")
        with tarfile.open(tp, "w:gz") as t:
            t.add(out, arcname="songcard")
        print(f"  tar {tp} ({tp.stat().st_size:,}바이트)")
    if not ok:
        sys.exit("⛔ 묶음 확인 실패")


if __name__ == "__main__":
    main()
