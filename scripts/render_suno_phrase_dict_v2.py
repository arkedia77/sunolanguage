#!/usr/bin/env python3
"""render_suno_phrase_dict_v2.py — data/suno_phrase_dict_v2/dict.json → 사람이 읽는 표 md (stdout).
쓰기 0. 칸마다 대표 구 = Suno 가 쓴 근거(V+ · AG · HS) 큰 순 · 2낱말↑ 먼저.
"""
import collections, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CATS = ["공간(라이브↔스튜디오)", "믹스·마스터", "전달", "보컬 음색", "추임새·관객", "곡 흐름", "결/리듬", "악기·연주", "금지형", "장르", "무드", "그 밖"]


def ev(r):
    return r["V+"] + 3 * r["HS"] + 5 * r["AG"]


def suno_known(r):
    return r["V+"] >= 5 or r["HS"] >= 3 or r["AG"] >= 2


def main():
    d = json.loads((REPO / "data/suno_phrase_dict_v2/dict.json").read_text())
    m, R = d["meta"], d["rows"]
    n = m["channel_docs"]
    P = print
    P(f"# 수노말 사전 {m['version']}\n")
    P(f"- 빌더 `repo:sunolanguage {m['builder']}` · 표 `scripts/render_suno_phrase_dict_v2.py` · 값 `data/suno_phrase_dict_v2/dict.json` · DB `sunolang.db` `suno_phrase_dict`(v1.2 `suno_emitted_terms` 안 건드림)")
    P(f"- 재료 해시: refs.json `{m['inputs']['refs.json']}` · variety_rewrites.json `{m['inputs']['variety_rewrites.json']}` (`repo:agent-comm projects/sunomusic/attachments/SUNO_HOME_REFS_20261111/`)")
    P("- 생성 0 · 지출 0 · 실가수·그룹·곡 이름 0(LEO 문장 2 의 이름 든 구는 뺌)\n")
    cnt = collections.Counter(r["category"] for r in R)
    kn = collections.Counter(r["category"] for r in R if suno_known(r))
    P("## 0. 한눈에\n")
    P(f"- **{len(R):,}구** · 그중 **Suno 가 썼다는 근거 있는 구 {sum(kn.values()):,}**(Variety 더함 ≥5곡 · 홈 Suno 작성 ≥3곡 · agentic ≥2 중 하나)")
    P(f"- 지금 판 대조: 기존(v1.2·v3.5 에 같은 꼴) {sum(r['new_kind']=='기존' for r in R):,} · **구 꼴만 새것**(낱말은 다 있던 것) {sum(r['new_kind']=='구 꼴만 새것' for r in R):,} · **새 낱말 포함** {sum(r['new_kind']=='새 낱말 포함' for r in R):,}(그중 Suno 근거 {sum(1 for r in R if r['new_kind']=='새 낱말 포함' and suno_known(r))})")
    st = m["stale_v1_2_absent_in_new"]
    P(f"- 낡은 구(v1.2 10곡↑인데 새 재료 0): {st['n']} — {', '.join(t for t, _ in st['top'])} ⇒ 한글 2 = 토크나이저 밖 · 5낱말 2 = 4낱말 창 밖 ⇒ **실제 낡은 구 ≈0 · 폐기 0**")
    P(f"- 효과 대조 짝 = **5구뿐**(§3 · 교락) — 나머지 «먹힘»은 **[미확인]**: 나옴(렌더 실례) ≠ 들림\n")
    P("| 칸 | 구 | Suno 근거 있는 구 |\n|---|---|---|")
    for c in CATS:
        P(f"| {c} | {cnt[c]} | {kn[c]} |")
    P("\n## 1. 재료 채널 (곡 단위 · 채널끼리 합산 0)\n")
    P("| 칸 이름 | 무엇 | 곡(문서) 수 | 누가 썼나 |\n|---|---|---|---|")
    rows = [("V+ / V-", "Variety 켠 우리 렌더 — 보낸 SP ↔ Suno 저장 tags · 더한 구 / 뺀 구", n["V+"], "**Suno 확정**"),
            ("AG", "우리 agentic 리믹스 클립 tags(PG gen_method=agentic_remix · global_id 비어 있어 단위 = 서로 다른 문장)", n["AG"], "**Suno 확정**"),
            ("HS", "홈 곡 중 설명 모드 입력 있음 · task=agentic_thinking", n["HS"], "Suno [추정 강] — 설명 모드는 Suno 가 tags 를 씀"),
            ("HU", "홈 곡 나머지(upload 문장 포함 — «• Song Title» 꼴 섞여 저자 못 가름)", n["HU"], "**모름**(올린 사람 입력일 수 있음)"),
            ("HD", "홈 곡 display_tags", n["HD"], "Suno 화면 표시 태그"),
            ("OD", "우리 클립 display_tags(PG)", n["OD"], "Suno 화면 표시 태그"),
            ("LS", "녹음 인식 프롬프트(tracks 79 · 실음악 듣고 Suno 가 쓴 말)", n["LS"], "**Suno 확정** · 역방향 근거(들리면 이 말로 부름)"),
            ("LEO", "LEO 문장 4", n["LEO"], "LEO 가 가져온 문장(출처 Suno 쪽으로 보임 · 미확인)")]
    for a, b, c_, e in rows:
        P(f"| {a} | {b} | {c_:,} | {e} |")
    P("\n⛔ Enhance·Inspire 자동 스타일 = 홈·PG 어디에도 식별 칸 없음 → **미측정**.\n")
    P("## 2. 칸별 대표 구 (Suno 근거 큰 순 · 2낱말↑ · 칸마다 14)\n")
    P("열: V+ = Suno 가 더한 곡 · V- = 뺀 곡 · AG · HS · HU · LS(녹음 인식 79 중) · 새 = 지금 판 대조 · 예 = 렌더 실례 id(나옴 ≠ 들림)\n")
    for c in CATS:
        rs = sorted([r for r in R if r["category"] == c and r["n_words"] >= 2], key=lambda r: (-ev(r), -r["HU"]))[:14]
        P(f"### {c}\n\n| 구 | V+ | V- | AG | HS | HU | LS | 새 | 예 |\n|---|---|---|---|---|---|---|---|---|")
        for r in rs:
            P(f"| {r['phrase']} | {r['V+']} | {r['V-']} | {r['AG']} | {r['HS']} | {r['HU']} | {r['LS']} | {r['new_kind']} | `{str(r['render_example'])[:8]}` |")
        P("")
    ep = m["effect_pair"]
    P("## 3. 효과 대조 짝 (먹힘 근거 1층 — 지금 1건)\n")
    P(f"- {ep['case']}")
    for k, v in ep["phrases"].items():
        P(f"  - `{k}` — {v}")
    P(f"- ⚠**교락**: {ep['confound']}")
    byp = {r["phrase"]: r for r in R}
    P("- 다섯 구가 재료에 나오는 곡 수(V+ · HS · HU): " + " · ".join(f"`{k}` {byp[k]['V+']}·{byp[k]['HS']}·{byp[k]['HU']}" for k in ep["phrases"] if k in byp)
      + " ⇒ ★`live mix` 는 Suno 가 거의 안 쓰는 꼴(홈 1곡) · Suno 가 스스로 쓰는 쪽은 `studio mix`(더함 81곡)")
    P("- ⇒ 이 짝은 «라이브 문구 묶음 + 템포 + 성별이 함께 바뀌면 판이 바뀐다»까지만 말한다. «Live Mix 한 낱말이 먹혔다»는 [미확인] — §6 한 칸 짝으로 가린다.\n")
    P("## 4. Suno 가 고쳐 쓸 때 (Variety 1,681곡)\n")
    tp = m["templates"]
    P("- **Suno 서명 꼴 «NNN BPM in <조>»**: " + " · ".join(f"{k} {v}" for k, v in tp.items()) + " ⇒ Suno 다시쓰기가 템포·조를 앞에 박는 버릇(우리 SP 엔 거의 없음)")
    add = sorted([r for r in R if r["n_words"] >= 2], key=lambda r: -r["V+"])[:20]
    rem = sorted([r for r in R if r["n_words"] >= 2], key=lambda r: -r["V-"])[:20]
    P("- Suno 가 **더한** 구 상위 20: " + " · ".join(f"{r['phrase']} {r['V+']}" for r in add))
    P("- Suno 가 **뺀** 구 상위 20: " + " · ".join(f"{r['phrase']} {r['V-']}" for r in rem))
    P("- 읽기: «guitar plays»·«piano plays» 같은 **서술 동사 꼴을 버리고** «clean electric-guitar arpeggios»·«bass locked to the kick» 같은 **명사구 + 관계 꼴**로 바꿔 씀 · «male/female vocal» → «male korean vocal»·«mid-register vocal» 로 **언어·음역을 붙임**\n")
    P("## 5. 4라인 SP 에 바로 쓸 꼴 예 (쉼표 사이 덩어리 = 사전 행 1~2개 이음 · 구성 구 전부 사전에 있음 · 실명 0 · ⛔시험 전 = 참고용 · 약한 구 = korean indie rock(AG 2)·live drums(HS 10·V+ 0))\n")
    for line in EXAMPLES:
        P(f"- {line}")
    P("\n## 6. 3단계 먹힘 시험 후보 (encore · 공간·전달 칸 · 한 칸만 바꾸는 짝)\n")
    for t in TESTS:
        P(f"- {t}")
    P("\n## 7. 한계\n")
    for t in LIMITS:
        P(f"- {t}")


