# antisuno · Phase 0 조사 브리프 v0 (외부 검색자 공통 지침)

## 우리가 알고 싶은 단 하나
"이 엔진에서 **사람이 타이핑해서 음악을 통제할 수 있는 면(control surface)**이 정확히 무엇인가."
장르 목록·마케팅 문구가 아니라 **입력 채널·문법·파라미터 이름·문자 제한·관측된 거동**이다.

## 절대 규칙
1. **모든 사실 주장에 출처 URL을 붙인다.** 출처 없는 값은 `null` + `"unknown"`. 추측 금지.
2. 공식 문서/API 레퍼런스 > 개발자 블로그 > 논문 > 커뮤니티(Reddit/Discord) 순. 각 항목에 `evidence` 등급을 적는다.
   - `E1` 공식 문서·API 레퍼런스 / `E2` 공식 블로그·릴리스노트 / `E3` 논문·기술리포트 / `E4` 커뮤니티 관측(미검증)
3. **"태그가 노래로 불리는가"** 같은 거동 질문은 반드시 `E`등급과 함께. 모르면 모른다고 쓴다.
4. 한국어로 서술, 고유명사·파라미터 이름은 원문 그대로.

## 출력 형식
마지막에 ```json 펜스 하나로만 출력. 스키마:

```
{
  "cluster": "<클러스터명>",
  "engines": [{
    "engine": "", "vendor": "", "status": "live|beta|research|discontinued",
    "models": [{"name":"","released":"","notes":"","url":""}],
    "access": [{"channel":"web|api|app|sdk","url":"","price_note":"","commercial_use":""}],
    "control_surface": {
      "text_prompt": {"exists":null,"char_limit":null,"evidence":"","url":"","notes":""},
      "lyrics_field": {"exists":null,"syntax":"","evidence":"","url":"","notes":""},
      "structure_tags": {"exists":null,"syntax_examples":[],"tags_are_sung":{"answer":"yes|no|partial|unknown","evidence":"","url":""},"evidence":"","url":""},
      "duration_control": {"exists":null,"how":"","evidence":"","url":""},
      "reference_audio": {"exists":null,"how":"","evidence":"","url":""},
      "negative_prompt": {"exists":null,"how":"","evidence":"","url":""},
      "seed_determinism": {"exists":null,"how":"","evidence":"","url":""},
      "stems_export": {"exists":null,"how":"","evidence":"","url":""},
      "inpaint_extend_edit": {"exists":null,"how":"","evidence":"","url":""},
      "instrumental_toggle": {"exists":null,"how":"","evidence":"","url":""},
      "vocal_control": {"exists":null,"how":"","evidence":"","url":""},
      "realtime_steering": {"exists":null,"how":"","evidence":"","url":""}
    },
    "api_params": [{"name":"","type":"","required":null,"doc_url":"","notes":""}],
    "documented_vocabulary": {"has_official_tag_list":null,"url":"","notes":""},
    "observed_behaviors": [{"claim":"","evidence":"E1|E2|E3|E4","url":""}],
    "gaps": [""]
  }],
  "cross_notes": "",
  "sources": [""]
}
```

## 반드시 답해야 하는 질문 (엔진마다)
- ⑴ 가사를 **따로 넣는 칸**이 있는가, 아니면 프롬프트 한 칸뿐인가?
- ⑵ `[Verse]` `[Chorus]` 같은 **구조 태그 문법**이 문서에 있는가? 문면 예시 그대로.
- ⑶ 대괄호 안 텍스트를 **지시로 읽는가, 노래로 부르는가**? (Suno는 지시로 읽음 — 이게 엔진 성질인지 일반 성질인지가 이 조사의 핵심)
- ⑷ 길이(초/마디)를 **숫자로 지시**할 수 있는가?
- ⑸ 레퍼런스 오디오 업로드 / continuation / inpainting이 되는가?
- ⑹ API가 있는가? 있으면 **파라미터 이름을 전부** 적는다.
- ⑺ 프롬프트 **문자 수 상한**은?
- ⑻ 공식 장르·태그 **목록 문서**가 존재하는가?
