#!/usr/bin/env python3
"""코어(관측 좌표) v0 실측 — 관측층은 요청층 말고 무엇을 더 말하는가.

사전 등록: docs/genre_core_v0_preregistration.md (★측정 전 작성분. 지표·통제·기각조건 고정)

핵심 설계 2가지만 기억하면 된다.
  ⑴ 요청층과 관측층을 **같은 자(단일 어휘집 L)**로 잰다 — 다른 자를 대면
     차이가 '자의 차이'인지 '층의 차이'인지 안 갈린다.
  ⑵ **짝 섞기 대조군**이 없으면 측정 안 한 것과 같다 — 악기 어휘는 흔해서
     "요청 SP에 piano가 있었다"만으로는 인과가 안 선다. 실측치−우연치만 신호다.

★자기적발(08-04, 1차 측정 직후) — 나는 ⑴을 써놓고 ⑴을 어겼다.
  1차판은 **관측만** v3 파서로 정규화하고 **요청은 원문 문자열**을 댔다. 그래서
  요청 `soft synth pads` ↔ 관측 `synthesizer`가 불일치로 세어졌다(같은 걸 가리키는데도).
  이건 사전등록 §4에 적어둔 '부분문자열 매칭은 거칠다'가 아니라 **설계 원칙 위반**이다.
  방향까지 적어 둔다: 이 위반은 실측·우연 **양쪽**의 일치를 함께 깎으므로 격차를 **0으로 끌어당긴다**
  (감쇠). 즉 1차판 격차 4.65%p는 과대가 아니라 **과소**일 수 있다.
  → mode=parsed(v0.1)에서 **같은 파서 사전(INSTRUMENT_ENTITIES)을 요청층에도 건다**.
  1차판 수치는 지우지 않고 mode=raw로 남겨 병기한다.

사용:
  python3 scripts/genre_core_uptake.py            v0.1(parsed) + v0(raw) 병기 측정
  python3 scripts/genre_core_uptake.py --sample   수기 점검용 표본 20건 출력
"""
import json
import re
import sqlite3
import sys
import collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_slot_entities_v3 import INSTRUMENT_ENTITIES, INSTRUMENT_FAMILY, find_entities

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "reanalysis_v2" / "lexical_index.sqlite"
MERGED = ROOT / "data" / "reanalysis_v2" / "merged_4values.json"
OUT = ROOT / "data" / "exchange" / "genre_core_uptake_result.json"

# 짝 섞기 대조군의 시프트량. 결정적(고정) — 난수 안 쓴다(재현성).
SHIFT = 197
# 부분문자열 오탐을 줄이는 최소 길이. 3자 이하 토큰('sax' 등)은 경계매칭으로만 인정.
MIN_FREE_LEN = 4


def norm(s):
    """정규화: 소문자·하이픈→공백·연속공백 1칸·앞뒤공백 제거."""
    return re.sub(r"\s+", " ", s.replace("-", " ").lower()).strip()


def unpack(raw):
    """entity 컬럼은 평문 또는 JSON 배열 문자열 둘 다 온다. 항상 리스트로 편다."""
    if not raw:
        return []
    raw = raw.strip()
    if raw.startswith("["):
        try:
            v = json.loads(raw)
            return [str(x) for x in v] if isinstance(v, list) else [str(v)]
        except json.JSONDecodeError:
            return []
    return [raw]


