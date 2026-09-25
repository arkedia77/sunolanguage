"""얇은 호환층 — 요청·버전·take·자산 목록을 JSON 한 파일에 둔다.

LM4 DB가 완성되기 전에 쓰는 임시 저장소다. 필드는 LM4 쪽으로 옮기기 쉽게 이름을 맞춘다:
request_id · legacy_gid · takes[].suno_uuid/selected · lyrics_versions · vocal_version · asset_manifest.

- 고객 사연이 들어가므로 `var/` 는 git 밖(.gitignore).
- 중복 생성 방지: 같은 client_key 로 두 번 만들면 **처음 것을 돌려준다**. 재요청도 redo_key 로 같다.
- source = sample | live : 샘플 음원 카드와 실생성 카드를 섞지 않는다.
"""
import hashlib
import json
import os
import secrets
import threading
import time
from pathlib import Path

VAR = Path(__file__).resolve().parent / "var"
DB_FILE = VAR / "songcard_store.json"
_lock = threading.RLock()

STATUSES = [
    "received",            # 사연 접수
    "lyrics_pending",      # 가사 담당 슬롯(LM 라인)에 발주됨
    "lyrics_ready",        # 가사 수령
    "generation_queued",   # sunomusic 생성 발주 작성됨
    "generating",          # 생성 중(발주 접수 확인)
    "audio_ready",         # 오디오 회수·take 선택
    "ready",               # 카드 완성
    "failed",
]
STATUS_KO = {
    "received": "사연을 받았어요",
    "lyrics_pending": "가사를 쓰고 있어요",
    "lyrics_ready": "가사가 완성됐어요",
    "generation_queued": "녹음 준비 중이에요",
    "generating": "노래를 만들고 있어요",
    "audio_ready": "마지막으로 들어보는 중이에요",
    "ready": "노래 카드가 완성됐어요",
    "failed": "문제가 생겼어요 — 다시 시도할게요",
}


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _load():
    if not DB_FILE.exists():
        return {"requests": {}, "by_client_key": {}, "by_share": {}}
    return json.loads(DB_FILE.read_text(encoding="utf-8"))


def _save(db):
    VAR.mkdir(parents=True, exist_ok=True)
    tmp = DB_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, DB_FILE)


def _key(client_key: str) -> str:
    return hashlib.sha256(client_key.encode()).hexdigest()[:24]


def create_request(form: dict, client_key: str, sp: dict, source: str = "live") -> tuple[dict, bool]:
    """→ (request, created). 같은 client_key 면 기존 요청을 created=False 로 돌려준다."""
    with _lock:
        db = _load()
        k = _key(client_key)
        if k in db["by_client_key"]:
            return db["requests"][db["by_client_key"][k]], False
        rid = "SC-" + time.strftime("%Y%m%d") + "-" + secrets.token_hex(3)
        req = {
            "request_id": rid,
            "source": source,
            "legacy_gid": None,
            "created_at": _now(),
            "status": "received",
            "history": [{"status": "received", "at": _now()}],
            "form": form,
            "sp": sp,
            "lyrics_versions": [],        # [{v, text, by, at}]
            "vocal_version": {"v": 1, "vocal": form["vocal"], "genre": form["genre"]},
            "takes": [],                  # [{suno_uuid, asset_id, selected}]
            "asset_manifest": [],         # [{asset_id, kind, path, sha256, bytes}]
            "redos": [],                  # [{redo_id, redo_key, what, note, at, status}]
            "owner_token": secrets.token_urlsafe(16),
            "share_token": secrets.token_urlsafe(10),
            "visibility": "private",      # private | link
        }
        db["requests"][rid] = req
        db["by_client_key"][k] = rid
        db["by_share"][req["share_token"]] = rid
        _save(db)
        return req, True


def get(rid: str) -> dict | None:
    with _lock:
        return _load()["requests"].get(rid)


def by_share(token: str) -> dict | None:
    with _lock:
        db = _load()
        rid = db["by_share"].get(token)
        return db["requests"].get(rid) if rid else None


def update(rid: str, fn):
    with _lock:
        db = _load()
        req = db["requests"][rid]
        fn(req)
        _save(db)
        return req


def set_status(rid: str, status: str, note: str | None = None):
    assert status in STATUSES, status

    def f(r):
        r["status"] = status
        h = {"status": status, "at": _now()}
        if note:
            h["note"] = note
        r["history"].append(h)

    return update(rid, f)


def add_asset(rid: str, path: Path, kind: str = "audio") -> str:
    data = Path(path).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    aid = sha[:16]

    def f(r):
        if not any(a["asset_id"] == aid for a in r["asset_manifest"]):
            r["asset_manifest"].append(
                {"asset_id": aid, "kind": kind, "path": str(Path(path).resolve()), "sha256": sha, "bytes": len(data)}
            )

    update(rid, f)
    return aid


def add_take(rid: str, suno_uuid: str | None, asset_id: str, select: bool = False):
    def f(r):
        if any(t["asset_id"] == asset_id for t in r["takes"]):
            return  # 같은 오디오 두 번 붙이지 않음
        if select:
            for t in r["takes"]:
                t["selected"] = False
        r["takes"].append({"suno_uuid": suno_uuid, "asset_id": asset_id, "selected": select})

    return update(rid, f)


def request_redo(rid: str, what: str, note: str, redo_key: str) -> tuple[dict, bool]:
    """재요청. 같은 redo_key 이거나 이미 열린 재요청이 있으면 새로 만들지 않는다."""
    created = {"v": False, "redo": None}

    def f(r):
        for x in r["redos"]:
            if x["redo_key"] == redo_key or x["status"] == "open":
                created["redo"] = x
                return
        x = {"redo_id": f"R{len(r['redos'])+1}", "redo_key": redo_key, "what": what, "note": note,
             "at": _now(), "status": "open"}
        r["redos"].append(x)
        created["v"], created["redo"] = True, x

    update(rid, f)
    return created["redo"], created["v"]


def public_view(req: dict, owner: bool) -> dict:
    """카드 화면용. 비밀 토큰·서버 경로는 내보내지 않는다."""
    sel = next((t for t in req["takes"] if t["selected"]), req["takes"][0] if req["takes"] else None)
    lyr = req["lyrics_versions"][-1] if req["lyrics_versions"] else None
    f = req["form"]
    v = {
        "request_id": req["request_id"],
        "source": req["source"],
        "status": req["status"],
        "status_ko": STATUS_KO[req["status"]],
        "history": [{"status": h["status"], "status_ko": STATUS_KO[h["status"]], "at": h["at"]} for h in req["history"]],
        "occasion": f["occasion"],
        "recipient": f["recipient"],
        "sender": f.get("sender", ""),
        "dedication": f.get("message", ""),
        "title": req.get("title") or f"{f['recipient']}에게",
        "genre": f["genre"],
        "vocal": f["vocal"],
        "lyrics": lyr["text"] if lyr else None,
        "audio": f"/audio/{req['share_token']}/{sel['asset_id']}" if sel else None,
        "share_token": req["share_token"],
        "visibility": req["visibility"],
        "sample_note": req.get("sample_note"),
    }
    if owner:
        v["story"] = f.get("story", "")
        v["redos"] = req["redos"]
        v["sp"] = req["sp"]["sp"]
    return v
