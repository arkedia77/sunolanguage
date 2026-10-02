"""요청층 프롬프트를 «우리 스타일» SP 로 재작성 (2026-10-02 LEO 지시).

우리 스타일 = 다섯 가지 규칙. ⛔말로만 두지 않고 기계가 검사한다.
  R1 평가어·마케팅어를 쓰지 않는다 — radio-ready·luxurious·impeccable 같은 말은
     «오디오 서술»이 아니라 «평가»다. Suno 관측에 그런 말은 거의 없다.
  R2 표기를 관측형으로 정규화한다 — sub bass→sub-bass(61) · kick→kick drum(496) 처럼
     우리 코퍼스가 실제로 그렇게 적은 꼴로.
  R3 쓰는 서술어는 전부 attested≥MIN · 데드존 아님. 못 넘으면 **거절**하고 대체어를 제시한다.
  R4 장르 라벨·BPM·구조 지시는 요청층으로 **분리 기재**한다(관측인 척하지 않는다).
  R5 SP 1000자 이내 · 중복 어휘 0 · 명령문("put some …") 0.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "sunolang.db"
MIN = 30
SP_MAX = 1000
EVAL_WORDS = re.compile(r"\b(radio-ready|luxurious|impeccable|high-end|premium|viral|instantly|"
                        r"captivating|empowering|elegant|polished|rich resonance|immersive)\b", re.I)
IMPERATIVE = re.compile(r"\b(put some|add |leave |avoid |make it)\b", re.I)


def lookup(con, term):
    r = con.execute("select attested_count, category, is_dead_zone from expr_concepts where suno_term=?",
                    (term,)).fetchone()
    return r


def nearest(con, term, k=3):
    """못 쓰는 말에 대한 «관측된» 대체 후보 — 부분일치 상위."""
    core = re.sub(r"[^a-z ]", " ", term.lower()).split()
    out = []
    for w in sorted(core, key=len, reverse=True)[:2]:
        out += con.execute("select suno_term, attested_count from expr_concepts "
                           "where suno_term like ? and is_dead_zone=0 and attested_count>=? "
                           "order by attested_count desc limit ?", (f"%{w}%", MIN, k)).fetchall()
    seen, uniq = set(), []
    for t, n in out:
        if t not in seen:
            seen.add(t); uniq.append((t, n))
    return uniq[:k]


def build(con, spec):
    """spec = {genre, bpm, structure, observed:[...]} → SP + provenance + 검사결과"""
    bad, prov = [], []
    for t in spec["observed"]:
        r = lookup(con, t)
        if not r:
            bad.append((t, "코퍼스에 없음", nearest(con, t)))
        elif r[2]:
            bad.append((t, f"데드존(attested={r[0]})", nearest(con, t)))
        elif r[0] < MIN:
            bad.append((t, f"문턱 미만(attested={r[0]}<{MIN})", nearest(con, t)))
        else:
            prov.append({"term": t, "attested_count": r[0], "category": r[1], "layer": "observed"})
    if bad:
        return None, bad, prov
    sp = ", ".join([spec["genre"]] + spec["observed"] + [f"{spec['bpm']} BPM"])
    checks = {
        "R1 평가어 0": not EVAL_WORDS.search(sp),
        "R5 명령문 0": not IMPERATIVE.search(sp),
        "R5 중복 0": len(spec["observed"]) == len(set(spec["observed"])),
        f"R5 {SP_MAX}자 이내": len(sp) <= SP_MAX,
    }
    prov += [{"term": spec["genre"], "layer": "request", "note": "장르 라벨=요청층(관측 아님)"},
             {"term": f"{spec['bpm']} BPM", "layer": "request", "note": "템포=요청층"}]
    if spec.get("structure"):
        prov.append({"term": spec["structure"], "layer": "request", "note": "구조 지시=요청층"})
    return {"sp": sp, "sp_chars": len(sp), "checks": checks, "provenance": prov}, [], prov


def main():
    specs = json.loads(Path(sys.argv[1]).read_text())
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out = []
    for s in specs:
        res, bad, prov = build(con, s)
        print(f"\n[{s['id']}] {s['label']}  ← {s['from']}")
        if bad:
            print("  ⛔거절 — 아래 말은 못 씁니다(코퍼스 근거 없음):")
            for t, why, alt in bad:
                a = ", ".join(f"{x}({n})" for x, n in alt) or "대체 후보 없음"
                print(f"     {t:28s} {why:24s} → 대체: {a}")
            continue
        print(f"  SP({res['sp_chars']}자): {res['sp']}")
        print("  검사: " + " · ".join(f"{k}={'✅' if v else '❌'}" for k, v in res["checks"].items()))
        obs = [p for p in res["provenance"] if p["layer"] == "observed"]
        print(f"  관측 어휘 {len(obs)}개 · 최저 attested {min(p['attested_count'] for p in obs)}")
        out.append({**s, **res})
    if out:
        dst = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if dst:
            dst.write_text(json.dumps(out, ensure_ascii=False, indent=1))
            print(f"\n→ {dst} ({len(out)}건)")


if __name__ == "__main__":
    main()
