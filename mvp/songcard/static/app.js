"use strict";
const $app = document.getElementById("app");
// 배포 경로 접두(예: 추측 불가 하위 경로). 서버가 index.html 에 넣어 준다. 모든 주소는 BASE 를 붙여 만든다.
const BASE = (window.SONGCARD_BASE || "").replace(/\/$/, "");
const STEPS = ["received", "lyrics_pending", "lyrics_ready", "generation_queued", "generating", "audio_ready", "ready"];
const STEP_KO = {
  received: "사연 접수", lyrics_pending: "가사 쓰는 중", lyrics_ready: "가사 완성",
  generation_queued: "녹음 준비", generating: "노래 만드는 중", audio_ready: "마지막 확인", ready: "카드 완성",
};
let OPT = null;
let pollTimer = null;

// ---------- 작은 도구 ----------
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : document.createTextNode(String(k)));
  return el;
}
async function api(path, opts = {}) {
  const r = await fetch(BASE + path, { headers: { "Content-Type": "application/json" }, ...opts });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `요청 실패 (${r.status})`);
  return j;
}
function mine() { try { return JSON.parse(localStorage.getItem("songcard.mine") || "[]"); } catch { return []; } }
function saveMine(list) { try { localStorage.setItem("songcard.mine", JSON.stringify(list)); } catch {} }
function ownerTokenForShare(share) { return (mine().find(m => m.share === share) || {}).t; }
function toast(msg) { const t = h("div", { class: "toast" }, msg); document.body.append(t); setTimeout(() => t.remove(), 2200); }
function occ(id) { return OPT.occasions.find(o => o.id === id) || { label: id, emoji: "🎵" }; }
function uuid() { return (crypto.randomUUID ? crypto.randomUUID() : Date.now() + "-" + Math.random().toString(16).slice(2)); }
function fmt(s) { if (!isFinite(s)) return "0:00"; s = Math.floor(s); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; }

