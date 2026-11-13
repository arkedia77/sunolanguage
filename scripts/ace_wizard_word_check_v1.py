#!/usr/bin/env python3
"""ace_wizard_word_check_v1.py — ACE 마법사 SP(encore 222908) 낱말이 Suno 채널에 몇 곡 나오나 · 축자 정규식 · 곡 단위 · 채널 합산 0 · 쓰기 0."""
import sys, re, json, collections, sqlite3
sys.path.insert(0, "/Users/purple/sunolanguage/scripts")
import build_suno_phrase_dict_v2 as B
T = {'drift phonk': r"\b(?:drift phonk)",'phonk': r"\b(?:phonk)",'memphis': r"\b(?:memphis)",'cowbell': r"\b(?:cowbell)",'808': r"\b(?:808)",'halftime|half-time': r"\b(?:halftime|half-time)",'eerie': r"\b(?:eerie)",'vinyl crackle': r"\b(?:vinyl crackle)",'telephone': r"\b(?:telephone)",'chopped[ -]and[ -]screwed': r"\b(?:chopped[ -]and[ -]screwed)",'pitched[ -]down': r"\b(?:pitched[ -]down)",'overdriven': r"\b(?:overdriven)",'wall of bass': r"\b(?:wall of bass)",'relentless': r"\b(?:relentless)",'piercing': r"\b(?:piercing)",'weaves?': r"\b(?:weaves?)",'embrac': r"\b(?:embrac)",'erupts?': r"\b(?:erupts?)",'explodes?': r"\b(?:explodes?)",'retreats?': r"\b(?:retreats?)",'cuts abruptly|abrupt': r"\b(?:cuts abruptly|abrupt)",'intentional': r"\b(?:intentional)",'midground': r"\b(?:midground)",'bandpass': r"\b(?:bandpass)",'abrasive': r"\b(?:abrasive)",'murky': r"\b(?:murky)",'blown[ -]out': r"\b(?:blown[ -]out)",'sidechain': r"\b(?:sidechain)",'tape saturation|tape-saturated': r"\b(?:tape saturation|tape-saturated)",'in the (back|mid|fore)ground': r"\b(?:in the (back|mid|fore)ground)"}
T = {k: re.compile(v) for k, v in T.items()}
def m(t):
    t = (t or "").lower().replace("’", "'")
    return {k for k, rx in T.items() if rx.search(t)}
df = {c: collections.Counter() for c in ("V+","V-","Vkeep","HS","HU","HD","LS","AG","OD")}
ex = collections.defaultdict(dict); n = collections.Counter()
def add(ch, ks, e):
    n[ch] += 1
    for k in ks: df[ch][k] += 1; ex[k].setdefault(ch, e)
for s in json.loads(B.VAR.read_text())["songs"]:
    if not s.get("sp_sent"): continue
    cl = [c for c in s["clips"] if c.get("sp_suno")]
    if not cl: continue
    sent = m(s["sp_sent"]); per = [(c["clip"], m(c["sp_suno"])) for c in cl]
    allu = set().union(*(u for _, u in per)); n["V"] += 1
    for k in allu - sent: df["V+"][k] += 1; ex[k].setdefault("V+", next(c for c, u in per if k in u))
    for k in sent - allu: df["V-"][k] += 1
    for k in sent & allu: df["Vkeep"][k] += 1
for s in json.loads(B.REFS.read_text())["songs"]:
    st = s.get("style") or ""
    sw = bool(s.get("gpt_description_prompt")) or s.get("task") == "agentic_thinking"
    if st.strip(): add("HS" if sw else "HU", m(st), s["id"])
    if s.get("display_tags"): add("HD", m(s["display_tags"]), s["id"])
db = sqlite3.connect("/Users/purple/sunolanguage/sunolang.db")
for tid, p in db.execute("select id, suno_prompt from tracks where suno_prompt is not null and trim(suno_prompt)!=''"): add("LS", m(p), f"tracks:{tid}")
from json_to_db import get_conn
cur = get_conn().cursor()
cur.execute("select clip_uuid::text, sp_suno from suno_clip_style where gen_method='agentic_remix' and sp_suno is not null")
ag = {}
for cu, sp in cur.fetchall(): ag.setdefault(sp.strip(), cu)
for sp, cu in ag.items(): add("AG", m(sp), cu)
cur.execute("select min(clip_uuid::text), string_agg(display_tags, ', ') from suno_clip_style where display_tags is not null and display_tags<>'' group by global_id")
for cu, dt in cur.fetchall(): add("OD", m(dt), cu)
print("분모", dict(n))
for k in T:
    print(f"{k:36s}", " ".join(f"{c}={df[c][k]}" for c in df if c not in ("OD",)))
