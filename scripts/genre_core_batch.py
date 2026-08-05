#!/usr/bin/env python3
"""배치축 귀속 + 배치내 제한 순열 재검정 — 코어 v0의 교락 한계를 닫는다.

사전 등록: docs/genre_core_batch_preregistration.md (★측정 전 작성. 판정 3분기 고정)
지정: kee 08-04 「①배치축 귀속」

왜 하나: 코어 v0의 판정 p=0.0047은 순열 검정인데, 순열은 곡 단위 셔플이 **교환가능**하다는
가정 위에 선다. 같은 배치 곡이 어휘를 공유하면 그 가정이 깨져 **귀무분포가 좁아지고 p가
과대평가**된다. 즉 v0의 근거가 배치 교락일 수 있다.

설계 3가지:
  ⑴ **자를 새로 안 짠다** — R·O 집합은 genre_core_uptake.parse_request/load를 그대로 재사용.
     자를 다시 만들면 코어 v0에서 낸 실패(관측만 정규화)를 반복한다.
  ⑵ **귀속 근거는 비어휘만**(kee 조건 ⑵) — 제목 완전일치로 DB batch를 조회하고,
     BPM(숫자) 대조로 오조인을 거른다. SP 본문·어휘 유사도는 안 쓴다.
     ★오조인은 배치 구조를 흐려 교락을 덜 보이게 만들고 그건 내 기존 결론에 유리한 방향이라
     검증을 건다.
  ⑶ **배치내 제한 순열** — 깨진 축 안에서만 섞는다. 배치가 공유하는 어휘는 실측·귀무 양쪽에
     똑같이 들어가 상쇄되고, 남는 차이만 배치 밖 신호다.

사용:
  python3 scripts/genre_core_batch.py            귀속 + 전제검증 + 제한순열 + 판정
"""
import json
import os
import sys
import collections
import configparser
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from genre_core_uptake import load, parse_request, family

MERGED = ROOT / "data" / "reanalysis_v2" / "merged_4values.json"
OUT = ROOT / "data" / "exchange" / "genre_core_batch_result.json"
DBCONF = os.path.expanduser("~/.config/leofamily_music/db.conf")

MIN_STRATUM = 2      # 크기 2 미만 배치는 섞을 수 없다 — 제외하고 곡수를 적는다
N_PERM = 200


def db_rows(titles):
    """제목 완전일치로 DB의 비어휘 필드만 가져온다(batch·bpm·gid). SP·가사는 안 읽는다."""
    import psycopg2
    c = configparser.ConfigParser()
    c.read(DBCONF)
    s = c[c.sections()[0]] if c.sections() else c["DEFAULT"]
    conn = psycopg2.connect(host=s.get("host"), port=s.get("port"), dbname=s.get("dbname"),
                            user=s.get("user"), password=s.get("password"))
    cur = conn.cursor()
    cur.execute("SELECT title, batch, bpm, global_id FROM songs WHERE title = ANY(%s)", (titles,))
    rows = cur.fetchall()
    conn.close()
    return rows


def attribute(samp, meta):
    """§3.2 — 제목 완전일치 → DB batch. 모호·BPM불일치는 미귀속으로 떨군다.

    반환: (batch_of, 사유별 미귀속 집계)
    """
    titles = {sid: (meta.get(sid, {}).get("title") or "").strip() for sid in samp}
    by_title = collections.defaultdict(list)
    for t, b, bpm, gid in db_rows(sorted({t for t in titles.values() if t})):
        by_title[t].append({"batch": b, "bpm": bpm, "gid": gid})

    # ★미귀속 사유와 「귀속됐으나 BPM 교차검증을 못 건 곡」은 다른 칸이다.
    #   한 칸에 담으면 합이 안 맞고(=조용한 오보고) 조인 신뢰도도 가려진다.
    batch_of, reason = {}, collections.Counter()
    no_bpm_check = []
    detail = []
    for sid in samp:
        t = titles[sid]
        cands = by_title.get(t, [])
        if not t:
            reason["제목없음"] += 1; continue
        if not cands:
            reason["DB 제목 미매칭"] += 1; continue

        # BPM 대조로 먼저 거른다(비어휘 교차확인). 코퍼스 bpm이 없으면 이 필터는 못 건다.
        src_bpm = meta.get(sid, {}).get("bpm")
        if src_bpm:
            ok = [c for c in cands if c["bpm"] == src_bpm]
            if not ok:
                reason["BPM 불일치"] += 1
                detail.append({"song_id": sid, "why": "bpm_mismatch",
                               "corpus_bpm": src_bpm, "db_bpm": [c["bpm"] for c in cands]})
                continue
            cands = ok

        batches = {c["batch"] for c in cands}
        if len(batches) > 1:
            reason["다중 batch 모호"] += 1
            detail.append({"song_id": sid, "why": "ambiguous_batch", "batches": sorted(batches)})
            continue
        batch_of[sid] = batches.pop()
        if not src_bpm:
            no_bpm_check.append(sid)     # 귀속은 됐으나 오조인 교차검증을 못 건 곡
    return batch_of, reason, detail, no_bpm_check


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else 0.0


