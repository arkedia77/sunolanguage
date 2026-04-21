# sunomusic 업로드 배치 — 2026-04-21

작성: sunolanguage (reklcli)
목적: Suno 네이티브 어휘 확장 검증. 각 곡/샘플을 Suno 앱에 업로드 → 4값 세트(SP, lyrics, genre, subgenre) 수집.

---

## 작업 순서

### Priority A: 전통악기 곡 (Leo 가설 검증 — 최우선)

Suno가 전통악기(대금·가야금·해금·장구 등)를 자체 묘사에서 인식하는지 확인.
현재 corpus 318곡에 전통악기 언급 **0건**이므로, 이 곡들이 첫 검증 케이스.

| # | gid | title | batch | 키워드 | Suno URL |
|---:|---:|---|---|---|---|
| A1 | 1703 | 퇴근 후 | B184 | 장구 | https://suno.com/song/e7e4a997-eff5-4ff8-9368-b7ca670e7b61 |
| A2 | 10010 | 엄마의 된장찌개 | K001 | 해금 | https://suno.com/song/75ba7617-c17a-4f2b-a4eb-4e8c3a83f5eb |
| A3 | 65 | 모국어 | B017 | 가야금 | https://suno.com/song/f49cd884-0698-43bf-942d-958519faa3cf |
| A4 | 63 | 삼 분 | B017 | 피리 | https://suno.com/song/9ed7fcfe-6b40-45b2-b263-3ba923b3f5d9 |
| A5 | 10 | 은빛 칼날 | B011 | 장구 | https://suno.com/song/686a038a-43ec-4d73-8f87-6024e7155ef4 |
| A6 | 100 | 감사 편지 | B020 | 피리 | https://suno.com/song/c67f1777-e52f-4556-b734-ea47ceba38ea |
| A7 | 1018 | 알림 제로 | B113 | 해금 | https://suno.com/song/4c19d88f-d22c-4da3-a8c7-97f0288b6f6e |
| A8 | 1166 | 혼밥 D-day | B129 | 장구 | https://suno.com/song/73c2c9fa-1ea0-4636-a2fe-6de73f6670c5 |
| A9 | 1319 | 처음으로 모른다고 말한 날 | B144 | 장구 | https://suno.com/song/7aef3098-db83-40b9-a093-d14f4073969b |

**방법**: 각 곡 재생 → 전통악기 소리가 가장 잘 들리는 구간 10초 녹음 → Suno 앱 업로드

---

### Priority B: novel-word 상위곡 (v3 밖 어휘 검증)

이 곡들은 leomusic SP에 v3 어휘 밖 단어가 많이 투입됨. Suno가 재분석 시 어떤 표현을 쓰는지 대조 목적.

| # | gid | title | batch | novel U | Suno URL |
|---:|---:|---|---|---:|---|
| B1 | 1510 | 7시 23분의 사람 | B165 | 111 | https://suno.com/song/e59c7e59-fb33-4c9f-a696-5ab01952b948 |
| B2 | 1506 | 알림 999+ | B165 | 104 | https://suno.com/song/e2e72d3b-70b2-47c5-8342-74f5b833cfbe |
| B3 | 1724 | 다른 책 | B186 | 100 | https://suno.com/song/0e4df1c2-b86c-4ca8-b7f5-12c1c3f7a717 |
| B4 | 1509 | 건배사가 끝나면 | B165 | 98 | https://suno.com/song/c6f70247-2ef4-4f04-bd22-018d5dc77bc5 |
| B5 | 1719 | 저기요, | B186 | 97 | https://suno.com/song/e3095273-eaf3-4708-b435-9e14e7a2009c |
| B6 | 1720 | 인데요, | B186 | 97 | https://suno.com/song/b29b0776-ae8f-496c-8783-932f6c2373ae |
| B7 | 1372 | 아무도 모르는 출발 | B149 | 96 | https://suno.com/song/f3d17f06-9a58-4087-87dd-ca1eb6e7203b |
| B8 | 487 | 읽씹 3분 | B059 | 96 | https://suno.com/song/b03c858e-42a1-456f-9a39-6f702d065b23 |
| B9 | 1721 | 읽지 않음 | B186 | 95 | https://suno.com/song/839f85e6-341f-4e08-b163-04333dc1ceac |
| B10 | 1723 | 이어폰 반쪽 | B186 | 92 | https://suno.com/song/7d0ae565-b69a-4a80-80a3-d50f8b444cd6 |
| B11 | 1373 | 번호 5번, 3명이 남았다 | B149 | 91 | https://suno.com/song/2c6e6f20-41ce-4fb9-8483-e1a1f01bb9bd |
| B12 | 1725 | 같은 책이었다 | B187 | 91 | https://suno.com/song/7ab08c5c-c9c1-48bc-bb78-a0163eefc19d |
| B13 | 1464 | 카메라 오프 | B160 | 86 | https://suno.com/song/5a37847d-d27f-4949-a838-ba5497534094 |
| B14 | 1727 | 사실은 | B187 | 86 | https://suno.com/song/9690160e-de6d-45f5-ba00-f2cf021aa23d |
| B15 | 1484 | 열두 분 | B162 | 85 | https://suno.com/song/8efc68fc-263b-4b33-95c7-55fad72861e2 |

