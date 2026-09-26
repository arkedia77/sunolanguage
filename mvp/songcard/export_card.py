"""완성 카드 1장을 «정적 묶음» 폴더로 내보낸다 — 서버 없이 정적 호스팅에 그대로 올린다.

  .venv/bin/python mvp/songcard/export_card.py <request_id> [--out mvp/songcard/var/export]

산출: <out>/<무작위 16자>/
  index.html   카드 화면(표지·헌사·재생기·가사·링크 복사) — 모든 경로가 상대경로라 어느 주소·하위 경로에 올려도 동작
  app.css      화면 스타일(앱과 같은 파일)
  card.js      재생기·가사 표시·공유
  card.json    카드 데이터
  audio.mp3    납품본 take(delivered) 1개

⛔ 묶음에 넣지 않는 것: 사연·장면 원문, SP, owner/share 토큰, request_id, 다른 take, WAV.
   카드에 원래 보이는 것(받는 분·보내는 분 이름, 헌사 한 줄, 제목, 가사)만 싣는다.
   실제로 빠졌는지는 내보낸 뒤 폴더 전체를 사연 문자열로 grep 해서 확인한다(출력에 찍음).
"""
import argparse
import hashlib
import json
import secrets
import shutil
import string
import sys
from pathlib import Path

import store

HERE = Path(__file__).resolve().parent
OCC = {"birthday": ("생일", "🎂"), "anniversary": ("기념일", "💍"), "thanks": ("감사", "🌿"),
       "cheer": ("응원", "🔥"), "comfort": ("위로", "🕯"), "parents": ("부모님께", "🏡")}