def premise_check(batch_of, obs):
    """§4.4 — 「배치가 어휘를 공유한다」는 전제부터 잰다. 공유가 없으면 교락도 없다."""
    groups = collections.defaultdict(list)
    for sid, b in batch_of.items():
        groups[b].append(sid)
    within, between = [], []
    keys = sorted(groups)
    for b in keys:
        m = groups[b]
        for i in range(len(m)):
            for j in range(i + 1, len(m)):
                within.append(jaccard(obs[m[i]], obs[m[j]]))
    # 배치간은 결정적 표집(난수 금지) — 배치 순서쌍을 순회하며 첫 곡끼리
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = groups[keys[i]], groups[keys[j]]
            for x in range(min(len(a), len(b), 3)):
                between.append(jaccard(obs[a[x]], obs[b[x]]))
    mean = lambda v: sum(v) / len(v) if v else None
    return {"within_pairs": len(within), "within_mean_jaccard": round(mean(within) or 0, 4),
            "between_pairs": len(between), "between_mean_jaccard": round(mean(between) or 0, 4),
            "gap": round((mean(within) or 0) - (mean(between) or 0), 4),
            "reading": "within > between 이면 배치가 어휘를 공유한다 = 교락 전제 성립. "
                       "차이가 없으면 배치 교락 자체가 없다는 뜻이고 그것도 결론이다."}


def add_rate(songs, obs, RS, pairing, level="term"):
    hit = den = 0
    for sid in songs:
        R = RS[pairing[sid]]
        O = obs[sid]
        if level == "family":
            O, R = {family(t) for t in O}, {family(t) for t in R}
        den += len(O)
        hit += len(O - R)
    return hit / den if den else 0.0


def restricted_perm(batch_of, obs, RS, level="term", min_size=MIN_STRATUM):
    """§4.2 — 배치내 제한 순열. 같은 배치 안에서만 요청층 짝을 회전시킨다.

    ★min_size가 왜 인자인가: 크기 2인 층은 **가능한 비항등 짝짓기가 1개뿐**이라
    모든 순열 회차에서 같은 값을 낸다 → 귀무분포의 분산이 줄고 **p가 또 낙관치**가 된다.
    (코어 v0에서 p를 낙관적으로 낸 것과 **같은 방향의 오류**다.)
    그래서 min_size=4로 다시 돌려 민감도를 본다.
    """
    groups = collections.defaultdict(list)
    for sid, b in batch_of.items():
        groups[b].append(sid)
    usable = {b: sorted(m, key=str) for b, m in groups.items() if len(m) >= min_size}
    dropped = {b: len(m) for b, m in groups.items() if len(m) < min_size}
    songs = [s for m in usable.values() for s in m]
    if not songs:
        return None, usable, dropped

    ident = {s: s for s in songs}
    actual = add_rate(songs, obs, RS, ident, level)

    null = []
    for k in range(1, N_PERM + 1):
        pairing = {}
        for b, m in usable.items():
            n = len(m)
            off = k % n
            if off == 0:                      # 항등 순열은 귀무가 아니다 — 건너뛴다
                off = 1 if n > 1 else 0
            for i, s in enumerate(m):
                pairing[s] = m[(i + off) % n]
        if all(pairing[s] == s for s in songs):
            continue
        null.append(add_rate(songs, obs, RS, pairing, level))
    null.sort()
    le = sum(1 for v in null if v <= actual)
    return ({"level": level, "songs": len(songs), "strata": len(usable),
             "actual_addition": round(actual, 4),
             "null_mean": round(sum(null) / len(null), 4),
             "null_min": round(null[0], 4), "null_max": round(null[-1], 4),
             "n_permutations": len(null), "null_le_actual": le,
             "p_one_sided": round((le + 1) / (len(null) + 1), 4),
             "gap_vs_null_mean_pp": round((sum(null) / len(null) - actual) * 100, 2)},
            usable, dropped)