**방법**: 전곡 또는 1분 구간 → Suno 앱 업로드 → 4값 수집

---

### Priority C: 외부 음원 — 비기본 악기 solo

freesound.org 등에서 다운로드 → 10초 슬라이스 → Suno 앱 업로드.
**목적**: Suno가 이 악기를 어떤 이름/표현으로 묘사하는지 확인.

| # | 악기 | 소스 | 비고 |
|---:|---|---|---|
| C1 | Erhu (얼후) | https://freesound.org/people/tarane468/packs/26451/ | Chinese Erhu pack — 다운 후 solo 구간 10초 |
| C2 | Koto + Shamisen | https://freesound.org/people/zagi2/sounds/222655/ | CC, koto shamisen loop |
| C3 | Theremin | https://freesound.org/people/realtheremin/ | 실제 테레민, 프로필 내 파일 여러 개 |
| C4 | Hurdy Gurdy | https://freesound.org/people/fallbackcrush/sounds/365190/ | 88.2 kHz WAV, 하디거디 solo |
| C5 | Hurdy Gurdy texture | https://freesound.org/people/missionariojose/sounds/205623/ | 텍스처 녹음 |
| C6 | Sitar + Tabla | https://freesound.org/people/cmlooi/sounds/330350/ | 시타르/타블라/벨 혼합 |
| C7 | Sitar (태그 탐색) | https://freesound.org/browse/tags/sitar/ | 태그 내 최적 solo 1-2개 선택 |

---

### Priority D: 외부 음원 — 이펙트 샘플

| # | 이펙트 | 소스 | 비고 |
|---:|---|---|---|
| D1 | Riser / Sweep | https://freesound.org/people/MikeOscarFoxtrot/packs/27382/ | Risers, Sweeps and Drops pack |
| D2 | Tension Riser | https://freesound.org/people/original_sound/sounds/493542/ | Tension Building Riser Whoosh |
| D3 | Whoosh | https://mixkit.co/free-sound-effects/whoosh/ | 무료, 여러 종류 |
| D4 | Vinyl Crackle | https://freesound.org/people/Anthousai/packs/22442/ | Vinyl Crackle pack |
| D5 | Vinyl start/end | https://freesound.org/people/lulyc/packs/19233/ | start/end crackle |
| D6 | Tape Hiss | https://99sounds.org/vinyl-noise-sfx/ | Free Vinyl Noise SFX (CC) |
| D7 | Bitcrushed | https://samplefocus.com/tag/bitcrushed | 태그 내 최적 1-2개 선택 |

---

## 결과 수집 포맷

각 업로드 건별 다음 정보 기록:

```json
{
  "source_id": "A1",
  "source_type": "internal|external",
  "gid": 1703,
  "source_url": "https://suno.com/song/...",
  "recorded_section": "0:45-0:55",
  "suno_result": {
    "sp": "(Suno가 생성한 SP 전문)",
    "lyrics": "(Suno가 인식한 가사)",
    "genre": "",
    "subgenre": ""
  },
  "notes": "장구 소리 명확히 들림"
}
```

**결과 파일**: `sunolanguage/data/reanalysis_v2/sunomusic_batch_20260421.json`

---

## 시간 예상

- Priority A (9곡): ~30분
- Priority B (15곡): ~45분
- Priority C (7건): ~30분 (다운로드 포함)
- Priority D (7건): ~30분

총 ~2.5시간. A → B → C → D 순서. 시간 부족 시 A + C 우선.

---

## 핵심 질문 (업로드 후 확인)

1. **전통악기**: Suno가 `janggu`, `haegeum`, `gayageum`, `piri`, `daegeum` 중 하나라도 언급하는가?
2. **Novel 단어**: leomusic이 SP에 쓴 `bitcrushed`, `ambient-wide`, `asmr-close` 같은 표현이 Suno 재분석에도 등장하는가?
3. **이펙트**: Suno가 riser/sweep/crackle을 어떤 단어로 묘사하는가?