INDEX = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="stylesheet" href="app.css">
</head>
<body>
<header class="top"><span class="brand">노래 카드</span></header>
<main id="app" aria-live="polite"></main>
<footer class="foot">{foot}</footer>
<script src="card.js"></script>
</body>
</html>
"""

CARD_JS = r"""\"use strict\";
const $app = document.getElementById("app");
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : document.createTextNode(String(k)));
  return el;
}
function fmt(s) { if (!isFinite(s)) return "0:00"; s = Math.floor(s); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; }
function lyricsForCard(text) {
  return text.split(/\n(?=\[)/).map(b => {
    const [head, ...rest] = b.split("\n");
    const m = head.trim().match(/^\[(.+)\]$/);
    const body = rest.join("\n").trim();
    if (!m) return b.trim();
    return body ? `— ${m[1]} —\n${body}` : "";
  }).filter(Boolean).join("\n\n");
}
function toast(msg) { const t = h("div", { class: "toast" }, msg); document.body.append(t); setTimeout(() => t.remove(), 2200); }
fetch("card.json").then(r => r.json()).then(c => {
  const audio = new Audio("audio.mp3");
  audio.preload = "metadata";
  const playBtn = h("button", { class: "play", "aria-label": "재생" }, "▶");
  const seek = h("input", { type: "range", min: 0, max: 1000, value: 0, "aria-label": "재생 위치" });
  const cur = h("span", {}, "0:00"), dur = h("span", {}, "--:--");
  playBtn.onclick = () => (audio.paused ? audio.play() : audio.pause());
  audio.onplay = () => { playBtn.textContent = "❚❚"; playBtn.setAttribute("aria-label", "일시정지"); };
  audio.onpause = () => { playBtn.textContent = "▶"; playBtn.setAttribute("aria-label", "재생"); };
  audio.onloadedmetadata = () => (dur.textContent = fmt(audio.duration));
  audio.ontimeupdate = () => { cur.textContent = fmt(audio.currentTime); if (audio.duration) seek.value = (audio.currentTime / audio.duration) * 1000; };
  seek.oninput = () => { if (audio.duration) audio.currentTime = (seek.value / 1000) * audio.duration; };
  const share = h("button", { class: "btn", onclick: async () => {
    const url = location.href.split("#")[0];
    if (navigator.share) { try { await navigator.share({ title: c.title, text: `${c.recipient}님께 드리는 노래`, url }); return; } catch {} }
    try { await navigator.clipboard.writeText(url); toast("링크를 복사했어요"); } catch { prompt("링크", url); }
  } }, "링크 공유하기");
  $app.append(h("div", { class: "music" },
    h("div", { class: `cover occ-${c.occasion}` },
      h("span", { class: "e", "aria-hidden": "true" }, c.emoji),
      h("div", { class: "to" }, `To. ${c.recipient}`),
      h("div", { class: "t" }, c.title),
      h("div", { class: "from" }, c.sender ? `From. ${c.sender}` : c.occasion_label)),
    h("div", { class: "body" },
      h("span", { class: `badge ${c.source}` }, c.source === "sample" ? "샘플" : "실제 제작"),
      c.sample_note ? h("p", { class: "samplenote" }, c.sample_note) : null,
      c.dedication ? h("p", { class: "dedi" }, `“${c.dedication}”`) : null,
      h("div", { class: "player" }, playBtn, h("div", { class: "bar" }, seek, h("div", { class: "time" }, cur, dur))),
      c.lyrics ? h("details", {}, h("summary", {}, "가사 보기"), h("div", { class: "lyrics" }, lyricsForCard(c.lyrics))) : null,
      share,
      h("p", { class: "meta" }, "이 페이지는 링크를 받은 분만 볼 수 있도록 검색에 노출되지 않습니다."))));
}).catch(() => $app.append(h("p", {}, "카드를 불러오지 못했어요.")));
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("request_id")
    ap.add_argument("--out", default=str(HERE / "var" / "export"))
    a = ap.parse_args()
    req = store.get(a.request_id)
    if not req:
        sys.exit("⛔ 없는 요청")
    if req["status"] != "ready" or not req.get("delivered"):
        sys.exit(f"⛔ 완성(ready)·납품본이 있는 카드만 내보냅니다 — 현재 {req['status']}")
    d = req["delivered"]
    asset = next(x for x in req["asset_manifest"] if x["asset_id"] == d["asset_id"])
    src = Path(asset["path"]) if Path(asset["path"]).is_absolute() else store.ROOT / asset["path"]
    lyr = next(x["text"] for x in req["lyrics_versions"] if x["v"] == d["lyrics_v"])
    f = req["form"]
    label, emoji = OCC[f["occasion"]]

    alphabet = string.ascii_letters + string.digits
    slug = "".join(secrets.choice(alphabet) for _ in range(16))   # admin 규약: /c/<무작위 16자>/
    out = Path(a.out) / slug
    out.mkdir(parents=True)
    card = {
        "title": d.get("title") or req.get("title") or f"{f['recipient']}에게",
        "occasion": f["occasion"], "occasion_label": label, "emoji": emoji,
        "recipient": f["recipient"], "sender": f.get("sender", ""), "dedication": f.get("message", ""),
        "lyrics": lyr, "source": req["source"], "sample_note": req.get("sample_note"),
        "genre": d.get("genre"), "vocal": d.get("vocal"),
    }
    (out / "card.json").write_text(json.dumps(card, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(src, out / "audio.mp3")
    shutil.copyfile(HERE / "static" / "app.css", out / "app.css")
    (out / "card.js").write_text(CARD_JS.replace('\\"use strict\\";', '"use strict";'), encoding="utf-8")
    foot = "샘플 카드" if req["source"] == "sample" else "노래 카드"
    (out / "index.html").write_text(INDEX.format(title=card["title"].replace("<", "&lt;"), foot=foot), encoding="utf-8")

    # 빠졌어야 할 것이 정말 빠졌는지 — 폴더 전체 텍스트를 뒤진다
    leaks = {"story": f.get("story", ""), "memory": f.get("memory", ""), "sp": req["sp"]["sp"],
             "owner_token": req["owner_token"], "share_token": req["share_token"], "request_id": req["request_id"]}
    blob = "".join(p.read_text(encoding="utf-8") for p in out.iterdir() if p.suffix in (".html", ".js", ".json", ".css"))
    found = [k for k, v in leaks.items() if v and v[:20] in blob]
    sha = hashlib.sha256((out / "audio.mp3").read_bytes()).hexdigest()[:16]
    print(f"EXPORTED {out}")
    print(f"  files  {sorted(p.name for p in out.iterdir())}")
    print(f"  audio  sha256[:16]={sha} (asset {d['asset_id']})")
    print(f"  누출검사 {'⛔ ' + ', '.join(found) if found else '0건 (사연·장면·SP·토큰·request_id 미포함)'}")
    if found:
        shutil.rmtree(out)
        sys.exit("⛔ 누출 — 묶음을 지웠습니다")


if __name__ == "__main__":
    main()