def unrestricted_perm(songs, obs, RS, level="term"):
    """★대조 필수 — 같은 곡 집합에서 '배치 무시' 순열을 돌린다.

    이게 없으면 v0(425곡·무제한) vs v1(364곡·배치내)의 격차 축소를 전부 '배치 통제 효과'로
    돌리게 되는데, 표본이 425→364로 바뀐 몫이 섞여 있어 **오귀속**이다.
    (같은 종류의 오귀속을 오늘 다른 슬롯이 냈다 — take 축 누락을 배치누출로 귀속.)
    """
    songs = sorted(songs, key=str)
    n = len(songs)
    ident = {s: s for s in songs}
    actual = add_rate(songs, obs, RS, ident, level)
    step = max(1, (n - 1) // N_PERM)
    null = sorted(add_rate(songs, obs, RS,
                           {songs[i]: songs[(i + off) % n] for i in range(n)}, level)
                  for off in range(1, n, step))
    le = sum(1 for v in null if v <= actual)
    return {"level": level, "songs": n, "actual_addition": round(actual, 4),
            "null_mean": round(sum(null) / len(null), 4),
            "n_permutations": len(null), "null_le_actual": le,
            "p_one_sided": round((le + 1) / (len(null) + 1), 4),
            "gap_vs_null_mean_pp": round((sum(null) / len(null) - actual) * 100, 2)}


def main():
    obs, req_txt, req_orig, _ = load()
    samp = sorted((s for s in obs if s in req_txt and obs[s] and req_txt[s]), key=str)
    RS = {sid: parse_request(req_orig[sid]) for sid in samp}
    meta = {r["song_id"]: r for r in json.loads(MERGED.read_text())}

    batch_of, reason, detail, no_bpm_check = attribute(samp, meta)
    unattributed = [s for s in samp if s not in batch_of]

    premise = premise_check(batch_of, obs)
    res_term, usable, dropped = restricted_perm(batch_of, obs, RS, "term")
    res_fam, _, _ = restricted_perm(batch_of, obs, RS, "family")

    # ★민감도 — 순열 자유도가 실제로 있는 층(크기≥4)만으로 다시 판정
    res_s4, usable4, dropped4 = restricted_perm(batch_of, obs, RS, "term", min_size=4)
    sizes = collections.Counter(collections.Counter(batch_of.values()).values())

    # ★격차 축소를 분해한다 — 같은 곡 집합에서 무제한 순열을 돌려 기준선을 잡는다
    same_songs = [s for m in usable.values() for s in m]
    unres = unrestricted_perm(same_songs, obs, RS, "term")
    decomp = None
    if res_term:
        v0_gap, sub_gap, res_gap = 5.33, unres["gap_vs_null_mean_pp"], res_term["gap_vs_null_mean_pp"]
        decomp = {
            "v0_gap_pp_425곡_무제한": v0_gap,
            "동일곡_무제한_gap_pp": sub_gap,
            "동일곡_배치내_gap_pp": res_gap,
            "표본변화_기여_pp": round(sub_gap - v0_gap, 2),
            "★배치통제_기여_pp": round(res_gap - sub_gap, 2),
            "reading": "v0→v1 축소를 전부 배치 탓으로 돌리면 오귀속이다. 표본이 425→364로 "
                       "바뀐 몫과 배치를 통제한 몫을 갈라 적는다.",
        }

    # ── §5 판정 — 사전등록한 3분기. 값 보고 고르지 않는다 ──────────────────────
    if res_term is None or len(usable) < 2:
        verdict = "C. 미판정 — 교락 미분리(귀속 부족 또는 단층). A로도 B로도 쓰지 않는다"
    elif res_term["null_le_actual"] == 0:
        verdict = ("A. 생존 — 배치내 제한 순열에서도 실측이 귀무분포 아래. "
                   "코어 v0 결론 유지, 단 p는 v1로 교체(v0 p=0.0047은 폐기)")
    else:
        verdict = ("B. 붕괴 — 제한 순열 귀무분포 안으로 실측이 들어옴. "
                   "★코어 v0의 판정 근거가 배치 교락이었다. 결론 철회")

    out = {
        "generated_by": "scripts/genre_core_batch.py",
        "preregistration": "docs/genre_core_batch_preregistration.md",
        "verdict": verdict,
        "attribution": {
            "sample": len(samp),
            "attributed": len(batch_of),
            "attributed_pct": round(len(batch_of) / len(samp) * 100, 1),
            "unattributed": len(unattributed),
            "unattributed_reasons": dict(reason),
            "reasons_sum_check": sum(reason.values()),
            "attributed_but_bpm_uncheckable": {
                "곡수": len(no_bpm_check),
                "뜻": "귀속은 됐으나 코퍼스 bpm이 없어 오조인 교차검증을 못 건 곡. "
                      "미귀속이 아니라 ★검증 약한 귀속이다 — 미귀속 칸에 넣으면 합이 안 맞는다",
            },
            "method": "제목 완전일치 → songs.batch, BPM(숫자) 대조로 오조인 제거, 다중 batch는 미귀속",
            "non_lexical_note": "SP 본문·가사·어휘 유사도 미사용. DB에서 읽은 것은 title/batch/bpm/global_id뿐",
            "distinct_batches": len(set(batch_of.values())),
            "strata_usable": len(usable), "strata_dropped_lt2": dropped,
            "★통제_불가_확정": {
                "곡수": len(unattributed),
                "판정": "「배제 못 함」이 아니라 「배제 불가임을 확인함」",
                "시도한_근거": {
                    "suno_reanalysis uuid → DB": "0% — 재분석 클립 id지 생성곡 id가 아님",
                    "leomusic_original.source_gid/source_batch": "표본 내 0%",
                    "series / song_id 접두": "59곡(13.9%)만 보유",
                    "제목 완전일치 → DB batch": "주경로. 위 사유별 집계 참조",
                },
                "표본_예시": detail[:15],
            },
        },
        "premise_check_배치가_어휘를_공유하는가": premise,
        "restricted_permutation": {"term": res_term, "family": res_fam,
                                   "note": "배치내에서만 섞음. 배치 공유 어휘는 실측·귀무 양쪽에 "
                                           "들어가 상쇄되고 남는 차이만 배치 밖 신호"},
        "unrestricted_same_songs": unres,
        "gap_decomposition": decomp,
        "★민감도_순열자유도": {
            "stratum_size_dist": {str(k): v for k, v in sorted(sizes.items())},
            "문제": "크기 2인 층은 비항등 짝짓기가 1개뿐이라 매 회차 같은 값을 낸다 → "
                    "귀무분포 분산이 줄어 p가 낙관치가 된다(코어 v0과 같은 방향의 오류)",
            "size2_strata": sizes.get(2, 0), "size2_songs": sizes.get(2, 0) * 2,
            "min_size4_재판정": res_s4,
            "읽는_법": "크기≥4 층만으로도 실측이 귀무분포 아래면 결론이 자유도 부족에 기댄 게 아니다. "
                       "들어오면 주판정(min_size=2)은 자유도 부족 때문일 수 있다",
        },
        "v0_comparison": {"v0_p": 0.0047, "v0_gap_pp": 5.33,
                          "v0_note": "전체 시프트(교환가능성 가정) — 배치 구조가 섞여 귀무분포가 좁았음"},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    a = out["attribution"]
    print(f"[귀속] 표본 {a['sample']} → 귀속 {a['attributed']} ({a['attributed_pct']}%) / "
          f"미귀속 {a['unattributed']}")
    for k, v in a["unattributed_reasons"].items():
        print(f"    미귀속 사유 {k}: {v}")
    print(f"    배치 {a['distinct_batches']}종 · 순열 가능 층 {a['strata_usable']} · "
          f"크기<2 제외 {sum(dropped.values())}곡")
    p = out["premise_check_배치가_어휘를_공유하는가"]
    print(f"\n[전제] 배치내 자카드 {p['within_mean_jaccard']} vs 배치간 {p['between_mean_jaccard']} "
          f"→ 격차 {p['gap']:+.4f}")
    print("\n[제한 순열] 배치 안에서만 섞음")
    for r in (res_term, res_fam):
        if r:
            print(f"  {r['level']:<7} 실측 {r['actual_addition']:.4f} · 귀무 {r['null_mean']:.4f} "
                  f"[{r['null_min']:.4f}~{r['null_max']:.4f}] n={r['n_permutations']} "
                  f"· p={r['p_one_sided']:.4f} · 격차 {r['gap_vs_null_mean_pp']:+.2f}%p")
    print("\n[민감도] 순열 자유도 — 크기 2인 층은 가능한 짝짓기가 1개뿐")
    print(f"  층 크기 분포: {dict(sorted(sizes.items()))}")
    if res_s4:
        print(f"  크기≥4만({res_s4['songs']}곡·{res_s4['strata']}층) 실측 {res_s4['actual_addition']:.4f} "
              f"· 귀무 {res_s4['null_mean']:.4f} [{res_s4['null_min']:.4f}~{res_s4['null_max']:.4f}] "
              f"· p={res_s4['p_one_sided']:.4f} · 격차 {res_s4['gap_vs_null_mean_pp']:+.2f}%p")
    if decomp:
        print("\n[격차 분해] ★축소를 전부 배치 탓으로 돌리지 않는다")
        print(f"  v0 425곡 무제한   {decomp['v0_gap_pp_425곡_무제한']:+.2f}%p")
        print(f"  동일 364곡 무제한 {decomp['동일곡_무제한_gap_pp']:+.2f}%p"
              f"   (표본변화 기여 {decomp['표본변화_기여_pp']:+.2f}%p)")
        print(f"  동일 364곡 배치내 {decomp['동일곡_배치내_gap_pp']:+.2f}%p"
              f"   (★배치통제 기여 {decomp['★배치통제_기여_pp']:+.2f}%p)")
    print(f"\n★판정: {verdict}")
    print(f"\n→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
