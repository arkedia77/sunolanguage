// 화면 함수 점검 — `static/app.js` 를 브라우저 없이 «실제로 실행»한다.
//
//   node mvp/songcard/ui_smoke.mjs [http://127.0.0.1:8787]     ← 서버가 떠 있어야 한다
//
// ★이건 «렌더 확인»이 아니다. 잡는 것 = 참조 오류·오타·필드 누락·문구 누락.
//   ⛔못 잡는 것 = CSS·레이아웃·실제 클릭/포커스·모바일 표시. 그건 눈으로 봐야 한다
// 개발용이라 배포 묶음(make_bundle.FILES)에는 들어가지 않는다.
//
// ⚠2026-09-30 실측: 이 하네스는 **10/10 통과인 채로 CSS 결함 1건을 놓쳤다** —
//   동의 칸 체크박스가 전역 `input{width:100%}` 를 먹어 문구가 세로로 흘러 카드 밖으로 나가고
//   뒤따르는 초대 코드 칸까지 밀렸다. 헤드리스 Chrome 렌더로만 보였다(`docs/songcard_mvp_shots/m390_form_v2_BROKEN_consent.png`).
//   ⇒ 이 하네스 통과는 «화면이 맞다»가 아니다. 화면을 바꾸면 **렌더를 한 장 떠서 눈으로 본다**.
import fs from "node:fs";
const BASE_URL = process.argv[2] || "http://127.0.0.1:8792";
const text = (n) => (n.nodeValue !== undefined ? n.nodeValue : (n.children || []).map(text).join("") + (n._text || ""));
function mkEl(tag) {
  return {
    tag, nodeType: 1, attrs: {}, children: [], _text: "", style: {},
    setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k]; },
    append(...k) { for (const x of k) if (x != null) this.children.push(typeof x === "string" ? { nodeValue: x } : x); },
    replaceChildren(...k) { this.children = []; this.append(...k); },
    querySelectorAll() { return []; }, addEventListener() {}, focus() {}, remove() {},
    set textContent(v) { this._text = v; }, get textContent() { return this._text; },
    get parentNode() { return mkEl("div"); },
  };
}
const app = mkEl("main");
global.document = { getElementById: () => app, createElement: mkEl, body: mkEl("body"),
  createTextNode: (v) => ({ nodeValue: String(v), nodeType: 3 }) };
global.window = { SONGCARD_BASE: "", addEventListener() {}, scrollTo() {} };
global.location = { hash: "", pathname: "/", origin: BASE_URL };
const store = {};
global.localStorage = { getItem: (k) => store[k] ?? null, setItem: (k, v) => (store[k] = v), removeItem: (k) => delete store[k] };
global.sessionStorage = global.localStorage;
Object.defineProperty(globalThis, "crypto", { value: { randomUUID: () => "uuid-0000-1111-2222" }, configurable: true });
Object.defineProperty(globalThis, "navigator", { value: { clipboard: { writeText: async () => {} } }, configurable: true });
global.setInterval = () => 0; global.clearInterval = () => {}; global.setTimeout = (f) => f && 0;
global.fetch = async (u, o) => {
  const r = await (await import("node:http")).default, res = await new Promise((ok, no) => {
    const req = r.request(BASE_URL + u.replace(BASE_URL, ""), { method: (o && o.method) || "GET",
      headers: { "Content-Type": "application/json" } }, (x) => { let b = ""; x.on("data", (d) => (b += d)); x.on("end", () => ok({ status: x.statusCode, body: b })); });
    req.on("error", no); if (o && o.body) req.write(o.body); req.end();
  });
  return { ok: res.status < 400, status: res.status, json: async () => JSON.parse(res.body) };
};
let src = fs.readFileSync("static/app.js", "utf8").replace(/^"use strict";/, "");
src = src.replace(/\nroute\(\);\s*$/, "\n");           // 자동 실행만 막고 나머지는 그대로
const mod = new Function(src + "\nreturn {route, viewHome, viewForm, viewDone, viewMine, occ};")();

const flat = (n, out = []) => { if (n.nodeValue) out.push(n.nodeValue); if (n._text) out.push(n._text);
  (n.children || []).forEach((c) => flat(c, out)); return out; };
const dump = () => flat(app).join(" ").replace(/\s+/g, " ").trim();
const R = [];
const t = (name, cond, extra = "") => R.push([cond, name, extra]);

await mod.route();                                   // OPT 적재 + 홈
const home = dump();
t("홈 — 템플릿 12종이 그려진다", (home.match(/생일|부모님께|연인에게|결혼 축가|환갑·칠순/g) || []).length >= 5, home.slice(0, 60));
t("홈 — 신규 6종 이름이 보인다", ["연인에게", "이별·추억", "졸업·첫걸음", "결혼 축가", "승진·개업 축하", "환갑·칠순"].every((x) => home.includes(x)));

app.replaceChildren(); mod.viewForm("wedding");
const form = dump();
t("폼 — 전용 칸(결혼)이 뜬다", form.includes("두 사람 이름·식 날짜"), form.slice(0, 50));
t("폼 — 관계 칸이 뜬다", form.includes("어떤 사이"));
t("폼 — 동의 칸이 뜨고 문구가 맞다", form.includes("카드에 실명 표시에 동의합니다") && form.includes("호칭만"));
t("폼 — 초대 코드 칸이 뜬다", form.includes("초대 코드"));

app.replaceChildren(); mod.viewForm("comfort");
t("폼 — 템플릿마다 전용 칸이 다르다", dump().includes("넣지 말아야 할 말"));

app.replaceChildren(); mod.viewDone("SC-20260930-abcdef");
const done = dump();
t("접수 완료 — 번호가 보인다", done.includes("SC-20260930-abcdef"));
t("접수 완료 — 대기 안내가 숫자 약속이 아니다", done.includes("보통 20분 안팎") && done.includes("더 걸릴 수 있어요"));
t("접수 완료 — 다시 찾아올 링크 버튼", done.includes("다시 찾아올 링크 복사"));

let bad = 0;
for (const [ok, name, ex] of R) { if (!ok) bad++; console.log((ok ? "✅" : "❌"), name, ex); }
console.log(`\n${R.length - bad} 통과 / ${bad} 실패`);
process.exit(bad ? 1 : 0);
