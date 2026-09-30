"""얇은 호환층 — 요청·버전·take·자산 목록을 JSON 한 파일에 둔다.

LM4 DB가 완성되기 전에 쓰는 임시 저장소다. 필드는 LM4 쪽으로 옮기기 쉽게 이름을 맞춘다:
request_id · legacy_gid · takes[].suno_uuid/selected · lyrics_versions · vocal_version · asset_manifest.

- 고객 사연이 들어가므로 `var/` 는 git 밖(.gitignore).
- 중복 생성 방지: 같은 client_key 로 두 번 만들면 **처음 것을 돌려준다**. 재요청도 redo_key 로 같다.
- source = sample | live : 샘플 음원 카드와 실생성 카드를 섞지 않는다.
"""
import fcntl
import hashlib
import json
import os
import secrets
import threading
import time
from pathlib import Path

# ★저장 위치는 환경변수로 옮길 수 있다(2026-09-30). 두 가지에 쓴다:
#   ⑴배포 — leoserver 에서 디스크 위치를 admin 이 정할 수 있게(사연 원문이 들어가는 곳이다)
#   ⑵점검 — 하루 상한 검사는 «빈 저장소»라야 참을 잰다. 공용 var 로 재면 오늘분에 오염돼
#     첫 요청부터 429 가 나고, 그래도 「두 번째가 429」는 통과해 **거짓 초록**이 된다(09-30 실물).
VAR = Path(os.environ.get("SONGCARD_VAR") or (Path(__file__).resolve().parent / "var"))
DB_FILE = VAR / "songcard_store.json"