// ---------- 라우팅 ----------
async function route() {
  clearInterval(pollTimer);
  if (!OPT) OPT = await api("/api/options");
  const cm = location.pathname.slice(BASE.length).match(/^\/c\/([\w-]+)/);
  const hash = location.hash.replace(/^#/, "");
  $app.replaceChildren();
  window.scrollTo(0, 0);
  if (cm && !hash) return viewCard(cm[1]);
  let m;
  if ((m = hash.match(/^\/new\/(\w+)/))) return viewForm(m[1]);
  if ((m = hash.match(/^\/r\/([\w-]+)/))) return viewStatus(m[1]);
  if (hash === "/mine") return viewMine();
  return viewHome();
}
window.addEventListener("hashchange", route);

// ---------- 1. 목적 카드 ----------
async function viewHome() {
  $app.append(
    h("h1", {}, "마음을 한 곡으로"),
    h("p", { class: "lead" }, "누구에게, 어떤 날을 위한 노래인지 골라 주세요. 사연을 적으면 그 이야기로 노래를 만들어 카드에 담아 드립니다."),
    h("div", { class: "grid" }, OPT.occasions.map(o =>
      h("button", { class: "occ", onclick: () => (location.hash = `/new/${o.id}`) },
        h("span", { class: "e", "aria-hidden": "true" }, o.emoji), h("b", {}, o.label), h("small", {}, o.hint)))),
  );
  const samples = await api("/api/samples").catch(() => []);
  if (samples.length) {
    $app.append(h("h2", {}, "샘플 카드 들어보기"),
      h("p", { class: "meta" }, "샘플은 카드가 어떻게 보이고 재생되는지 보여 드리려고 내부 제작곡을 빌려 쓴 것입니다."),
      h("div", { class: "samples" }, samples.map(s =>
        h("a", { class: `mini occ-${s.occasion}`, href: `${BASE}/c/${s.share_token}` }, h("span", {}, `${occ(s.occasion).emoji} ${s.title}`)))));
  }
}

// ---------- 2. 사연·장르·보컬 입력 ----------
function viewForm(occId) {
  const o = occ(occId);
  const st = { genre: null, vocal: null, client_key: sessionStorage.getItem("songcard.ck." + occId) || uuid() };
  sessionStorage.setItem("songcard.ck." + occId, st.client_key); // 새로고침·두 번 누름에도 같은 키 → 같은 요청
  const L = OPT.limits;
  const f = (name, label, hint, tag = "input", extra = {}) => [
    h("label", { for: name }, label, hint ? h("small", {}, " · " + hint) : null),
    h(tag, { id: name, name, maxlength: L[name], ...extra }),
  ];
  const chips = (key, list) => h("div", { class: "chips", role: "group" }, list.map(x =>
    h("button", { type: "button", class: "chip", "aria-pressed": "false", onclick: e => {
      st[key] = x.id;
      e.target.parentNode.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", String(c === e.target)));
    } }, x.label)));
  const err = h("div", { class: "err", role: "alert" });
  const btn = h("button", { class: "btn", type: "submit" }, "노래 만들기 요청");
  const form = h("form", { class: "card", onsubmit: async e => {
    e.preventDefault();
    err.textContent = "";
    const fd = new FormData(form);
    const body = { occasion: occId, genre: st.genre, vocal: st.vocal, client_key: st.client_key };
    for (const k of ["recipient", "sender", "story", "memory", "message"]) body[k] = fd.get(k) || "";
    btn.disabled = true;
    try {
      const r = await api("/api/requests", { method: "POST", body: JSON.stringify(body) });
      const list = mine().filter(m => m.rid !== r.request_id);
      list.unshift({ rid: r.request_id, t: r.owner_token, share: r.share_token, recipient: body.recipient, occ: occId });
      saveMine(list);
      sessionStorage.removeItem("songcard.ck." + occId);
      location.hash = `/r/${r.request_id}`;
    } catch (x) { err.textContent = x.message; btn.disabled = false; }
  } },
    ...f("recipient", "받는 분 이름", "노래와 카드에 들어가요", "input", { required: true, autocomplete: "off" }),
    ...f("sender", "보내는 사람", "선택", "input", { autocomplete: "off" }),
    ...f("story", "사연", "어떤 사이인지, 왜 이 노래를 주고 싶은지", "textarea", { required: true, placeholder: "떠오르는 대로 적어 주세요. 이름·장소·말버릇 같은 구체적인 것이 가사를 살립니다." }),
    ...f("memory", "함께한 장면 하나", "선택", "textarea", { placeholder: "예) 비 오는 날 우산 하나로 걸어 온 길" }),
    ...f("message", "카드에 적을 한 줄", "노래 위에 헌사로 보여요", "input", {}),
    h("label", {}, "장르"), chips("genre", OPT.genres),
    h("label", {}, "목소리"), chips("vocal", OPT.vocals),
    btn, err,
  );
  $app.append(h("h1", {}, `${o.emoji} ${o.label} 노래`), h("p", { class: "lead" }, o.hint), form);
}

// ---------- 3. 제작 상태 ----------
async function viewStatus(rid) {
  const m = mine().find(x => x.rid === rid);
  if (!m) { $app.append(h("p", {}, "이 기기에서 만든 요청이 아니에요.")); return; }
  const box = h("div");
  $app.append(h("h1", {}, "노래를 만들고 있어요"), box);
  const draw = async () => {
    let r;
    try { r = await api(`/api/requests/${rid}?t=${encodeURIComponent(m.t)}`); } catch (e) { box.replaceChildren(h("p", { class: "err" }, e.message)); return; }
    const idx = STEPS.indexOf(r.status);
    const failed = r.status === "failed";
    box.replaceChildren(
      h("div", { class: `music` },
        h("div", { class: `cover occ-${r.occasion}`, style: "aspect-ratio:auto;min-height:150px" },
          h("span", { class: "e" }, occ(r.occasion).emoji),
          h("div", { class: "to" }, `To. ${r.recipient}`),
          h("div", { class: "t" }, r.status_ko)),
        h("div", { class: "body" },
          h("span", { class: `badge ${r.source}` }, r.source === "sample" ? "샘플" : "실제 제작"),
          h("span", { class: "meta" }, `  요청번호 ${r.request_id}`),
          failed ? h("p", { class: "err" }, "제작 중 문제가 생겼어요. 담당자가 확인 후 다시 진행합니다.") : null,
          h("ol", { class: "steps" }, STEPS.map((s, i) =>
            h("li", { class: i < idx || s === "ready" && idx === STEPS.length - 1 ? "done" : i === idx ? "now" : "" },
              h("span", { class: "dot" }), STEP_KO[s]))),
          r.status === "ready" ? h("a", { class: "btn", href: `${BASE}/c/${r.share_token}` }, "완성된 노래 카드 열기") : h("p", { class: "meta" }, "이 화면은 자동으로 새로 고쳐져요. 닫았다가 ‘내 카드’에서 다시 볼 수 있어요."),
        )),
    );
    if (r.status === "ready" || failed) clearInterval(pollTimer);
  };
  await draw();
  pollTimer = setInterval(draw, 5000);
}

// ---------- 4. 음악 카드 ----------
async function viewCard(share) {
  const t = ownerTokenForShare(share);
  let r;
  try { r = await api(`/api/cards/${share}${t ? "?t=" + encodeURIComponent(t) : ""}`); }
  catch (e) { $app.append(h("div", { class: "card" }, h("p", {}, e.message), h("a", { class: "btn ghost", href: `${BASE}/` }, "처음으로"))); return; }
  const owner = !!r.story || r.story === "";
  const o = occ(r.occasion);
  const audio = r.audio ? new Audio(BASE + r.audio + (t ? "?t=" + encodeURIComponent(t) : "")) : null;
  const playBtn = h("button", { class: "play", "aria-label": "재생" }, "▶");
  const seek = h("input", { type: "range", min: 0, max: 1000, value: 0, "aria-label": "재생 위치" });
  const cur = h("span", {}, "0:00"), dur = h("span", {}, "--:--");
  if (audio) {
    audio.preload = "metadata";
    playBtn.onclick = () => (audio.paused ? audio.play() : audio.pause());
    audio.onplay = () => { playBtn.textContent = "❚❚"; playBtn.setAttribute("aria-label", "일시정지"); };
    audio.onpause = () => { playBtn.textContent = "▶"; playBtn.setAttribute("aria-label", "재생"); };
    audio.onloadedmetadata = () => (dur.textContent = fmt(audio.duration));
    audio.ontimeupdate = () => { cur.textContent = fmt(audio.currentTime); if (audio.duration) seek.value = (audio.currentTime / audio.duration) * 1000; };
    seek.oninput = () => { if (audio.duration) audio.currentTime = (seek.value / 1000) * audio.duration; };
  }
  const url = `${location.origin}${BASE}/c/${share}`;
  const shareBtn = h("button", { class: "btn", onclick: async () => {
    if (owner && r.visibility !== "link") {
      await api(`/api/requests/${r.request_id}/share`, { method: "POST", body: JSON.stringify({ t, visibility: "link" }) });
      r.visibility = "link"; visLine.textContent = visText();
    }
    if (navigator.share) { try { await navigator.share({ title: r.title, text: `${r.recipient}님께 드리는 노래`, url }); return; } catch {} }
    try { await navigator.clipboard.writeText(url); toast("링크를 복사했어요"); } catch { prompt("링크", url); }
  } }, "공유하기");
  const visText = () => r.visibility === "link" ? "링크가 있는 사람은 누구나 들을 수 있어요" : "지금은 나만 볼 수 있어요 · 공유하면 링크가 열립니다";
  const visLine = h("p", { class: "meta" }, visText());
  const redo = owner && r.source === "live" && r.status === "ready" ? redoForm(r, t) : null;
  const updating = r.updating ? h("p", { class: "meta" }, `새 버전을 만드는 중이에요 (${r.status_ko}) · 완성될 때까지 지금 카드가 그대로 보여요`) : null;
  $app.append(h("div", { class: "music" },
    h("div", { class: `cover occ-${r.occasion}` },
      h("span", { class: "e", "aria-hidden": "true" }, o.emoji),
      h("div", { class: "to" }, `To. ${r.recipient}`),
      h("div", { class: "t" }, r.title),
      h("div", { class: "from" }, r.sender ? `From. ${r.sender}` : o.label)),
    h("div", { class: "body" },
      h("span", { class: `badge ${r.source}` }, r.source === "sample" ? "샘플" : "실제 제작"),
      r.sample_note ? h("p", { class: "samplenote" }, r.sample_note) : null,
      r.dedication ? h("p", { class: "dedi" }, `“${r.dedication}”`) : null,
      audio ? h("div", { class: "player" }, playBtn, h("div", { class: "bar" }, seek, h("div", { class: "time" }, cur, dur)))
            : h("p", { class: "meta" }, `아직 노래가 준비되지 않았어요 (${r.status_ko})`),
      updating,
      r.lyrics ? h("details", {}, h("summary", {}, "가사 보기"), h("div", { class: "lyrics" }, lyricsForCard(r.lyrics))) : null,
      shareBtn, owner ? visLine : null, redo,
      h("a", { class: "btn ghost", href: `${BASE}/` }, "나도 노래 카드 만들기"),
    )));
}

// 재요청: 무엇을(가사/목소리/장르) · 목소리·장르면 «무엇으로» · 메모. 키는 폼 하나에 하나, 성공하면 버린다.
function redoForm(r, t) {
  const st = { what: null, to: null, key: uuid() };
  const optsBox = h("div");
  const note = h("textarea", { maxlength: 300, placeholder: "어떻게 바꾸면 좋을지 적어 주세요 (선택)" });
  const err = h("div", { class: "err", role: "alert" });
  const pick = (group, key, val) => { st[key] = val; group.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", String(c.dataset.v === val))); };
  const chipRow = (key, list, onPick) => { const g = h("div", { class: "chips" }); list.forEach(x => g.append(h("button", { type: "button", class: "chip", "data-v": x.id, "aria-pressed": "false", onclick: () => { pick(g, key, x.id); onPick && onPick(x.id); } }, x.label))); return g; };
  const whatRow = chipRow("what", [{ id: "lyrics", label: "가사" }, { id: "vocal", label: "목소리" }, { id: "genre", label: "장르" }], w => {
    st.to = null;
    const list = w === "vocal" ? OPT.vocals : w === "genre" ? OPT.genres : [];
    optsBox.replaceChildren(...(list.length ? [h("label", {}, "무엇으로 바꿀까요?"), chipRow("to", list.filter(x => x.id !== r["production_" + w]))] : []));
  });
  const btn = h("button", { class: "btn", type: "button", onclick: async () => {
    err.textContent = "";
    if (!st.what) { err.textContent = "고칠 곳을 골라 주세요"; return; }
    if (st.what !== "lyrics" && !st.to) { err.textContent = "바꿀 값을 골라 주세요"; return; }
    btn.disabled = true;
    try {
      const x = await api(`/api/requests/${r.request_id}/redo`, { method: "POST", body: JSON.stringify({ t, what: st.what, to: st.to, note: note.value, redo_key: st.key }) });
      toast(x.created ? "다시 만들기를 요청했어요" : "이미 요청된 수정이 진행 중이에요");
      st.key = uuid();
    } catch (e) { err.textContent = e.message; }
    btn.disabled = false;
  } }, "다시 만들어 주세요");
  return h("details", {}, h("summary", {}, "고치고 싶은 곳이 있나요?"), h("label", {}, "고칠 곳"), whatRow, optsBox, h("label", {}, "메모"), note, btn, err);
}

// 가사 표시: [Verse 1] 같은 구간 태그는 «— Verse 1 —»로, 빈 구간(전주 등)은 뺀다. 원문은 그대로 둔다(표시만).
function lyricsForCard(text) {
  const blocks = text.split(/\n(?=\[)/);
  return blocks.map(b => {
    const [head, ...rest] = b.split("\n");
    const m = head.trim().match(/^\[(.+)\]$/);
    const body = rest.join("\n").trim();
    if (!m) return b.trim();
    return body ? `— ${m[1]} —\n${body}` : "";
  }).filter(Boolean).join("\n\n");
}

// ---------- 내 카드 ----------
function viewMine() {
  const list = mine();
  $app.append(h("h1", {}, "내 카드"),
    list.length ? h("div", {}, list.map(m => h("a", { class: "card", style: "display:block;text-decoration:none", href: `${BASE}/#/r/${m.rid}` },
      h("b", {}, `${occ(m.occ).emoji} ${m.recipient}`), h("div", { class: "meta" }, m.rid))))
      : h("p", { class: "lead" }, "이 기기에서 만든 카드가 아직 없어요."));
}

route();
