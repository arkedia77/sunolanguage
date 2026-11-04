#!/usr/bin/env python3
"""weekly_chart_genre_v1.py — 주간 차트 장르·결 표 (encore 11-05 발주 · 매주 일요일).

입력 = 멜론 top100 (지금 차트 페이지 · 또는 encore 스냅숏 tsv) + 스포티파이 KR 주간(kworb 공개 집계 · 별도 채널).
곡마다 멜론 공개 페이지 3장: 곡 정보(장르·발매일) · 아티스트(유형=그룹/솔로|성별) · 앨범(기획사).
⛔ 오디오·가사 수집 0 · 공개 집계·곡 정보만. 출력 = data/weekly_chart/{label}.json (쓰기 = 그 파일 하나 · DB 쓰기 0).

「결」은 멜론 장르가 아니라 **우리 판 체계로 내가 붙인 분류**(규칙 = GYEOL_RULES · 행마다 근거 칸).
"""
import argparse, html, json, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0"}
M = "https://www.melon.com"
GYEOL_RULES = [
    ("트롯", "멜론 장르에 트로트"),
    ("힙합", "멜론 장르에 랩/힙합"),
    ("발라드", "멜론 장르에 발라드"),
    ("밴드·싱어송라이터", "멜론 장르에 록/메탈·인디음악·포크/블루스"),
    ("걸그룹 댄스", "위 넷 아님 ∧ 아티스트 유형 그룹|여성"),
    ("보이그룹", "위 넷 아님 ∧ 아티스트 유형 그룹|남성"),
    ("그 밖", "나머지(솔로 댄스·R&B·OST 등) — 장르 칸 그대로 봄"),
]


def get(url, cache={}):
    for wait in (None,):  # 재시도 안 함 — 막히면 그 칸은 미측정(차단 우회 0)
        if url in cache: break
        time.sleep(2)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                cache[url] = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError:
            if wait is None: raise
            time.sleep(wait)
    return cache[url]


def dd(page, dt):
    m = re.search(rf"<dt>{dt}</dt>\s*<dd>(.*?)</dd>", page, re.S)
    return re.sub(r"\s*\|[\s|]*", "|", re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "|", m.group(1))))).strip(" |")if m else None


def norm(s):
    s = unicodedata.normalize("NFKC", html.unescape(s)).lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    return re.sub(r"[^0-9a-z가-힣ぁ-ん一-龥]", "", s)


def chart_now():
    h = get(f"{M}/chart/index.htm")
    rows = []
    for tr in re.findall(r'<tr class="lst(?:50|100)".*?</tr>', h, re.S):
        sid = re.search(r'data-song-no="(\d+)"', tr).group(1)
        rank = int(re.search(r'<span class="rank ">(\d+)</span>', tr).group(1))
        title = html.unescape(re.search(r'rank01"><span>.*?<a [^>]*>(.*?)</a>', tr, re.S).group(1))
        artist = html.unescape(re.search(r'rank02">\s*<a [^>]*>(.*?)</a>', tr, re.S).group(1)).replace("\xa0", " ")
        rows.append({"rank": rank, "title": title, "artist": artist, "song_id": sid})
    return rows


def search_song(title, artist):
    h = get(f"{M}/search/song/index.htm?" + urllib.parse.urlencode({"q": f"{title} {artist}"}))
    for sid in dict.fromkeys(re.findall(r"goSongDetail\('(\d+)'", h)):
        info = song_info(sid)
        if norm(info["title"]) == norm(title) and (norm(artist)[:4] in norm(info["artist"]) or norm(info["artist"])[:4] in norm(artist)):
            return sid
    return None


def song_info(sid):
    p = get(f"{M}/song/detail.htm?songId={sid}")
    t = re.search(r'class="song_name">\s*<strong class="none">곡명</strong>(.*?)</div>', p, re.S)
    a = re.search(r"goArtistDetail\('(\d+)'\)\" title=\"(.*?)\"", p)
    al = re.search(r"goAlbumDetail\('(\d+)'\)", p)
    return {"title": html.unescape(re.sub(r"<[^>]+>|\s+", " ", t.group(1))).strip() if t else "",
            "artist": html.unescape(a.group(2)) if a else "", "artist_id": a.group(1) if a else None,
            "album_id": al.group(1) if al else None, "genre": dd(p, "장르"), "released": dd(p, "발매일")}


CACHE = REPO / "data/weekly_chart/_page_fields.json"  # 아티스트 유형·앨범 기획사 = 잘 안 바뀌는 칸만 저장(같은 페이지 재요청 막기)
_cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


