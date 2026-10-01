"""사연 노래 카드 MVP 서버 — 표준 라이브러리만 쓴다.

실행:  .venv/bin/python mvp/songcard/server.py [--port 8787] [--host 0.0.0.0]

경로
  GET  /                       앱(목적 카드 → 입력 → 상태 → 음악 카드)
  GET  /c/<share_token>        공유된 음악 카드(같은 앱이 카드 화면으로 연다)
  GET  /api/options            템플릿 12종·장르·보컬 선택지
  POST /api/requests           사연 접수 (client_key 중복 방지 · ★초대 코드 필수 · 하루 상한)
  GET  /api/requests/<id>?t=   내 요청 상태(owner token 필요)
  POST /api/requests/<id>/redo 재요청(가사/보컬/장르) — redo_key 로 중복 방지
  POST /api/requests/<id>/share  공개 범위 private|link
  GET  /api/cards/<share>      공유 카드(visibility=link 이거나 owner token)
  GET  /audio/<share>/<asset>  오디오(카드 접근 권한과 같은 규칙)
"""
import argparse
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import sp_builder
import store
import templates

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"
ROOT = HERE.parents[1]          # sunolanguage 리포 루트 — 자산 경로는 여기 기준 상대경로로 저장
BASE = ""                       # 배포 경로 접두(--base). 프록시가 접두를 떼든 안 떼든 둘 다 받는다

# ---------- 접근 통제 (2026-09-30 · kee 전결 ⒞ 하루 5건) ----------
# ★**fail-closed**: 초대 코드를 «하나도 주지 않으면 접수를 전부 막는다**.
#   반대로 짜면(코드 없으면 통과) 설정을 빠뜨린 배포가 조용히 «공개 POST 구멍»이 된다 —
#   그 실수는 화면에 아무 표시도 안 남는다. 그래서 기본값을 «닫힘»으로 둔다.
INVITES: set[str] = set()
DAILY_LIMIT = 5

LIMITS = {"recipient": 20, "sender": 20, "relation": 20, "story": 1200, "memory": 600, "message": 200}
OCCASIONS = templates.options()      # ★정본은 templates.py (여기서 목록을 다시 적지 않는다)


def _json(h, code, obj):
    body = json.dumps(obj, ensure_ascii=False).encode()
    h.send_response(code)
    h.send_header("X-Robots-Tag", "noindex, nofollow")
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Cache-Control", "no-store")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)


def _can_view(req, token):
    return req is not None and (req["visibility"] == "link" or token == req["owner_token"])


