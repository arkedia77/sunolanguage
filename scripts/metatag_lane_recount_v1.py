#!/usr/bin/env python3
"""외부 메타태그 v2 4레인 재집계 — 인용 표준 「고유 표기 234종」의 재현기.

★왜 뒤늦게 만드나: 08-13 TEST-3의 헤드라인 수치(234종·등급 분포·중복 클러스터)가
  `docs/canonicalization_and_release_plan_v1.md` §1에 **재현 경로 없이** 실려 있었다.
  같은 문서의 TEST-1·TEST-2는 스크립트·JSON을 명시했는데 TEST-3만 없었다.
  전파(계획 §3 1단계 ⑵)하려면 남이 다시 셀 수 있어야 한다. → 이 파일이 그 자리다.

★이 스크립트가 세는 것과 안 세는 것을 먼저 적는다:
  - 센다: 각 레인의 `tags[]`(표기 자체) + lane2 `speaker_syntax[]`(화자 표기 패턴).
  - 안 센다: `not_accessed`(못 봄 — 「없음」이 아니다) · lane3 `instances`/`advice`/
    `precedence_statements`/`rule_block_prompting`(표기가 아니라 진술·사례) ·
    lane4 `target_attempts`(수집 시도 로그) · lane2 `failure_modes`(주장).

실행: python3 scripts/metatag_lane_recount_v1.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANES = REPO / "data" / "metatag_external" / "v2_lanes"
OUT = REPO / "data" / "metatag_external" / "lane_recount_v1.json"

FILES = ["lane1_phone_broadcast", "lane2_spoken_narrator",
         "lane3_sp_predeclaration", "lane4_multilingual"]


def norm(s):
    """정규화(엄격) — 대소문자·바깥괄호·끝구두점·연속공백만 접는다.

    ★한자·한글을 지우지 않는다. 1차 시안에서 `[^a-z0-9가-힣 ]`로 잡부호를 털었더니
      lane4(다국어 레인)의 `主持人`·`女性叙述者`·`耳语`가 **통째로 빈 문자열이 되어
      한 종으로 합쳐졌다.** 다국어를 모으려고 만든 레인을 정규화가 지우면 그 레인이
      존재할 이유가 없어진다. → 문자 클래스 화이트리스트 금지.
    """
    s = s.strip().lower()
    s = re.sub(r"^[\[\(<{]+|[\]\)>}]+$", "", s)
    s = re.sub(r"[:：,\.]+$", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm_loose(s):
    """정규화(관대) — 엄격판 + 강조 표기(`*static*` 류) 제거. 폭을 내기 위한 두 번째 자."""
    return re.sub(r"\s+", " ", norm(s).strip("*_ ")).strip()


def main():
    items, self_report, actual_per_lane = [], {}, {}
    for f in FILES:
        d = json.loads((LANES / f"{f}.json").read_text())
        self_report[f] = d.get("extracted_count")
        n = 0
        for t in d.get("tags", []):
            items.append({
                "표기": t["tag"], "정규화": norm(t["tag"]), "레인": f,
                "출처": t.get("source_url", ""), "출처명": t.get("source_label", ""),
                "등급": t.get("grade", ""), "괄호": t.get("bracketed"),
                "종류": "tag", "파생표시": t.get("derivative"),
            })
            n += 1
        for s in d.get("speaker_syntax", []):      # lane2 전용 — 표기 패턴이라 계상
            items.append({
                "표기": s["pattern"], "정규화": norm(s["pattern"]), "레인": f,
                "출처": s.get("source_url", ""), "출처명": s.get("source_label", ""),
                "등급": s.get("grade", ""), "괄호": None,
                "종류": "speaker_syntax", "파생표시": None,
            })
            n += 1
        actual_per_lane[f] = n

    uniq_tokens = {i["정규화"] for i in items}
    uniq_loose = {norm_loose(i["표기"]) for i in items}
    uniq_pairs = {(i["정규화"], i["출처"]) for i in items}

    # 중복(같은 표기가 여러 출처·레인에 반복) 상위
    per_token = defaultdict(list)
    for i in items:
        per_token[i["정규화"]].append(i)
    dup_top = sorted(per_token.items(), key=lambda kv: -len(kv[1]))[:12]

    # 등급 — 표기 단위(고유)로도, 항목 단위로도 낸다. 항목 단위만 내면 중복이 등급을 부풀린다.
    grade_items = Counter(i["등급"] for i in items)
    grade_uniq = Counter()
    for tok, group in per_token.items():
        gs = {g["등급"] for g in group}
        grade_uniq["A_demo" if "A_demo" in gs else (sorted(gs)[0] if gs else "")] += 1

    result = {
        "무엇": "외부 메타태그 v2 4레인 재집계 — 인용 표준 재현기",
        "재현": "python3 scripts/metatag_lane_recount_v1.py",
        "원자료": "data/metatag_external/v2_lanes/*.json",
        "세는_규칙": "각 레인 tags[] + lane2 speaker_syntax[]. not_accessed·advice·"
                     "precedence_statements·rule_block_prompting·target_attempts·failure_modes 제외",
        "★자기신고_대_실물": {
            "레인별_자기신고(extracted_count)": self_report,
            "레인별_실물": actual_per_lane,
            "차": {f: (actual_per_lane[f] - (self_report[f] or 0)) for f in FILES},
            "자기신고_합": sum(v or 0 for v in self_report.values()),
            "실물_합": sum(actual_per_lane.values()),
            "해석": "★어느 쪽도 「수집 건수」의 정답이 아니다 — 자기신고는 틀렸고, "
                    "실물 합도 중복을 포함한 항목 수다. 인용은 고유 표기 수로 한다.",
        },
        "★인용_표준": {
            "고유_표기_엄격": len(uniq_tokens),
            "고유_표기_관대": len(uniq_loose),
            "고유_(표기,출처)_쌍": len(uniq_pairs),
            "항목(중복포함)": len(items),
            "★문장": f"외부 나레이션·화자 표기 **고유 {len(uniq_loose)}~{len(uniq_tokens)}종** "
                     f"(정규화 규칙 의존 — 인용 시 규칙 병기. B_recited "
                     f"{round(100*grade_items.get('B_recited',0)/max(1,len(items)),1)}% = 대부분 전언). "
                     f"★「{sum(v or 0 for v in self_report.values())}」·「332」 단독 인용 금지.",
            "★재현_실패_기록": {
                "대상": "docs/canonicalization_and_release_plan_v1.md §1 TEST-3의 「고유 표기 234종 / 고유 쌍 259」",
                "결과": f"★재현 안 됨. 이 스크립트로는 엄격 {len(uniq_tokens)}종 · 관대 {len(uniq_loose)}종 "
                        f"· (표기,출처) 쌍 {len(uniq_pairs)}. 234는 두 자 사이에 있고 259는 어느 자로도 안 나온다.",
                "원인_판정": "★불명 — 그 수치를 낸 절차가 리포에 없다(스크립트·JSON 부재). "
                             "즉 「내가 틀렸다」도 「그때가 틀렸다」도 지금은 확정 못 한다.",
                "처분": "★재현되는 수치로 교체한다. 재현 없는 수치는 인용 표준이 될 수 없다.",
            },
        },
        "등급_분포": {"항목단위": dict(grade_items), "고유표기단위": dict(grade_uniq)},
        "★중복_상위(=파생 복제 신호)": [
            {"표기": t, "중복": len(g),
             "출처수": len({x["출처"] for x in g}),
             "레인": sorted({x["레인"][:5] for x in g})}
            for t, g in dup_top
        ],
        "★안_센_것": {
            f: {k: len(json.loads((LANES / f"{f}.json").read_text()).get(k, []))
                for k in ("not_accessed", "advice", "precedence_statements",
                          "rule_block_prompting", "target_attempts", "failure_modes")
                if json.loads((LANES / f"{f}.json").read_text()).get(k)}
            for f in FILES
        },
        "★한계": [
            "고유 표기 수는 **수집된 문자열의 종수**이지 **유효 어휘 수가 아니다**. 유효성은 하나도 안 쟀다.",
            "정규화는 대소문자·바깥괄호·끝구두점만 접는다. 어순·동의어(narrator/narration)는 **따로 센다**.",
            "★고유 표기 수는 정규화 규칙에 따라 흔들린다(엄격/관대 2종을 병기하는 이유). "
            "단일 정수로 인용하면 그 흔들림이 숨는다.",
            "not_accessed는 제외했다 — 「없음」이 아니라 **「안 봄」**이다(합계는 ★안_센_것 참조).",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != "★중복_상위(=파생 복제 신호)"},
                     ensure_ascii=False, indent=1))
    print("\n중복 상위:")
    for r in result["★중복_상위(=파생 복제 신호)"]:
        print(f"  {r['표기']:<28} {r['중복']}회 / 출처 {r['출처수']}")


if __name__ == "__main__":
    main()
