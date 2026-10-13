# G2 가사게이트 v0 — FAIL 앵커 테스트 (G5 원칙: "이런 가사면 FAIL" 반례 고정.
# 통과만 확인하는 게이트 금지 — 각 항목이 실제로 거르는지 증명)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from g2_lyrics_gate import run_gate, line_metrics, tukey  # noqa: E402

# 테스트 전용 소형 기준선 (DB 비의존 — 실기준선은 data/g2_baseline.json [MEASURED])
BASELINE_FIXTURE = {
    "provenance": "[FIXTURE] 테스트 전용",
    "fences": {
        "syllables": {"q1": 8.0, "q3": 12.0, "lo": 2.0, "hi": 18.0, "n": 100},
        "coda_ratio": {"q1": 0.33, "q3": 0.54, "lo": 0.03, "hi": 0.85, "n": 100},
        "cluster_per_10": {"q1": 0.8, "q3": 1.4, "lo": 0.0, "hi": 2.3, "n": 100,
                           "zero_inflated_nonzero_fence": True},
    },
}

GOOD = """[Verse 1]
창밖에 흐르는 밤의 강물
너의 목소리가 남아 있어

[Chorus]
우리 다시 만나는 그날까지
별빛 아래 노래할게

[Verse 2]
새벽이 오면 길을 떠나며
너의 미소를 기억할게

[Chorus]
우리 다시 만나는 그날까지
별빛 아래 노래할게

[Outro]
[soft piano fades]
"""


def test_pass_anchor():
    r = run_gate(GOOD, concept="이별과 재회의 밤", baseline=BASELINE_FIXTURE)
    assert r["verdict"] == "PASS", r["hard_fail_items"]
    assert r["outside_gate"], "outside_gate 명시 필수 (정직 보류)"


# ── ①음절수 FAIL 앵커: 멜로디 스펙 4~8음절인데 20음절 행 ──
def test_fail_anchor_syllables():
    bad = "[Verse 1]\n이 행은 멜로디가 감당할 수 없을 만큼 지나치게 길게 이어지는 가사 행입니다\n둘째 행도 있어\n"
    r = run_gate(bad, melody_spec={"syllables_per_line": [4, 8]}, baseline=BASELINE_FIXTURE)
    item = r["items"][0]
    assert item["verdict"] == "FAIL" and item["role"] == "hard_fail"
    assert r["verdict"] == "FAIL"


def test_syllables_not_compared_without_spec():
    # 스펙 부재 = NOT_COMPARED 정직 표기 (게이트 차단 금지)
    r = run_gate(GOOD, baseline=BASELINE_FIXTURE)
    item = r["items"][0]
    assert item["verdict"] == "NOT_COMPARED" and item["role"] == "report_only"


# ── ②발음 난이도 FAIL 앵커: 받침 폭탄 + 경계 클러스터 밀집 ──
def test_fail_anchor_pronunciation():
    bad = "[Verse 1]\n칡밭 꺾꽂이 밟고 짓밟혀 꺾였다\n닭장 곁 붉닭 꽉 껴 갇혔닭\n"
    r = run_gate(bad, baseline=BASELINE_FIXTURE)
    item = r["items"][1]
    assert item["verdict"] == "FAIL", item["detail"]
    assert item["role"] == "report_only"
    assert r["verdict"] == "PASS", "report_only는 게이트 차단 금지"


# ── ③금칙어 FAIL 앵커 + 예외어 오탐 방지 ──
def test_fail_anchor_forbidden():
    bad = "[Verse 1]\n씨발 세상이 다 미워\n그래도 걸어가\n"
    r = run_gate(bad, baseline=BASELINE_FIXTURE)
    item = r["items"][2]
    assert item["verdict"] == "FAIL" and item["role"] == "hard_fail"
    assert r["verdict"] == "FAIL"


def test_forbidden_exception_no_false_positive():
    ok = "[Verse 1]\n시발점에 다시 선 우리 두 사람\n새로운 길을 걸어가\n"
    r = run_gate(ok, baseline=BASELINE_FIXTURE)
    assert r["items"][2]["verdict"] == "PASS", r["items"][2]["detail"]


# ── ④컨셉 일치 FAIL 앵커: 명시 키워드 계약 위반 ──
def test_fail_anchor_concept_keywords():
    lyrics = "[Verse 1]\n도시의 겨울 골목을 걸어\n차가운 바람이 분다\n"
    r = run_gate(lyrics, concept_keywords=["바다", "여름"], baseline=BASELINE_FIXTURE)
    item = r["items"][3]
    assert item["verdict"] == "FAIL" and item["role"] == "hard_fail"
    assert r["verdict"] == "FAIL"


def test_concept_freetext_is_report_only():
    lyrics = "[Verse 1]\n도시의 겨울 골목을 걸어\n차가운 바람이 분다\n"
    r = run_gate(lyrics, concept="여름 바다의 추억", baseline=BASELINE_FIXTURE)
    item = r["items"][3]
    assert item["role"] == "report_only"
    assert r["verdict"] == "PASS", "자유서술 컨셉 불일치는 권고만"


