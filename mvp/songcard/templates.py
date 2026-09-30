"""템플릿 카드 12종 — ★이 파일이 유일한 정본이다.

왜 만들었나: 목적 표가 **3곳에 복제**돼 있었다(`server.OCCASIONS` 6종 · `sp_builder.MOODS`/`TEMPO` ·
`export_card.OCC`). 09-30 템플릿을 12종으로 늘리면서 그대로 뒀으면 자가 세 벌이 된다
(값은 한 곳에서만 — 늘리는 김에 접는다). 세 곳 모두 여기서 읽어 간다.

칸의 뜻
  mood   분위기 어휘 — ★**코퍼스 관측어만**. `sp_builder`가 접수 때마다 `expr_concepts`에서
         attested_count 를 그 자리에서 읽어 문턱(MIN_ATTESTED) 미만·데드존이면 **거절**한다.
         ⛔여기 수치를 옮겨 적지 않는다(설계 문서의 괄호 숫자는 09-30 실측 시점의 표시일 뿐).
  bpm    요청층 값(우리가 달라고 쓰는 숫자 — Suno가 그렇게 들었다는 관측이 아니다)
  preset 폼에 «미리 선택된 채» 뜨는 기본값. 사용자가 바꿀 수 있다.
         ★vocal 기본값은 **앱 공통 기본(female)이고 템플릿별 근거가 없다** — 근거 있는 척하지 않는다.
  extra  템플릿 전용 입력 칸 1개(없으면 None)
  structure_hint  가사 «구조» 지시 1줄 → 발주서 필드로 나간다.
         ⛔가사 문면은 sunolanguage 가 쓰지 않는다(LM 라인 담당 — ①-41 경계).
"""

DEFAULT_VOCAL = "female"   # 앱 공통 기본값(템플릿별 근거 없음 — 사용자가 바꾼다)


def _t(label, emoji, hint, mood, bpm, genre, extra, structure_hint):
    return {"label": label, "emoji": emoji, "hint": hint, "mood": mood, "bpm": bpm,
            "preset": {"genre": genre, "vocal": DEFAULT_VOCAL},
            "extra": extra, "structure_hint": structure_hint}


def _x(fid, label, hint, limit=40):
    return {"id": fid, "label": label, "hint": hint, "limit": limit}


# 순서 = 화면에 뜨는 순서
TEMPLATES = {
    "birthday": _t("생일", "🎂", "올해도 태어나줘서 고맙다는 말", ["bright", "warm"], 100, "ballad",
                   _x("age", "몇 번째 생일", "선택 · 예) 마흔", 20),
                   "1절=태어난 날·그 사람다움 → 후렴=「오늘은 네 날」 반복 → 2절=올 한 해 바람"),
    "parents": _t("부모님께", "🏡", "늦게 전하는 이야기", ["warm", "tender"], 74, "ballad",
                  _x("unsaid", "못 했던 말 한 줄", "선택"),
                  "1절=옛 장면(집·손·밥) → 후렴=늦게 전하는 고백 → 2절=지금의 나"),
    "thanks": _t("감사", "🌿", "말로 다 못 한 고마움", ["warm", "gentle"], 80, "acoustic",
                 _x("what", "고마운 일 한 가지", "선택"),
                 "1절=그 일 → 후렴=고맙다는 말 반복 → 브리지=갚고 싶은 마음"),
    "couple": _t("연인에게", "💞", "처음과 지금 사이", ["intimate", "warm"], 78, "ballad",
                 _x("first_met", "처음 만난 장면", "선택"),
                 "1절=처음 → 후렴=지금도 같은 마음 → 2절=앞으로"),
    "anniversary": _t("기념일", "💍", "함께 지나온 시간", ["warm", "intimate"], 76, "ballad",
                     _x("years", "몇 주년", "선택 · 예) 10주년", 20),
                     "1절=지나온 시간 목록 → 후렴=숫자를 부르는 후렴 → 2절=다음 해"),
    "cheer": _t("응원·도전", "🔥", "새 출발·시험·도전 앞에서", ["bright", "punchy"], 110, "acoustic",
                _x("facing", "앞둔 일", "선택 · 예) 수능·이직·수술"),
                "1절=지금의 무게 → 후렴=밀어 주는 구호 → 2절=끝난 뒤 그림"),
    "comfort": _t("위로", "🕯", "곁에 있다는 마음", ["gentle", "soft", "intimate"], 70, "ballad",
                  _x("avoid", "넣지 말아야 할 말", "선택 · 예) 「힘내」는 빼 주세요"),
                  "1절=곁에 있음 → 후렴=위로 없이 그냥 함께 → ⛔해결·훈계 금지"),
    "farewell": _t("이별·추억", "🍂", "보내는 마음", ["atmospheric", "gentle"], 72, "ballad",
                   _x("kind", "작별인지 추모인지", "선택"),
                   "1절=남은 장면 → 후렴=잘 가라는 말 → 2절=기억하는 방식"),
    "graduation": _t("졸업·첫걸음", "🎓", "문을 나서는 날", ["bright", "grand"], 92, "acoustic",
                     _x("school", "학교·과정 이름", "선택"),
                     "1절=지나온 교실 → 후렴=문을 나서는 장면 → 2절=새 자리"),
    "wedding": _t("결혼 축가", "💒", "두 사람에게", ["grand", "warm", "lush"], 72, "ballad",
                  _x("couple_names", "두 사람 이름·식 날짜", "선택"),
                  "1절=두 사람의 시작 → 후렴=축복 → 2절=하객에게"),
    "congrats": _t("승진·개업 축하", "🎉", "버틴 끝에 온 날", ["bright", "groove"], 104, "trot",
                   _x("achieved", "무엇을 이뤘는지", "선택"),
                   "1절=버틴 시간 → 후렴=흥나는 축하 반복 → 2절=앞날"),
    "milestone": _t("환갑·칠순", "🎊", "긴 세월에 드리는 노래", ["warm", "grand"], 84, "trot",
                    _x("age_title", "연세·자녀 호칭", "선택 · 예) 칠순·막내아들"),
                    "1절=지나온 세월 → 후렴=건강 기원 → 2절=자손들 인사"),
}

IDS = list(TEMPLATES)
MOODS = {k: v["mood"] for k, v in TEMPLATES.items()}     # sp_builder 가 읽는다
TEMPO = {k: v["bpm"] for k, v in TEMPLATES.items()}      #   〃


def options():
    """화면(/api/options)용 — 서버 내부값(mood·structure_hint)은 내보내지 않는다."""
    return [{"id": k, "label": v["label"], "emoji": v["emoji"], "hint": v["hint"],
             "preset": v["preset"], "extra": v["extra"]} for k, v in TEMPLATES.items()]


def label_emoji(occasion: str):
    t = TEMPLATES.get(occasion)
    return (t["label"], t["emoji"]) if t else (occasion, "🎵")