SEED = {}  # --seed: 앞서 같은 기계가 받은 표의 가수명 → 아티스트 유형(다시 묻지 않기)


def field(url, dt, seed=None):
    key = f"{url}#{dt}"
    if key not in _cache and seed:
        _cache[key] = seed
    if key not in _cache:
        try:
            _cache[key] = dd(get(url), dt)
        except urllib.error.HTTPError as e:
            print("미측정", e.code, url, file=sys.stderr)
            return None
        CACHE.write_text(json.dumps(_cache, ensure_ascii=False, indent=0))
    return _cache[key]


def enrich(row):
    info = song_info(row["song_id"])
    row.update(genre=info["genre"], released=info["released"],
               artist_type=field(f"{M}/artist/detail.htm?artistId={info['artist_id']}", "유형", SEED.get(norm(row["artist"]))) if info["artist_id"] else None,
               agency=field(f"{M}/album/detail.htm?albumId={info['album_id']}", "기획사") if info["album_id"] else None,
               url=f"{M}/song/detail.htm?songId={row['song_id']}")
    g, at = row["genre"] or "", row["artist_type"] or ""
    if "트로트" in g: k = 0
    elif "랩/힙합" in g: k = 1
    elif "발라드" in g: k = 2
    elif re.search("록/메탈|인디음악|포크/블루스", g): k = 3
    elif not at: row["gyeol"], row["gyeol_basis"] = "미측정", "장르로 안 갈리고 아티스트 유형 못 받음"; return row
    elif "그룹" in at and "여성" in at: k = 4
    elif "그룹" in at and "남성" in at: k = 5
    else: k = 6
    row["gyeol"], row["gyeol_basis"] = GYEOL_RULES[k]
    return row


def spotify_kr(n):
    h = get("https://kworb.net/spotify/country/kr_weekly.html")
    date = re.search(r"South Korea - (\d{4}/\d\d/\d\d)", h)
    out = []
    for tr in re.findall(r"<tr[^>]*>.*?</tr>", h, re.S)[:n + 1]:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 3 or not tds[0].strip().isdigit(): continue
        art = re.search(r'<a href="\.\./artist/[^"]*">(.*?)</a>', tds[2])
        trk = re.search(r'<a href="\.\./track/[^"]*">(.*?)</a>', tds[2])
        if not (art and trk): continue
        out.append({"rank": int(tds[0]), "artist": html.unescape(art.group(1)), "title": html.unescape(trk.group(1))})
    return (date.group(1) if date else None), out[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("--tsv", help="encore 스냅숏(순위\\t제목\\t가수). 없으면 지금 멜론 차트")
    ap.add_argument("--spotify", type=int, default=0, help="스포티파이 KR 주간 상위 N(0=안 함)")
    ap.add_argument("--seed", help="앞서 받은 표 json(가수 → 아티스트 유형 재사용)")
    a = ap.parse_args()
    if a.seed:
        for r in json.loads(Path(a.seed).read_text())["melon"]:
            if r.get("artist_type"): SEED[norm(r["artist"])] = re.sub(r"\|+", "|", r["artist_type"])
    now = chart_now()
    idx = {(norm(r["title"]), norm(r["artist"])): r["song_id"] for r in now}
    if a.tsv:
        rows = []
        for line in Path(a.tsv).read_text().splitlines():
            if line.startswith("#") or not line.strip(): continue
            rk, t, ar = line.split("\t")[:3]
            rows.append({"rank": int(rk), "title": t, "artist": ar, "song_id": idx.get((norm(t), norm(ar)))})
        source = f"tsv:{a.tsv}"
    else:
        rows, source = now, f"{M}/chart/index.htm @ {time.strftime('%Y-%m-%dT%H:%M%z')}"
    for r in rows:
        if not r["song_id"]:
            r["song_id"] = search_song(r["title"], r["artist"]); r["matched_by"] = "search"
        if r["song_id"]: enrich(r)
    out = {"label": a.label, "source": source, "rules": GYEOL_RULES, "melon": rows,
           "unmatched": [r["rank"] for r in rows if not r["song_id"]]}
    if a.spotify:
        out["spotify_kr_week"], sp = spotify_kr(a.spotify)
        for r in sp:
            r["song_id"] = idx.get((norm(r["title"]), norm(r["artist"]))) or search_song(r["title"], r["artist"])
            if r["song_id"]: enrich(r)
        out["spotify_kr"] = sp
    p = REPO / f"data/weekly_chart/{a.label}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(p, "melon", len(rows), "unmatched", out["unmatched"], "spotify", len(out.get("spotify_kr", [])))


if __name__ == "__main__":
    main()
