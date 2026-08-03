#!/usr/bin/env python
"""분리력 검사 v2 — ★교락(confound) 분리 설계.

v1(08-03)의 한계: 표본 18곡 전량이 단일배치 S_PU → '장르 효과'와 '배치(SP 작성 스타일) 효과'를
분리할 수 없었다. centroid F비 26이 장르를 잰 것인지 배치를 잰 것인지 증명 불가.

v2 설계(sunomusic 매핑 인덱스 5,754행 수령으로 가능해짐):
  ①곡당 take1만(같은 곡 2take=유사 표본 중복계상 방지)
  ②장르당 표본을 **서로 다른 배치**에서 뽑음(배치 다양성 최대화)
  ③3중 검정:
     F_genre        = 장르 간/내 분산비            (장르가 가르는가)
     F_batch_within = 장르 내부에서 배치 간/내 분산비 (배치가 가르는가 — 교락 지표)
     F_balladfam    = 발라드 3종족만의 분산비        (★변별 검정)
        → 장르 탐지기라면 발라드끼리도 갈라야 한다.
          못 가르면 그 지표는 '장르 정체'가 아니라 '편곡 밀도 계층'을 재는 것 = 재명명 유지가 옳음.

라벨=design_intent(SP 지정값). 오디오=cdn_mp3 폴백(NAS 미마운트). 산출=lab/probe_v2_results.json
사용: .venv/bin/python lab/probe_genre_v2.py inbox/aware_clip_index.jsonl [N_PER_GENRE]
"""
import sys, os, json, re, time, collections, urllib.request
import numpy as np
import librosa

CACHE = os.path.join(os.path.dirname(__file__), 'audio_cache')
OUT = os.path.join(os.path.dirname(__file__), 'probe_v2_results.json')
EXCERPT_S = 60
SLEEP = 0.7  # CDN 예의(동시성 1·간격 유지 — sunomusic 가이드 2~4 이내)

GENRES = ["trot", "city pop", "korean ballad", "piano ballad", "ballad", "synth pop", "hip-hop"]
BALLAD_FAM = ["korean ballad", "piano ballad", "ballad"]


def norm(g):
    if not g:
        return None
    return re.split(r'\s*[/,]\s*', g.strip())[0].strip().lower()


def pick(rows, n_per, per_batch=2):
    """장르당 n_per개를 '배치당 per_batch곡'으로 — ★배치 효과를 잴 수 있어야 하므로
    한 배치에서 최소 2곡을 뽑는다(배치당 1곡이면 배치 내 분산이 정의되지 않아 교락 측정 불가).
    남는 자리는 1곡짜리 배치로 채워 분산도를 유지한다."""
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r.get('take') != 'take1' or not r.get('cdn_mp3'):
            continue
        g = norm(r.get('genre_design'))
        if g in GENRES:
            by[g][r.get('batch')].append(r)
    out = {}
    for g, batches in by.items():
        pool = {b: list(v) for b, v in batches.items()}
        multi = sorted([b for b in pool if len(pool[b]) >= per_batch], key=lambda b: -len(pool[b]))
        sel = []
        for b in multi:
            if len(sel) + per_batch > n_per:
                break
            sel += [pool[b].pop(0) for _ in range(per_batch)]
        for b in sorted(pool, key=lambda b: -len(pool[b])):  # 잔여는 분산 우선
            while pool[b] and len(sel) < n_per:
                sel.append(pool[b].pop(0))
        out[g] = sel
    return out


def fetch(r):
    p = os.path.join(CACHE, f"{r['uuid']}.mp3")
    if os.path.exists(p) and os.path.getsize(p) > 10000:
        return p, "cache"
    req = urllib.request.Request(r['cdn_mp3'], headers={'User-Agent': 'encore-EAR/0.1'})
    with urllib.request.urlopen(req, timeout=90) as resp, open(p, 'wb') as f:
        f.write(resp.read())
    time.sleep(SLEEP)
    return p, "cdn"