class _XLock:
    """스레드 잠금 + **프로세스 간** 파일 잠금(flock).

    서버와 운영 CLI(pipeline.py)가 서로 다른 프로세스에서 같은 JSON을 읽고-고치고-쓴다.
    RLock 만으로는 프로세스 사이가 안 막혀서 한쪽 갱신이 사라졌다(solself 09-25 독립 재현).
    같은 스레드에서 다시 들어오면 flock 은 한 번만 잡는다.
    """

    def __init__(self):
        self._r = threading.RLock()
        self._depth = 0
        self._fd = None

    def __enter__(self):
        self._r.acquire()
        if self._depth == 0:
            VAR.mkdir(parents=True, exist_ok=True)
            self._fd = os.open(VAR / ".store.lock", os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(self._fd, fcntl.LOCK_EX)
        self._depth += 1
        return self

    def __exit__(self, *exc):
        self._depth -= 1
        if self._depth == 0:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = None
        self._r.release()


_lock = _XLock()

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


def by_client_key(client_key: str) -> dict | None:
    """이미 접수된 같은 폼인지. ★상한 판정 «전에» 봐야 재전송이 상한을 먹지 않는다."""
    with _lock:
        db = _load()
        rid = db["by_client_key"].get(_key(client_key))
        return db["requests"].get(rid) if rid else None


def count_today_live(today: str | None = None) -> int:
    """오늘(로컬 날짜) 새로 «만들어진» live 요청 수 — 하루 상한 판정용.
    ★샘플(source=sample)은 안 센다. 재전송은 새 요청이 아니므로 애초에 여기 안 들어온다."""
    today = today or time.strftime("%Y-%m-%d")
    with _lock:
        return sum(1 for r in _load()["requests"].values()
                   if r["source"] == "live" and str(r.get("created_at", ""))[:10] == today)


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


ROOT = Path(__file__).resolve().parents[2]   # sunolanguage 리포 루트


def _relpath(path) -> str:
    """리포 안 파일은 루트 기준 상대경로로 저장(다른 머신·경로에 배포해도 풀리게). 밖이면 절대경로."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def add_asset(rid: str, path: Path, kind: str = "audio") -> str:
    data = Path(path).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    aid = sha[:16]

    def f(r):
        if not any(a["asset_id"] == aid for a in r["asset_manifest"]):
            r["asset_manifest"].append(
                {"asset_id": aid, "kind": kind, "path": _relpath(path), "sha256": sha, "bytes": len(data)}
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
        # take 는 만들어질 때의 가사판·보컬판에 묶인다(다른 판의 가사와 섞여 보이지 않게)
        r["takes"].append({"suno_uuid": suno_uuid, "asset_id": asset_id, "selected": select,
                           "lyrics_v": r["lyrics_versions"][-1]["v"] if r["lyrics_versions"] else None,
                           "vocal_v": r["vocal_version"]["v"]})

    return update(rid, f)


def request_redo(rid: str, what: str, note: str, redo_key: str, to: str | None = None) -> tuple[dict, bool]:
    """재요청. 같은 redo_key 이거나 이미 열린 재요청이 있으면 새로 만들지 않는다.

    보컬·장르 재요청은 바꿀 **값**(to)을 같이 받아 둔다 — 닫을 때 그 값으로 SP·발주서를 다시 만든다.
    """
    created = {"v": False, "redo": None}

    def f(r):
        for x in r["redos"]:
            if (redo_key and x["redo_key"] == redo_key) or x["status"] == "open":
                created["redo"] = x
                return
        x = {"redo_id": f"R{len(r['redos'])+1}", "redo_key": redo_key, "what": what, "to": to, "note": note,
             "at": _now(), "status": "open"}
        r["redos"].append(x)
        created["v"], created["redo"] = True, x

    update(rid, f)
    return created["redo"], created["v"]


def deliver(r: dict, take: dict):
    """납품본 = (take · 그 take 의 가사판 · 보컬판) 한 묶음. 카드는 이것만 보여 준다."""
    r["delivered"] = {"asset_id": take["asset_id"], "lyrics_v": take["lyrics_v"], "vocal_v": take["vocal_v"],
                      "genre": r["vocal_version"]["genre"], "vocal": r["vocal_version"]["vocal"],
                      "title": r.get("title"), "at": _now()}


def display_names(form: dict) -> tuple[str, str]:
    """카드·상태 화면에 보일 (받는 분, 보내는 분). ★이 규칙은 여기 한 곳에만 있다
    (`public_view` 와 `export_card` 가 둘 다 여기서 읽는다 — 한쪽만 고쳐 새는 걸 막는다).

    kee 전결 ⒝(2026-09-30): 「카드에 이름 표시」 동의 칸 **기본 꺼짐**.
      꺼져 있으면 실명 대신 **호칭**(relation, 예 「엄마」)만 나간다.
    ⛔`name_consent` 키가 «없으면» 켜진 것으로 보지 않는다 — **불명이면 가리는 쪽**이다.
      (09-26 이전 요청에는 이 칸 자체가 없다. 그것들을 노출로 승격시키지 않는다.)
    """
    if form.get("name_consent"):
        return form.get("recipient", ""), form.get("sender", "")
    rel = (form.get("relation") or "").strip()
    return (rel or "소중한 분"), ""


def public_view(req: dict, owner: bool) -> dict:
    """카드 화면용. 비밀 토큰·서버 경로는 내보내지 않는다."""
    # 카드에는 «납품본» 묶음만 싣는다. 새 판을 만드는 중이어도 이전 납품본(오디오+그 가사)을 그대로 보여 주고,
    # 새 가사와 옛 오디오를 섞지 않는다.
    d = req.get("delivered")
    lyr = next((x for x in req["lyrics_versions"] if d and x["v"] == d["lyrics_v"]), None)
    f = req["form"]
    to_name, from_name = display_names(f)
    v = {
        "request_id": req["request_id"],
        "source": req["source"],
        "status": req["status"],
        "status_ko": STATUS_KO[req["status"]],
        "history": [{"status": h["status"], "status_ko": STATUS_KO[h["status"]], "at": h["at"]} for h in req["history"]],
        "occasion": f["occasion"],
        "recipient": to_name,                 # ★동의 꺼짐이면 호칭(display_names)
        "sender": from_name,
        "name_consent": bool(f.get("name_consent")),
        "dedication": f.get("message", ""),
        "title": (d or {}).get("title") or req.get("title") or f"{to_name}에게",
        # 카드에 보이는 보컬·장르 = 납품본 것. 만드는 중인 판은 production_* 로 따로 둔다(solself 09-25 재검 메모)
        "genre": (d or {}).get("genre") or req["vocal_version"]["genre"],
        "vocal": (d or {}).get("vocal") or req["vocal_version"]["vocal"],
        "production_genre": req["vocal_version"]["genre"],
        "production_vocal": req["vocal_version"]["vocal"],
        "lyrics": lyr["text"] if lyr else None,
        "audio": f"/audio/{req['share_token']}/{d['asset_id']}" if d else None,
        "updating": bool(d) and req["status"] != "ready",
        "share_token": req["share_token"],
        "visibility": req["visibility"],
        "sample_note": req.get("sample_note"),
    }
    if owner:
        v["story"] = f.get("story", "")
        v["real_recipient"] = f.get("recipient", "")   # 오너 본인에게만
        v["relation"] = f.get("relation", "")
        v["redos"] = req["redos"]
        v["sp"] = req["sp"]["sp"]
    return v