# ── ⑤코퍼스 규격 FAIL 앵커: 영어 디렉티브 누출 / 1행 섹션 / V1≡V2 ──
def test_fail_anchor_english_leak():
    bad = "[Verse 1]\n너의 목소리가 남아\nFiddle solo over drone\n"
    r = run_gate(bad, baseline=BASELINE_FIXTURE)
    item = r["items"][4]
    assert item["verdict"] == "FAIL" and item["role"] == "hard_fail"
    types = {p["type"] for p in item["detail"]["problems"]}
    assert "english_directive_leak" in types
    assert r["verdict"] == "FAIL"


def test_fail_anchor_thin_section_and_identical_verses():
    bad = ("[Verse 1]\n같은 가사 반복되는 절\n한 줄 더 있는 절\n\n"
           "[Verse 2]\n같은 가사 반복되는 절\n한 줄 더 있는 절\n\n"
           "[Bridge]\n한 줄뿐인 브릿지\n")
    r = run_gate(bad, baseline=BASELINE_FIXTURE)
    item = r["items"][4]
    types = {p["type"] for p in item["detail"]["problems"]}
    assert "identical_sections" in types, item["detail"]
    assert "thin_section" in types, item["detail"]
    assert r["verdict"] == "FAIL"


def test_instrumental_sections_not_thin_flagged():
    ok = "[Intro]\n[soft piano]\n\n[Verse 1]\n너의 목소리가 남아 있어\n밤의 강을 건너서\n\n[Outro]\n[fade out]\n"
    r = run_gate(ok, baseline=BASELINE_FIXTURE)
    assert r["items"][4]["verdict"] == "PASS", r["items"][4]["detail"]


# ── 기반 유틸 ──
def test_line_metrics_basic():
    m = line_metrics("밤하늘의 별")
    assert m["syllables"] == 5
    assert 0 < m["coda_ratio"] <= 1


def test_tukey_zero_inflated():
    f = tukey([0.0] * 80 + [1.0, 1.2, 1.4, 2.0] * 5)
    assert f.get("zero_inflated_nonzero_fence") is True
    assert f["hi"] > 0 and f["lo"] == 0.0


# ── ⑦ 읽기 계열 짝맞음 (report_only · 2026-10-13 encore 판정) ──
def test_reading_class_warns_on_sino_before_native_unit():
    """「오후 삼 시」는 ⑥(숫자 글자)을 통과한다 — ⑦이 그 문을 본다."""
    ly = "[Verse 1]\n오후 삼 시 그 자리에\n네 시에 만나자고\n"
    r = run_gate(ly, baseline=BASELINE_FIXTURE)
    it = r["items"][6]
    assert it["id"] == 7 and it["role"] == "report_only"
    assert it["verdict"] == "WARN", it["detail"]
    assert it["detail"]["n_hits"] == 1
    assert it["detail"]["hits"][0]["token"] == "삼 시"


def test_reading_class_is_report_only_and_never_blocks():
    """★report_only = verdict 에 안 들어간다. 이게 깨지면 0.10% 가 가사를 막는다."""
    ly = "[Verse 1]\n오후 삼 시 그 자리에\n칠 시 반 교복 위에\n"
    r = run_gate(ly, baseline=BASELINE_FIXTURE)
    assert r["items"][6]["verdict"] == "WARN"
    assert r["verdict"] == "PASS", r["hard_fail_items"]
    assert "읽기 계열 짝맞음" not in r["hard_fail_items"]


def test_reading_class_silent_on_native_before_sino_unit():
    """「세 초」는 대상 밖 — 한글로 적힌 순간 적힌 대로 읽히므로 오독이 아니다(encore 판정)."""
    ly = "[Verse 1]\n세 초만 더 기다려\n열두 퍼센트 남은 밤\n"
    r = run_gate(ly, baseline=BASELINE_FIXTURE)
    assert r["items"][6]["verdict"] == "PASS", r["items"][6]["detail"]


def test_reading_class_no_false_alarm_on_hundreds():
    """100 이상은 한자어가 표준 — 「백 개」·「십 명」은 정당(1차 검출기 오탐 59% 자기정정분)."""
    ly = "[Verse 1]\n별 백 개를 세었다\n사람 십 명이 모여\n"
    r = run_gate(ly, baseline=BASELINE_FIXTURE)
    assert r["items"][6]["verdict"] == "PASS", r["items"][6]["detail"]


def test_item_order_unchanged_for_first_six():
    """★판본이 올라도 ①~⑥ 인덱스는 안 흔들린다(남의 호출부가 items[i] 로 읽는다)."""
    r = run_gate("[Verse 1]\n조용한 밤의 노래\n먼 길을 걸어서\n", baseline=BASELINE_FIXTURE)
    assert [i["id"] for i in r["items"]] == [1, 2, 3, 4, 5, 6, 7]
    assert r["version"] == "v0.2"
