# 3070 드릴 비트 — Suno 자체분석 SP 리듬 어휘 분석 (2026-07-16)

**지시**: LEO 07-16 — 3070 LeoMusicOS 비트→Suno 업로드 시 Suno 자체분석 프롬프트에서 '우리가 모르는 리듬 용어' 채굴.
**소재**: 2건 (GRIND=london_grind_3070 uuid 7b899ec2 / Machine Drill=machine_drill_3070 uuid f4e9caed). sunomusic가 Upload 클립 clip API 직조회한 **순수 자체분석본**(Cover 편곡 덮어쓰기와 별개). 원문 `data/collection/beat_ref_3070_drill_suno_sp_20260716.json`.
**대조 베이스**: lexical_index 556트랙/17,822 + suno_dictionary_v3(v3.2).

---

## 판정: 신규 원자어휘 0 — 사전 갱신 불요

리듬/프로덕션 후보 28종 대조 결과, **코퍼스+사전 부재로 처음 잡힌 3종이 전부 기존 어휘의 변이/컴파운드**로 확인(false positive):

| 후보(0건) | 실제 커버 | 판정 |
|---|---|---|
| `open hats` | **`open hi-hat` 45건** | Suno 축약 표기, 개념 보유 |
| `industrial clap` | `clap` 83건 (+`industrial` 다수) | attested 구성어 컴파운드 |
| `four on the floor` | **`four-on-the-floor` 74건** | 하이픈 변이 |

thin(attested<3, 편입 보류): `rhythmic gating`(1)·`sawtooth synth lead`(1)·`acid-style synth`(2, 단 `acid synth` 10)·`high resonance`(2)·`low-end rumble`(2). 전부 단일 출처(본 2비트)라 **attested≥2 미충족 → 사전 편입 안 함**.

이미 견고: backbeat 245·off-beats 124·sixteenth-note pattern 137·sub-bass 304·four-on-the-floor 74·industrial techno 34·EBM 19·bitcrush 14. → 우리 코퍼스의 industrial/EDM/techno 곡들이 드릴 비트 리듬 어휘를 이미 포괄. **패션필름 교훈 재확인(novel=attested 컴파운드).**

---

## ★핵심 발견 (진짜 가치) — 장르 어휘 매핑: Drill → Industrial techno

3070·sunomusic 둘 다 이 비트들을 **"UK Drill/dark drill"**로 지칭했으나, **Suno 자체 분석은 두 곡 모두 "Industrial techno (with heavy EBM influences)"로 장르 판정**.

- **함의**: `drill`/`UK drill`이 Suno 장르 어휘에 약할 가능성. Suno는 드릴의 사운드(distorted overdriven kick·four-on-the-floor·metallic percussion·white-noise snare·acid synth)를 **industrial techno/EBM 프레임**으로 듣는다.
- **활용**: 드릴/다크 비트 계열 SP 작성 시 `drill` 단독 앵커보다 **`industrial techno`+`EBM`+구성 사운드어**가 Suno 반응 신뢰. (GT/trot 'Trot 라벨 드리프트' 발견과 동류 — 장르명보다 사운드 앵커.)
- **지위**: 관찰 2건(파일럿). suspicion 등재 수준, 단정 아님. sunomusic 표준 스텝(차기 비트 업로드마다 clip API 자동 캡처)으로 누적 → n 증가 시 재판정.

## 후속
- sunomusic가 **차기 3070 비트 업로드마다 Suno 자체분석 자동 캡처·회신**(표준 스텝 등재) → 누적분 재분석. thin 5종·drill→techno 매핑은 **attested≥2 도달 시** 각각 사전 technique 편입 / 장르 글로서리 등재 재검토.
- 본 파일럿 자체는 사전 갱신 0(정직).
