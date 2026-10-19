#!/usr/bin/env python3
"""fetch_suno_help.py — help.suno.com 공식 도움말 수집(LEO 10-19 «수노가이드 조차 학습 안 한 거네» · encore 130359).
카테고리를 따라 글 id 를 모으고 글마다 제목·Edited 날짜·본문 텍스트를 data/suno_docs/help/{id}.json 에 저장, index.json 생성.
사용: .venv/bin/python scripts/fetch_suno_help.py
"""
import html, json, re, subprocess, time
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "data/suno_docs/help"
BASE = "https://help.suno.com"
ROOTS = ["/en/categories/550017-making-music", "/en/categories/1708865-studio", "/en/categories/594561-mobile-app",
         "/en/categories/1730369-hooks", "/en/categories/550145-rights-ownership"]

def get(path):
    r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "30", BASE + path], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")

def text(h):
    m = re.search(r"<article.*?</article>", h, re.S)
    s = m.group(0) if m else h
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S)
    s = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\n\s*\n+", "\n", s).strip()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cats, seen_c, arts = list(ROOTS), set(), {}
    while cats:
        c = cats.pop(0)
        if c in seen_c: continue
        seen_c.add(c); h = get(c); time.sleep(0.5)
        for sc in re.findall(r'href="(?:https://help\.suno\.com)?(/en/categories/[0-9][^"#?]*)"', h):
            if sc not in seen_c: cats.append(sc)
        for a in re.findall(r'href="(?:https://help\.suno\.com)?/en/articles/(\d+)', h):
            arts.setdefault(a, c)
    idx = []
    for a, c in sorted(arts.items()):
        h = get(f"/en/articles/{a}"); time.sleep(0.5)
        t = text(h)
        title = html.unescape((re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1]).split("|")[0].strip()
        ed = re.search(r"Edited\s*\n?\s*([A-Z][a-z]+day, [A-Z][a-z]+ \d{1,2} \d{4})", t)
        rec = {"id": a, "url": f"{BASE}/en/articles/{a}", "category": c, "title": title,
               "edited": ed.group(1) if ed else None, "text": t}
        (OUT / f"{a}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        idx.append({k: rec[k] for k in ("id", "url", "category", "title", "edited")} | {"chars": len(t)})
    (OUT / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1))
    print("categories", len(seen_c), "articles", len(idx))

if __name__ == "__main__":
    main()
