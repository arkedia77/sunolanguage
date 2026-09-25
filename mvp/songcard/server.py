"""사연 노래 카드 MVP 서버 — 표준 라이브러리만 쓴다.

실행:  .venv/bin/python mvp/songcard/server.py [--port 8787] [--host 0.0.0.0]

경로
  GET  /                       앱(목적 카드 → 입력 → 상태 → 음악 카드)
  GET  /c/<share_token>        공유된 음악 카드(같은 앱이 카드 화면으로 연다)
  GET  /api/options            목적·장르·보컬 선택지
  POST /api/requests           사연 접수 (client_key 로 중복 방지)
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

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"

OCCASIONS = [
    {"id": "birthday", "label": "생일", "emoji": "🎂", "hint": "올해도 태어나줘서 고맙다는 말"},
    {"id": "anniversary", "label": "기념일", "emoji": "💍", "hint": "함께 지나온 시간"},
    {"id": "thanks", "label": "감사", "emoji": "🌿", "hint": "말로 다 못 한 고마움"},
    {"id": "cheer", "label": "응원", "emoji": "🔥", "hint": "새 출발·시험·도전 앞에서"},
    {"id": "comfort", "label": "위로", "emoji": "🕯", "hint": "곁에 있다는 마음"},
    {"id": "parents", "label": "부모님께", "emoji": "🏡", "hint": "늦게 전하는 이야기"},
]
LIMITS = {"recipient": 20, "sender": 20, "story": 1200, "memory": 600, "message": 200}


def _json(h, code, obj):
    body = json.dumps(obj, ensure_ascii=False).encode()
    h.send_response(code)
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
    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = u.path
        if p == "/" or p.startswith("/c/"):
            return self._file(STATIC / "index.html", "text/html; charset=utf-8")
        if p.startswith("/static/"):
            f = (STATIC / p[len("/static/"):]).resolve()
            if STATIC in f.parents and f.is_file():
                ct = {"css": "text/css", "js": "text/javascript", "svg": "image/svg+xml"}.get(f.suffix[1:], "application/octet-stream")
                return self._file(f, ct + "; charset=utf-8")
            return self.send_error(404)
        if p == "/api/options":
            return _json(self, 200, {
                "occasions": OCCASIONS,
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
            return self._file(Path(a["path"]), "audio/mpeg", ranged=True)
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
        p = urlparse(self.path).path
        try:
            body = self._body()
        except Exception as e:
            return _json(self, 400, {"error": str(e)})

        if p == "/api/requests":
            form, err = _validate(body)
            if err:
                return _json(self, 400, {"error": err})
            ck = str(body.get("client_key") or "")
            if len(ck) < 8:
                return _json(self, 400, {"error": "client_key 가 필요합니다"})
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
    f = {k: str(b.get(k, "")).strip() for k in ("occasion", "recipient", "sender", "story", "memory", "message", "genre", "vocal")}
    if f["occasion"] not in {o["id"] for o in OCCASIONS}:
        return None, "목적을 골라 주세요"
    if f["genre"] not in sp_builder.GENRES or f["vocal"] not in sp_builder.VOCALS:
        return None, "장르와 보컬을 골라 주세요"
    if not f["recipient"]:
        return None, "받는 분 이름을 적어 주세요"
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
    a = ap.parse_args()
    print(f"songcard MVP → http://{a.host}:{a.port}/")
    ThreadingHTTPServer((a.host, a.port), H).serve_forever()