EXAMPLES = [  # 쉼표 사이 덩어리 = 사전 행 1~2개를 이은 것(구성 구 전부 dict.json 에 있음 — 11-12 대조) · 템포·조 숫자는 꼴(«NNN BPM in <조>») 자리
    "**걸그룹 댄스** — `K-pop, dance-pop at 124 BPM in F minor, four-on-the-floor kick, sidechain synth bass, bright, female Korean vocals, layered chorus harmonies, chant on the hook, half-time bridge before the final chorus, polished, wide stereo, studio mix`",
    "**발라드** — `Korean ballad at 72 BPM in D major, felt piano, bowed strings entering in verse two, intimate close-mic male Korean vocal, restrained vibrato, plate reverb, swelling final chorus, warm analog, studio mix`",
    "**밴드·싱어송라이터** — `Korean indie rock at 132 BPM, clean electric-guitar arpeggios, rounded bass, locked to the kick, live drums, room tone, female Korean vocal, half-spoken verses opening, belting choruses, tape saturation, stripped-back open-space mix`",
]
TESTS = [
    "공간 ① `Studio Mix` ↔ `Live Mix` — 나머지 축자 · 같은 가사·원곡 · 2클립↑씩(곡 안 클립 차 0.09~0.33 교훈) · 사전등록: 관객·공간 소리 유무만 달라지나",
    "공간 ② `room tone`·`plate reverb` 넣음 ↔ 뺌 — Suno 더함 상위(26·20곡) · 듣는 자리 = 보컬 꼬리 길이",
    "전달 ③ `half-spoken` 넣음 ↔ 뺌 — Suno 더함 22곡 · agentic 4 · 듣는 자리 = 벌스 첫 4마디가 말하듯인가",
    "전달 ④ `belting`(HS 3 · HU 12) · `restrained vibrato`(Suno 더함 15) — 따로 한 짝씩 · 듣는 자리 = 후렴 음량·떨림",
    "⛔한 번에 한 칸 — 플라멩코 짝처럼 6곳 함께 바꾸면 어느 낱말이 먹혔는지 못 가림",
]
LIMITS = [
    "«먹힘» 근거는 효과 짝 1건(교락) · 나머지는 «Suno 가 썼다»(V+·AG·HS·LS)까지 — **Suno 가 쓴다 ≠ Suno 가 따른다**(듀엣 표 §6 교훈의 반대 방향도 성립 안 함)",
    "홈 곡은 두 계정 홈·탐색 응답 1회 표집(11-11) · 개인화 칸 첫 장만 · 트렌딩 칸 없음(sunomusic README)",
    "구 = 쉼표·세미콜론·마침표 사이 1~4낱말 · 더 긴 구 안에서만(80%↑) 나오는 짧은 구는 뺌 · 한글 낱말은 토크나이저 밖",
    "칸 = 낱말 규칙(빌더 CATS · 위에서 먼저 걸리는 것) — 경계 구(예 live drums = 악기)는 규칙으로 고정 · «그 밖» 1,4xx 은 서술 연결어(reframed·refracted·beneath 류 = Variety 문체)",
    "실명 거름: LEO 문장은 이름 목록으로 뺌 · 홈 구는 자동 거름 없음 — 흔한 가수명·feat 꼴 대조 0건(11-12) · 쓰기 전 한 번 더 볼 것",
    "V2~4 인데 «같음» 132클립 = 기록 착오 아님 — 실제 Variety 2~4 렌더 3,402 중 132(3.9%)가 SP 를 안 고침(sunomusic 223325 · 클립 메타 다시 읽기 132/132) · 이 클립들은 V+·V- 에 아무 구도 안 보탬(클립 단위 비교라 그대로 맞음) · 무엇이 가르는지 모름 · V1 보낸 SP 길이 미검증은 그대로",
]

if __name__ == "__main__":
    main()