def load():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 관측층 — suno_sp_full 파싱분. 악기 슬롯만(사전등록 §2.1).
    obs = collections.defaultdict(set)
    cur.execute("SELECT song_id, entity FROM entries "
                "WHERE source='sp_entity' AND slot='instrument' AND entity IS NOT NULL")
    for sid, ent in cur.fetchall():
        for e in unpack(ent):
            t = norm(e)
            if t:
                obs[sid].add(t)

    # 요청층 — DB에 파싱본이 없는 층이라 원문을 그대로 받는다.
    #   raw  : 소문자·하이픈제거 정규화본 (v0 부분문자열 매칭용)
    #   parse: ★무가공 원문 (v0.1 파서용 — 파서 패턴이 하이픈에 의존하므로 정규화하면 안 된다)
    cur.execute("SELECT song_id, sentence FROM entries WHERE source='leomusic_sp_full'")
    req_txt, req_orig = {}, {}
    for sid, s in cur.fetchall():
        req_txt[sid] = norm(s or "")
        req_orig[sid] = s or ""

    # 관측 장르 라벨 — 분해용(층 표기: observed)
    cur.execute("SELECT song_id, entity FROM entries "
                "WHERE source='sp_entity' AND slot='genre' AND entity IS NOT NULL")
    obs_genre = {sid: (unpack(e)[0] if unpack(e) else "") for sid, e in cur.fetchall()}

    con.close()
    return obs, req_txt, req_orig, obs_genre


def present(term, text):
    """[v0/raw] 어휘 t가 요청 SP 원문에 있는가. 짧은 토큰은 단어경계 강제(오탐 억제).

    ★비대칭 자(尺). 관측층은 파서를 거쳤는데 이쪽은 원문이다. 감쇠 편향이 있다 — 병기용으로만 남긴다.
    """
    if not text:
        return False
    if len(term) >= MIN_FREE_LEN:
        return term in text
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def parse_request(text):
    """[v0.1/parsed] 요청 SP에 **관측층과 동일한 파서 사전**을 걸어 정규화 엔티티를 뽑는다.

    파서가 SP를 문장 단위로 도는 것을 그대로 흉내낸다(find_entities의 포괄어 제거가
    문장 문맥에 종속되므로, 전문을 한 덩어리로 넣으면 관측층과 다른 자가 된다).
    """
    ents = set()
    for sent in re.split(r"[.\n]+", text):
        sent = sent.strip()
        if sent:
            ents.update(norm(e) for e in find_entities(sent, INSTRUMENT_ENTITIES))
    return {e for e in ents if e}


