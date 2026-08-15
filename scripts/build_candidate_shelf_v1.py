#!/usr/bin/env python3
"""후보 선반 v1 — 외부 나레이션·화자 표기 235~236종을 `expr_*`가 **아닌** 별도 대장에 세운다.

설계 근거: docs/canonicalization_and_release_plan_v1.md §3 2단계 ⑹.
필수 열: grade · layer · source_author · derivative_cluster(Bark 복제 플래그).

★이 선반의 존재 이유 = **격리**다.
  이 235~236종은 전부 **D(전언)** 등급이고 우리 실측이 아니다. `expr_concepts`에 넣는 순간
  「Suno 네이티브 어휘」와 「인터넷에서 주운 말」이 같은 통에 섞이고, 커넥터 OUT을 통해
  5팀에 「검증된 어휘」로 배포된다. 그래서 별도 대장이다. ★선반→코퍼스 승격은 이 스크립트가
  하지 않는다(승격은 우리 실측으로만 — corpus_classification_criteria_v1.md §11 원칙 1).

정본=이 스크립트가 쓰는 JSON 파일. DB에 안 넣는다(넣으면 재빌드가 지운다 — 08-15 별칭 6건 사고).

재현: .venv/bin/python scripts/build_candidate_shelf_v1.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metatag_lane_recount_v1 import LANES, FILES, norm, norm_loose  # 정규화 단일 기재(G-K4)

REPO = Path(__file__).resolve().parent.parent
MERGED = REPO / "data" / "reanalysis_v2" / "merged_4values.json"
OUT = REPO / "data" / "metatag_external" / "candidate_shelf_v1.json"

BARK_RE = re.compile(r"\bbark\b|\bchirp\b", re.I)


def load_items():
    """4레인 원자료 → 항목 리스트. metatag_lane_recount_v1과 같은 세는 규칙."""
    items = []
    for f in FILES:
        d = json.loads((LANES / f"{f}.json").read_text())
        for t in d.get("tags", []):
            items.append({
                "표기": t["tag"], "레인": f, "종류": "tag",
                "출처명": t.get("source_label") or "", "출처url": t.get("source_url") or "",
                "등급": t.get("grade") or "", "괄호": t.get("bracketed"),
                "파생표시": t.get("derivative"), "맥락": t.get("context") or "",
                "언어": t.get("language"),
            })
        for s in d.get("speaker_syntax", []):   # lane2 전용 — 표기 패턴이라 같이 계상
            items.append({
                "표기": s["pattern"], "레인": f, "종류": "speaker_syntax",
                "출처명": s.get("source_label") or "", "출처url": s.get("source_url") or "",
                "등급": s.get("grade") or "", "괄호": None,
                "파생표시": None, "맥락": s.get("context") or "",
                "언어": None,
            })
    return items


def corpus_channels():
    """우리 코퍼스를 **층으로 갈라서** 돌려준다. ★여기서 층을 틀리면 선반 전체가 오염된다.

    실측 확인(2026-08-15):
      - `parse_slot_entities_v3.py:928`이 파싱하는 가사 브라켓은 `sr.get("lyrics")`이고
        `sr`은 **`suno_reanalysis`** 원소다 ⇒ `bracket_entities_v3.json`은 **출력층**이다
        (`source:"lyrics"`라는 라벨이 「우리 가사」로 오독되기 쉽다 — 실제론 Suno가 돌려준 가사).
      - `leomusic_original.lyrics`(=우리가 넣은 가사)의 브라켓은 **어떤 인덱스에도 안 들어간다.**
        여기서만 직접 읽는다. 이게 우리가 가진 **유일한 입력층 브라켓 채널**이다.
    """
    data = json.loads(MERGED.read_text())
    inp_br, out_br, out_sp = Counter(), Counter(), []
    songs_in = set()
    for r in data:
        sid = r.get("song_id")
        lo = (r.get("leomusic_original") or {}).get("lyrics") or ""
        for b in re.findall(r"\[([^\]]{1,200})\]", lo):
            inp_br[norm(b)] += 1
            songs_in.add(sid)
        for sr in r.get("suno_reanalysis") or []:
            for b in re.findall(r"\[([^\]]{1,200})\]", sr.get("lyrics") or ""):
                out_br[norm(b)] += 1
            if sr.get("sp"):
                out_sp.append(sr["sp"].lower())
    return inp_br, out_br, out_sp, len(songs_in), len(data)


def cluster_of(group):
    """derivative_cluster — ★리포에 실재하는 근거로만 판정한다.

    Bark 정본 토큰 목록은 이 리포에 없다. 그래서 「목록에 있나」로 못 가른다.
    가를 수 있는 것은 수집 당시 기록된 두 가지뿐이다: `derivative` 불리언(lane4)과
    `context` 안의 Bark/Chirp 언급. 둘 다 없으면 **미판정**이다 —
    ★「근거 없음」을 「파생 아님」으로 접지 않는다(「없음」≠「안 봄」).
    """
    ev = []
    bark = indep = False
    for it in group:
        if it["파생표시"] is True:
            bark = True
            ev.append(f"파생표시=true / {it['출처명'] or it['출처url']}")
        elif it["파생표시"] is False:
            indep = True
        if BARK_RE.search(it["맥락"]):
            bark = True
            ev.append(f"맥락에 Bark·Chirp 언급 / {it['출처명'] or it['출처url']}")
    if bark:
        return "bark_계보_근거있음", ev
    if indep:
        return "독립_주장", ev          # ★출처의 주장이지 우리가 검증한 게 아니다
    return "미판정", ev


def main():
    items = load_items()
    inp_br, out_br, out_sp, songs_in, n_songs = corpus_channels()

    groups = defaultdict(list)
    for it in items:
        groups[norm(it["표기"])].append(it)

    rows = []
    for key in sorted(groups):
        g = groups[key]
        cluster, ev = cluster_of(g)
        srcs, seen = [], set()
        for it in g:
            sig = (it["출처명"], it["출처url"])
            if sig in seen:
                continue
            seen.add(sig)
            srcs.append({"출처명": it["출처명"], "출처url": it["출처url"], "레인": it["레인"]})
        grades = Counter(it["등급"] for it in g)
        rows.append({
            "표기_정규화": key,
            "표기_변종": sorted({it["표기"] for it in g}),
            "관대키": norm_loose(key),
            "종수_기여": len(g),

            # ── 필수 열 4종 ──
            "grade": {
                "최고": "A_demo" if "A_demo" in grades else (sorted(grades)[0] if grades else ""),
                "분포": dict(grades),
                "★주": "A_demo도 외부 시연 관측이지 우리 실측이 아니다. 선반 전체의 대장 등급은 D(전언).",
            },
            "layer": {
                "주장": "입력층",
                "★주장의_주체": "외부 출처(‘이렇게 써넣으면 먹힌다’는 메타태그 주장)",
                "검증": None,
                "★검증이_null인_이유": "우리 코퍼스는 압도적으로 출력층이다. 입력층 브라켓 채널은 "
                                       "leomusic_original.lyrics 하나뿐이고 그것도 ‘써 봤다’는 사용 이력이지 "
                                       "‘먹혔다’는 결과 측정이 아니다(대조군 0).",
            },
            "source_author": srcs,
            "출처_수": len(srcs),
            "★출처_수는_교차확인이_아니다": "같은 Bark/Chirp 정본 목록을 여러 사이트가 복제하면 "
                                            "수만 늘고 독립 확인은 0이다. derivative_cluster를 같이 볼 것.",
            "derivative_cluster": cluster,
            "derivative_근거": ev,

            # ── 우리 코퍼스와의 접촉 (층을 값 옆에 붙인다) ──
            "우리코퍼스_접촉": {
                "출력층_브라켓_정확일치": out_br.get(key, 0),
                "출력층_SP문장_부분포함": sum(1 for sp in out_sp if key and key in sp),
                "입력층_브라켓_정확일치": inp_br.get(key, 0),
                "★해석": "출력층 출현은 ‘Suno가 이 말을 쓴다’는 관측이지 "
                          "‘입력에 쓰면 이렇게 된다’는 처방이 아니다. 승격 근거로 쓰지 말 것.",
            },
        })

    out = {
        "무엇": "후보 선반 v1 — 외부 나레이션·화자 표기 격리 대장 (expr_* 아님)",
        "재현": ".venv/bin/python scripts/build_candidate_shelf_v1.py",
        "원자료": "data/metatag_external/v2_lanes/*.json (4레인)",
        "정본_지위": "★이 파일이 정본이다. DB에 넣지 않는다 — expr_* 재빌드가 DELETE 후 시드에서 재구성하므로 "
                     "DB에만 있는 값은 조용히 소실된다(2026-08-15 별칭 6건 실사고).",
        "대장_등급": "D(전언) — 선반 전체. 개별 행의 grade는 수집 당시 출처 등급이지 승격 자격이 아니다.",
        "승격_규칙": "★이 선반에서 expr_*로의 승격은 이 스크립트가 하지 않는다. 승격은 우리 실측으로만 "
                     "(corpus_classification_criteria_v1.md §11 원칙 1). 외부 출처가 몇 개 겹쳐도 D는 D다.",
        "단위": {
            "키": "norm() 엄격 정규화(대소문자·바깥괄호·끝구두점·연속공백만 접음)",
            "고유_표기_엄격": len(rows),
            "관대키_기준_종수": len({r["관대키"] for r in rows}),
            "★인용": "고유 235~236종으로 폭을 적는다. 단일 정수 인용 금지(정규화 규칙 의존).",
        },
        "층_귀속_실측": {
            "출력층_채널": "suno_reanalysis.sp / suno_reanalysis.lyrics 브라켓 / stems tags·prompt",
            "입력층_채널": "leomusic_original.lyrics 브라켓 — ★현재 lexical_index에 안 들어간다(미인덱스)",
            "★주의": "bracket_entities_v3.json의 source 라벨이 'lyrics'라 입력층으로 오독하기 쉽다. "
                      "실제 파싱 대상은 parse_slot_entities_v3.py:928의 sr['lyrics'](=suno_reanalysis) — 출력층이다.",
            "입력층_브라켓_모집단": {"곡": songs_in, "전체곡": n_songs,
                                     "총_브라켓": sum(inp_br.values()), "고유": len(inp_br)},
            "출력층_브라켓_모집단": {"총_브라켓": sum(out_br.values()), "고유": len(out_br)},
        },
        "집계": {
            "derivative_cluster": dict(Counter(r["derivative_cluster"] for r in rows)),
            "출력층_접촉_1회이상": sum(1 for r in rows
                                       if r["우리코퍼스_접촉"]["출력층_브라켓_정확일치"] > 0
                                       or r["우리코퍼스_접촉"]["출력층_SP문장_부분포함"] > 0),
            "입력층_접촉_1회이상": sum(1 for r in rows
                                       if r["우리코퍼스_접촉"]["입력층_브라켓_정확일치"] > 0),
            "우리코퍼스_접촉_0": sum(1 for r in rows
                                     if not any(r["우리코퍼스_접촉"][k] for k in
                                                ("출력층_브라켓_정확일치", "출력층_SP문장_부분포함",
                                                 "입력층_브라켓_정확일치"))),
        },
        "★한계": [
            "유효성은 하나도 안 쟀다. 이 선반은 ‘무엇을 주웠나’의 대장이지 ‘무엇이 먹히나’의 대장이 아니다.",
            "derivative_cluster의 ‘미판정’은 ‘파생 아님’이 아니다 — 근거가 리포에 없다는 뜻이다.",
            "‘독립_주장’도 출처의 자기신고다. 우리가 계보를 추적해 확인한 게 아니다.",
            "출처_수는 독립 확인 수가 아니다. 복제 클러스터가 수를 부풀린다.",
            "입력층 접촉은 ‘우리가 써 봤다’는 사용 이력이다. 결과(먹혔는가)는 대조군이 0이라 미측정.",
        ],
        "후보": rows,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"WROTE {OUT.relative_to(REPO)}  ({len(rows)}종)")
    print(json.dumps({k: out[k] for k in ("단위", "층_귀속_실측", "집계")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