def feats(path):
    y, sr = librosa.load(path, sr=22050, mono=True, duration=EXCERPT_S)
    y_h, y_p = librosa.effects.hpss(y)
    rms = librosa.feature.rms(y=y)[0]
    return {
        "centroid": float(librosa.feature.spectral_centroid(y=y, sr=sr).mean()),
        "rolloff85": float(librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85).mean()),
        "hp_ratio": float(np.sum(y_h ** 2) / (np.sum(y_p ** 2) + 1e-9)),
        "dr_db": float(20 * np.log10((np.percentile(rms, 95) + 1e-9) / (np.percentile(rms, 10) + 1e-9))),
        "contrast": float(librosa.feature.spectral_contrast(y=y, sr=sr).mean()),
        "zcr": float(librosa.feature.zero_crossing_rate(y).mean()),
        "onset_density": float(len(librosa.onset.onset_detect(y=y, sr=sr)) / (len(y) / sr)),
        "bpm": float(np.atleast_1d(librosa.beat.beat_track(y=y, sr=sr)[0])[0]),
    }


def fratio(groups, min_n=2):
    vals = [np.asarray(v, float) for v in groups.values() if len(v) >= min_n]
    if len(vals) < 2:
        return None
    k, n = len(vals), sum(len(v) for v in vals)
    gm = np.concatenate(vals).mean()
    ssb = sum(len(v) * (v.mean() - gm) ** 2 for v in vals)
    ssw = sum(((v - v.mean()) ** 2).sum() for v in vals)
    if n - k <= 0 or ssw <= 0:
        return None
    return float((ssb / (k - 1)) / (ssw / (n - k)))


if __name__ == '__main__':
    idx = sys.argv[1]
    n_per = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    rows = [json.loads(l) for l in open(idx)]
    sample = pick(rows, n_per)
    print("표본 설계:", {g: f"{len(v)}곡/{len(set(x['batch'] for x in v))}배치" for g, v in sample.items()},
          file=sys.stderr)

    data, errs = [], []
    for g, items in sample.items():
        for r in items:
            try:
                p, src = fetch(r)
                f = feats(p)
                f.update(genre_design=g, uuid=r['uuid'][:8], batch=r['batch'],
                         source_project=r.get('source_project'), src=src)
                data.append(f)
                print(f"  ok {g:16s} {r['batch']:>6s} {r['uuid'][:8]} ({src})", file=sys.stderr)
            except Exception as e:
                errs.append({"uuid": r['uuid'], "genre": g, "batch": r['batch'], "err": repr(e)[:150]})
                print(f"  ERR {g:16s} {r['uuid'][:8]} {e}", file=sys.stderr)

    METRICS = ["centroid", "rolloff85", "hp_ratio", "dr_db", "contrast", "zcr", "onset_density", "bpm"]
    summary = {}
    for m in METRICS:
        byg = collections.defaultdict(list)
        for d in data:
            byg[d['genre_design']].append(d[m])
        # 교락 지표: 각 장르 내부에서 배치별 F — 장르별 산출 후 중앙값
        within = []
        for g in byg:
            bb = collections.defaultdict(list)
            for d in data:
                if d['genre_design'] == g:
                    bb[d['batch']].append(d[m])
            f = fratio(bb)
            if f is not None:
                within.append(f)
        summary[m] = {
            "F_genre": fratio(byg),
            "F_batch_within_genre_median": float(np.median(within)) if within else None,
            "n_genres_testable_for_batch": len(within),
            "F_balladfam": fratio({g: v for g, v in byg.items() if g in BALLAD_FAM}),
            "per_genre": {g: {"mean": round(float(np.mean(v)), 2), "sd": round(float(np.std(v, ddof=1)), 2), "n": len(v)}
                          for g, v in sorted(byg.items()) if len(v) >= 2},
        }

    json.dump({"as_of": "2026-08-03", "design": "v2 confound-split", "label_source": "design_intent",
               "excerpt_s": EXCERPT_S, "n_clips": len(data), "errors": errs,
               "batch_diversity": {g: len(set(d['batch'] for d in data if d['genre_design'] == g)) for g in sample},
               "summary": summary, "rows": data},
              open(OUT, 'w'), ensure_ascii=False, indent=1)

    print(f"\n{'지표':14s} {'F_장르':>8s} {'F_배치(장르내)':>14s} {'F_발라드3종':>12s}")
    for m in METRICS:
        s = summary[m]
        fm = lambda x: '-' if x is None else round(x, 1)
        print(f"{m:14s} {fm(s['F_genre']):>8} {fm(s['F_batch_within_genre_median']):>14} {fm(s['F_balladfam']):>12}")
    print(f"\n분석 {len(data)}클립 / 실패 {len(errs)}", file=sys.stderr)