class H(BaseHTTPRequestHandler):
    server_version = "songcard/0.1"

    def log_message(self, fmt, *a):  # 사연 내용이 로그에 안 남게 경로만
        print(f"[{self.log_date_time_string()}] {self.command} {urlparse(self.path).path}")

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 64_000:
            raise ValueError("본문이 너무 큽니다")
        return json.loads(self.rfile.read(n) or b"{}")

    # ---------- GET ----------
    def _path(self):
        p = urlparse(self.path).path
        if BASE and (p == BASE or p.startswith(BASE + "/")):
            p = p[len(BASE):] or "/"
        return p

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = self._path()
        if p == "/robots.txt":
            body = b"User-agent: *\nDisallow: /\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if p == "/" or p.startswith("/c/"):
            html = (STATIC / "index.html").read_text(encoding="utf-8").replace("__BASE__", BASE).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            return self.wfile.write(html)
        if p.startswith("/static/"):
            f = (STATIC / p[len("/static/"):]).resolve()
            if STATIC in f.parents and f.is_file():
                ct = {"css": "text/css", "js": "text/javascript", "svg": "image/svg+xml"}.get(f.suffix[1:], "application/octet-stream")
                return self._file(f, ct + "; charset=utf-8")
            return self.send_error(404)
        if p == "/api/options":
            return _json(self, 200, {
                "occasions": OCCASIONS,
                "invite_required": True,
                "genres": [{"id": k, "label": v["label"]} for k, v in sp_builder.GENRES.items()],
                "vocals": [{"id": k, "label": v["label"]} for k, v in sp_builder.VOCALS.items()],
                "limits": LIMITS,
            })
        if p == "/api/samples":
            db = store._load()
            return _json(self, 200, [store.public_view(r, owner=False) for r in db["requests"].values()
                                     if r["source"] == "sample" and r["visibility"] == "link"])
        m = re.fullmatch(r"/api/requests/([\w-]+)", p)
        if m:
            req = store.get(m.group(1))
            if not req or q.get("t") != req["owner_token"]:
                return _json(self, 404, {"error": "없는 요청입니다"})
            return _json(self, 200, store.public_view(req, owner=True))
        m = re.fullmatch(r"/api/cards/([\w-]+)", p)
        if m:
            req = store.by_share(m.group(1))
            if not _can_view(req, q.get("t")):
                return _json(self, 404, {"error": "비공개 카드이거나 없는 카드입니다"})
            return _json(self, 200, store.public_view(req, owner=q.get("t") == req["owner_token"]))
        m = re.fullmatch(r"/audio/([\w-]+)/([0-9a-f]{16})", p)
        if m:
            req = store.by_share(m.group(1))
            if not _can_view(req, q.get("t")):
                return self.send_error(404)
            a = next((a for a in req["asset_manifest"] if a["asset_id"] == m.group(2)), None)
            if not a:
                return self.send_error(404)
            ap = Path(a["path"])
            return self._file(ap if ap.is_absolute() else ROOT / ap, "audio/mpeg", ranged=True)
        self.send_error(404)

    def _file(self, path: Path, ctype, ranged=False):
        if not path.is_file():
            return self.send_error(404)
        size = path.stat().st_size
        start, end = 0, size - 1
        rng = self.headers.get("Range") if ranged else None
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", rng or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("Content-Length", str(end - start + 1))
        if ranged:
            self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(65536, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    # ---------- POST ----------
    def do_POST(self):
        p = self._path()
        try:
            body = self._body()
        except Exception as e:
            return _json(self, 400, {"error": str(e)})

        if p == "/api/requests":
            # ★순서: 초대 → 검증 → 상한. 상한을 맨 뒤에 두어야 «거절된 요청»이 상한을 먹지 않는다.
            if str(body.get("invite") or "").strip() not in INVITES:
                return _json(self, 403, {"error": "지금은 초대 코드를 받은 분만 만들 수 있어요"})
            form, err = _validate(body)
            if err:
                return _json(self, 400, {"error": err})
            ck = str(body.get("client_key") or "")
            if len(ck) < 8:
                return _json(self, 400, {"error": "client_key 가 필요합니다"})
            # 같은 client_key 재전송은 «새 요청»이 아니므로 상한에 걸리면 안 된다 → 기존분은 먼저 돌려준다
            existing = store.by_client_key(ck)
            if existing is None and store.count_today_live() >= DAILY_LIMIT:
                return _json(self, 429, {"error": f"오늘 만들 수 있는 노래({DAILY_LIMIT}곡)를 다 썼어요. 내일 다시 부탁드려요"})
            sp = sp_builder.build_sp(form["occasion"], form["genre"], form["vocal"])
            req, created = store.create_request(form, ck, sp, source="live")
            return _json(self, 201 if created else 200, {
                "created": created, "request_id": req["request_id"],
                "owner_token": req["owner_token"], "share_token": req["share_token"],
            })

        m = re.fullmatch(r"/api/requests/([\w-]+)/(redo|share)", p)
        if m:
            req = store.get(m.group(1))
            if not req or body.get("t") != req["owner_token"]:
                return _json(self, 404, {"error": "없는 요청입니다"})
            if m.group(2) == "share":
                vis = body.get("visibility")
                if vis not in ("private", "link"):
                    return _json(self, 400, {"error": "visibility=private|link"})
                store.update(req["request_id"], lambda r: r.__setitem__("visibility", vis))
                return _json(self, 200, {"visibility": vis})
            what = body.get("what")
            if what not in ("lyrics", "vocal", "genre"):
                return _json(self, 400, {"error": "what=lyrics|vocal|genre"})
            if req["source"] == "sample":
                return _json(self, 409, {"error": "샘플 카드는 재요청할 수 없어요"})
            if req["status"] != "ready":
                return _json(self, 409, {"error": "지금 만드는 중인 노래가 끝난 뒤에 고칠 수 있어요"})
            to = None
            if what in ("vocal", "genre"):   # 무엇으로 바꿀지 값이 있어야 다시 만들 수 있다
                to = str(body.get("to") or "")
                allowed = sp_builder.VOCALS if what == "vocal" else sp_builder.GENRES
                if to not in allowed:
                    return _json(self, 400, {"error": f"바꿀 {'목소리' if what == 'vocal' else '장르'}를 골라 주세요"})
                if to == req["vocal_version"][what]:
                    return _json(self, 400, {"error": "지금과 같은 선택이에요"})
            redo, created = store.request_redo(req["request_id"], what, str(body.get("note", ""))[:300],
                                               str(body.get("redo_key") or ""), to=to)
            return _json(self, 201 if created else 200, {"created": created, "redo": redo})
        self.send_error(404)


def _validate(b):
    f = {k: str(b.get(k, "")).strip() for k in
         ("occasion", "recipient", "sender", "relation", "story", "memory", "message", "genre", "vocal")}
    if f["occasion"] not in templates.TEMPLATES:
        return None, "목적을 골라 주세요"
    if f["genre"] not in sp_builder.GENRES or f["vocal"] not in sp_builder.VOCALS:
        return None, "장르와 보컬을 골라 주세요"
    if not f["recipient"]:
        return None, "받는 분 이름을 적어 주세요"
    if not f["relation"]:
        return None, "어떤 사이인지 한 단어로 적어 주세요(예: 엄마·친구)"
    # ★이름 공개 동의 — ★«두 칸»(kee 10-01 `102626`, solself 반증 반영). 둘 다 기본 «꺼짐».
    #   요청자 체크는 제3자의 공개 허락을 증명하지 못하므로 쓰임새별로 나눠 받는다.
    for k in store.CONSENT_KEYS:
        f[k] = bool(b.get(k))
    # 템플릿 전용 칸 1개(있는 템플릿만) — 값은 form.extra 에 그대로 싣는다
    x = templates.TEMPLATES[f["occasion"]]["extra"]
    if x:
        val = str(b.get("extra", "")).strip()
        if len(val) > x["limit"]:
            return None, f"{x['label']} 은(는) {x['limit']}자까지예요"
        f["extra"] = val
        f["extra_label"] = x["label"]
    if len(f["story"]) < 10:
        return None, "사연을 조금만 더 적어 주세요(10자 이상)"
    for k, n in LIMITS.items():
        if len(f[k]) > n:
            return None, f"{k} 는 {n}자까지예요"
    return f, None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--base", default="", help="배포 경로 접두(예: /abc123) — 추측 불가 하위 경로에 올릴 때")
    ap.add_argument("--invite", action="append", default=[], metavar="CODE",
                    help="초대 코드(여러 번 지정 가능). ★하나도 없으면 접수가 전부 막힌다(fail-closed)")
    ap.add_argument("--daily-limit", type=int, default=DAILY_LIMIT, help=f"하루 새 요청 상한(기본 {DAILY_LIMIT})")
    a = ap.parse_args()
    BASE = "/" + a.base.strip("/") if a.base.strip("/") else ""
    INVITES = {c.strip() for c in a.invite if c.strip()}
    DAILY_LIMIT = a.daily_limit
    print(f"songcard MVP → http://{a.host}:{a.port}{BASE}/")
    print(f"  초대 코드 {len(INVITES)}개" + ("" if INVITES else " — ⛔0개라 접수가 전부 막힙니다(fail-closed)")
          + f" · 하루 상한 {DAILY_LIMIT}건")
    ThreadingHTTPServer((a.host, a.port), H).serve_forever()