def measure(mode, obs, req_txt, req_orig, obs_genre):
    """mode='parsed'(v0.1, 양쪽 동일 파서) | 'raw'(v0, 요청은 원문 부분문자열 — 병기용)."""
    # 분석 표본 = 관측 악기 ∧ 요청 원문 동시 보유 (사전등록 §1)
    # song_id는 int/str 혼재(1 … 'S018_16') — 정렬 키를 str로 통일한다.
    songs = sorted((s for s in obs if s in req_txt and obs[s] and req_txt[s]), key=str)
    excluded_no_req = sorted((s for s in obs if s not in req_txt), key=str)

    # 단일 어휘집 L — 코퍼스 전체 관측 악기 엔티티 (표본 아닌 497곡 전체에서)
    L = sorted({t for s in obs for t in obs[s]})
    Lfreq = collections.Counter(t for s in obs for t in obs[s])

    # ★R을 곡마다 한 번만 확정한다. 이후 모든 분해가 이 한 집합을 참조한다
    #   — 지표마다 매칭을 따로 재구현하면 정의가 갈린다(전 세션 recompute 통합 교훈).
    if mode == "parsed":
        RSET = {sid: parse_request(req_orig[sid]) for sid in songs}
    else:
        RSET = {sid: {t for t in L if present(t, req_txt[sid])} for sid in songs}

    # 짝 섞기 대조군: 곡 i의 O를 곡 (i+SHIFT)%n 의 요청 SP와 대조
    n = len(songs)
    shuffled = {songs[i]: songs[(i + SHIFT) % n] for i in range(n)}

    rows = []
    for sid in songs:
        O = obs[sid]
        R = RSET[sid]
        Rc = RSET[shuffled[sid]]
        rows.append({
            "song_id": sid,
            "n_obs": len(O), "n_req": len(R),
            "uptake_hit": len(R & O), "uptake_den": len(R),
            "add_hit": len(O - R), "add_den": len(O),
            "c_uptake_hit": len(Rc & O), "c_uptake_den": len(Rc),
            "c_add_hit": len(O - Rc), "c_add_den": len(O),
            "req_len": len(req_txt[sid]),
            "observed_genre": obs_genre.get(sid, ""),
        })

    def ratio(num_k, den_k):
        num = sum(r[num_k] for r in rows)
        den = sum(r[den_k] for r in rows)
        return (num / den if den else 0.0), num, den

    uptake, u_n, u_d = ratio("uptake_hit", "uptake_den")
    addition, a_n, a_d = ratio("add_hit", "add_den")
    c_uptake, cu_n, cu_d = ratio("c_uptake_hit", "c_uptake_den")
    c_addition, ca_n, ca_d = ratio("c_add_hit", "c_add_den")

    # ── 부가 어휘 순위 — 관측에만 있고 그 곡 요청엔 없던 어휘 ──────────────────
    add_counter = collections.Counter()
    own_counter = collections.Counter()
    for sid in songs:
        for t in obs[sid]:
            own_counter[t] += 1
            if t not in RSET[sid]:
                add_counter[t] += 1
    # 어휘별 부가율 = 그 어휘가 관측될 때 요청에 없었던 비율
    per_term = [{"term": t, "observed_in": own_counter[t], "added_in": add_counter[t],
                 "add_rate": round(add_counter[t] / own_counter[t], 4)}
                for t in own_counter if own_counter[t] >= 10]
    per_term.sort(key=lambda x: (-x["added_in"], -x["add_rate"]))

    # ── 교락 분해: L 빈도 십분위 (흔한 어휘일수록 우연히 맞을 확률↑) ───────────
    ranked = [t for t, _ in Lfreq.most_common()]
    decile_of = {t: min(9, (i * 10) // max(1, len(ranked))) for i, t in enumerate(ranked)}
    dec = collections.defaultdict(lambda: {"obs": 0, "added": 0})
    for sid in songs:
        for t in obs[sid]:
            d = dec[decile_of.get(t, 9)]
            d["obs"] += 1
            if t not in RSET[sid]:
                d["added"] += 1
    decile_rows = [{"decile": k, "observed": v["obs"], "added": v["added"],
                    "add_rate": round(v["added"] / v["obs"], 4) if v["obs"] else None}
                   for k, v in sorted(dec.items())]

    # ── 교락 분해: 인스트루멘탈 / 배치(통제 가능분만) ─────────────────────────
    meta = {r["song_id"]: r for r in json.loads(MERGED.read_text())}
    def split_by(keyfn, label):
        g = collections.defaultdict(lambda: {"obs": 0, "added": 0, "songs": 0})
        for sid in songs:
            k = keyfn(meta.get(sid, {}))
            if k is None:
                continue
            b = g[k]
            b["songs"] += 1
            for t in obs[sid]:
                b["obs"] += 1
                if t not in RSET[sid]:
                    b["added"] += 1
        return {"axis": label, "groups": [
            {"key": str(k), "songs": v["songs"], "observed": v["obs"], "added": v["added"],
             "add_rate": round(v["added"] / v["obs"], 4) if v["obs"] else None}
            for k, v in sorted(g.items(), key=lambda x: -x[1]["songs"])]}

    inst_split = split_by(lambda m: m.get("is_instrumental") if "is_instrumental" in m else None,
                          "is_instrumental")
    batch_split = split_by(lambda m: m.get("series"), "series(배치)")

    # L의 요청 SP 커버리지 — 채택율 상한 편향의 크기 (사전등록 §4)
    req_tokens = collections.Counter()
    for sid in songs:
        for t in RSET[sid]:
            req_tokens[t] += 1
    l_cov = {"L_size": len(L),
             "L_terms_seen_in_any_request": sum(1 for t in L if req_tokens[t] > 0),
             "requested_terms_outside_L": sorted(set(req_tokens) - set(L)),
             "note": "L은 관측에서 뽑았다 — 요청에만 있고 Suno가 한 번도 안 쓴 어휘는 애초에 안 세어진다"}

    result = {
        "mode": mode,
        "mode_note": {"parsed": "v0.1 — 요청·관측 양쪽에 동일 파서 사전(INSTRUMENT_ENTITIES) 적용. 정본",
                      "raw": "v0 — 요청은 원문 부분문자열. ★비대칭 자, 격차를 0으로 감쇠시킴. 병기용"}[mode],
        "generated_by": "scripts/genre_core_uptake.py",
        "preregistration": "docs/genre_core_v0_preregistration.md",
        "layer_note": "R=requested(leomusic_sp_full) / O=observed(suno_sp_full 파싱 instrument). 층 혼용 금지.",
        "sample": {
            "population_with_observed": len(obs),
            "analyzed": n,
            "excluded_no_requested_sp": len(excluded_no_req),
            "scope": "leomusic 생성곡. 수집 코퍼스·encore 모집단에 외삽 금지",
        },
        "lexicon": l_cov,
        "metrics": {
            "uptake": {"value": round(uptake, 4), "hit": u_n, "den": u_d,
                       "means": "요청한 악기가 관측에 살아남은 비율"},
            "chance_uptake": {"value": round(c_uptake, 4), "hit": cu_n, "den": cu_d},
            "uptake_lift_pp": round((uptake - c_uptake) * 100, 2),
            "addition": {"value": round(addition, 4), "hit": a_n, "den": a_d,
                         "means": "관측 악기 중 그 곡 요청엔 없던 비율"},
            "chance_addition": {"value": round(c_addition, 4), "hit": ca_n, "den": ca_d},
            "addition_gap_pp": round((c_addition - addition) * 100, 2),
        },
        "reject_gate": {
            "rule_1": "부가율 − 우연부가율 ≤ 5%p 이면 코어 폐기 (사전등록 §3-1)",
            "rule_1_note": "부가율은 낮을수록 요청 반영이 큰 값이므로, 우연부가율이 실측보다 "
                           "높아야 신호. 격차(chance−actual)를 본다.",
        },
        "confounds": {"frequency_decile": decile_rows,
                      "instrumental": inst_split,
                      "batch": batch_split,
                      "batch_controllable": "series 보유 곡만. 미보유분은 통제 불가 — 불가라고 적는다"},
        "top_added_terms": per_term[:40],
        "per_song": rows,
    }
    return result


def report(res):
    s, m, l = res["sample"], res["metrics"], res["lexicon"]
    print(f"[{res['mode']}] 표본 {s['analyzed']}곡 "
          f"(관측보유 {s['population_with_observed']} / 요청SP부재 제외 {s['excluded_no_requested_sp']})")
    print(f"  어휘집 L={l['L_size']}종 · 요청층에 한 번이라도 등장 {l['L_terms_seen_in_any_request']}종")
    print(f"  채택율 {m['uptake']['value']:.3f} ({m['uptake']['hit']}/{m['uptake']['den']})"
          f"  우연 {m['chance_uptake']['value']:.3f}  → 리프트 {m['uptake_lift_pp']:+.2f}%p")
    print(f"  부가율 {m['addition']['value']:.3f} ({m['addition']['hit']}/{m['addition']['den']})"
          f"  우연 {m['chance_addition']['value']:.3f}  → 격차 {m['addition_gap_pp']:+.2f}%p")


def family(t):
    return INSTRUMENT_FAMILY.get(t, "other")


def robustness(obs, req_orig, songs):
    """게이트를 0.29%p 차로 통과했다. 그 폭으로는 코어를 못 세운다 — 두 가지를 더 본다.

    ⑴ **귀무분포** — 짝섞기를 SHIFT 1회로 끝내면 그건 우연치의 표본 1개일 뿐이다.
       여러 시프트로 분포를 만들어 실측이 그 분포 밖인지 본다.
       ★이건 '효과가 있나(유의)'를 재는 것이지 '효과가 큰가'를 재는 게 아니다. 둘을 안 섞는다.
    ⑵ **입도(granularity) 아티팩트 차감** — 요청 `warm lo-fi guitar`(파서→`guitar`)에
       관측 `electric guitar`가 오면 어휘 단위로는 '부가'로 세어진다. 진짜 부가가 아니라
       입도 차이일 수 있다. 그래서 **패밀리 단위**로 다시 센다(사전등록 §3-2 차감 재판정).
    """
    RS = {sid: parse_request(req_orig[sid]) for sid in songs}
    n = len(songs)

    def add_rate(offset, level):
        hit = den = 0
        for i, sid in enumerate(songs):
            R = RS[songs[(i + offset) % n]] if offset else RS[sid]
            if level == "family":
                O, Rf = {family(t) for t in obs[sid]}, {family(t) for t in R}
            else:
                O, Rf = obs[sid], R
            den += len(O)
            hit += len(O - Rf)
        return hit / den if den else 0.0

    out = {}
    for level in ("term", "family"):
        actual = add_rate(0, level)
        # 시프트 1..n-1 중 199개를 균등 간격으로 — 결정적, 난수 안 씀
        step = max(1, (n - 1) // 199)
        null = sorted(add_rate(o, level) for o in range(1, n, step))
        worse = sum(1 for v in null if v <= actual)
        out[level] = {
            "actual_addition": round(actual, 4),
            "null_mean": round(sum(null) / len(null), 4),
            "null_min": round(null[0], 4), "null_max": round(null[-1], 4),
            "n_permutations": len(null),
            "null_le_actual": worse,
            "p_one_sided": round((worse + 1) / (len(null) + 1), 4),
            "gap_vs_null_mean_pp": round((sum(null) / len(null) - actual) * 100, 2),
        }
    out["reading"] = (
        "term 격차가 family에서 무너지면 어휘단위 '부가'는 입도 아티팩트였다는 뜻. "
        "유지되면 부가는 입도가 아니라 악기 자체의 부가다.")

    # ── 악기족별 분해 — 전체 5%p가 어디서 나오는지. 족마다 우연치가 다르므로 각각 대조한다 ──
    fam = collections.defaultdict(lambda: {"obs": 0, "added": 0, "c_added": 0})
    ctrl = songs[len(songs) // 3:] + songs[:len(songs) // 3]   # 결정적 대조 짝
    for i, sid in enumerate(songs):
        R, Rc = RS[sid], RS[ctrl[i]]
        for t in obs[sid]:
            b = fam[family(t)]
            b["obs"] += 1
            b["added"] += t not in R
            b["c_added"] += t not in Rc
    # ★절대격차와 상대배수는 다른 이야기를 한다 — bass는 격차 최대인데 배수 최소다.
    #   하나만 적으면 반드시 오독된다. 둘 다 남긴다.
    rows = []
    for k, v in fam.items():
        if v["obs"] < 30:
            continue
        share = (v["obs"] - v["added"]) / v["obs"]        # 관측분 중 실제로 요청했던 비율
        c_share = (v["obs"] - v["c_added"]) / v["obs"]    # 같은 값의 우연 기대치
        rows.append({"family": k, "observed": v["obs"],
                     "add_rate": round(v["added"] / v["obs"], 4),
                     "chance_add_rate": round(v["c_added"] / v["obs"], 4),
                     "gap_pp": round((c_share - share) * -100, 2),
                     "requested_share": round(share, 4),
                     "chance_share": round(c_share, 4),
                     "lift_ratio": round(share / c_share, 2) if c_share else None})
    out["per_family"] = sorted(rows, key=lambda x: -x["observed"])
    out["per_family_note"] = ("gap_pp=절대격차 / lift_ratio=상대배수. "
                              "bass는 절대격차 최대·상대배수 최소 — 한쪽만 적으면 오독된다.")
    return out


def main():
    obs, req_txt, req_orig, obs_genre = load()
    parsed = measure("parsed", obs, req_txt, req_orig, obs_genre)
    raw = measure("raw", obs, req_txt, req_orig, obs_genre)

    songs = sorted((s for s in obs if s in req_txt and obs[s] and req_txt[s]), key=str)
    rob = robustness(obs, req_orig, songs)

    gap = parsed["metrics"]["addition_gap_pp"]
    fam_gap = rob["family"]["gap_vs_null_mean_pp"]
    if gap <= 5.0:
        verdict = "REJECT — 사전등록 §3-1 발동, 관측층은 요청층의 메아리"
    elif fam_gap <= 5.0:
        verdict = ("HELD — 어휘단위는 게이트를 넘으나(+%.2f%%p) 패밀리단위에서 무너짐(+%.2f%%p). "
                   "사전등록 §3-2 차감 재판정 결과 '부가'의 상당분이 입도 아티팩트." % (gap, fam_gap))
    else:
        verdict = "PASS — 어휘·패밀리 양 입도에서 게이트 통과"
    out = {"primary": "parsed",
           "verdict": {"gate": "사전등록 §3-1: 부가율 격차(우연−실측) ≤ 5%p 이면 코어 폐기",
                       "parsed_gap_pp": gap, "raw_gap_pp": raw["metrics"]["addition_gap_pp"],
                       "family_gap_pp": fam_gap,
                       "result": verdict,
                       "margin_note": "★어휘단위 통과폭이 %.2f%%p뿐이다. 통과했다고 튼튼한 게 아니다."
                                      % (gap - 5.0),
                       "note": "raw는 비대칭 자라 격차를 0으로 감쇠시킨다. 판정은 parsed로만 한다."},
           "robustness": rob, "parsed": parsed, "raw": raw}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    report(parsed)
    print()
    report(raw)
    print("\n[강건성] 짝섞기 귀무분포 (결정적 시프트)")
    for lv in ("term", "family"):
        r = rob[lv]
        print(f"  {lv:<7} 실측부가 {r['actual_addition']:.4f} · 귀무 평균 {r['null_mean']:.4f} "
              f"[{r['null_min']:.4f}~{r['null_max']:.4f}] n={r['n_permutations']} "
              f"· p={r['p_one_sided']:.4f} · 격차 {r['gap_vs_null_mean_pp']:+.2f}%p")
    print("\n[악기족별] 관측 중 '요청했던' 비율 vs 우연치 — 절대격차와 상대배수 병기")
    for r in rob["per_family"]:
        print(f"  {r['family']:<9} n={r['observed']:>4}  요청분 {r['requested_share']:.3f} vs "
              f"우연 {r['chance_share']:.3f}  → {r['gap_pp']:+.2f}%p · {r['lift_ratio']}배")
    print(f"\n★게이트: parsed 격차 {gap:+.2f}%p / family {fam_gap:+.2f}%p\n  → {verdict}")
    print("\n부가 상위 12 (parsed):")
    for r in parsed["top_added_terms"][:12]:
        print(f"  {r['term']:<30} 관측 {r['observed_in']:>3}곡 중 부가 {r['added_in']:>3} "
              f"({r['add_rate']:.2f})")
    print(f"\n→ {OUT.relative_to(ROOT)}")


def sample():
    """수기 오탐 점검용 20건 (사전등록 §4)."""
    obs, req_txt, req_orig, _ = load()
    songs = sorted((s for s in obs if s in req_txt and obs[s] and req_txt[s]), key=str)
    for sid in songs[::max(1, len(songs) // 20)][:20]:
        R = parse_request(req_orig[sid])
        print(f"\n=== {sid} ===")
        print(f"  요청 파싱: {sorted(R)}")
        print(f"  관측     : {sorted(obs[sid])}")
        print(f"  ★미채택  : {sorted(R - obs[sid])}")
        print(f"  ★부가    : {sorted(obs[sid] - R)}")


if __name__ == "__main__":
    sample() if "--sample" in sys.argv else main()
