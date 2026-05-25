# S_INST200 — 200곡 코퍼스 공백 타겟팅 배치 프로토콜

**시리즈**: S_INST200
**설계일**: 2026-05-25 (v2 — gap-targeting redesign)
**목적**: 기존 코퍼스(437곡)의 조성/BPM/박자/악기/장르 공백을 체계적으로 채움
**원칙**: "좋은 음악"이 아니라 "안 해본 것". 토큰 버릴 각오로 Suno 한계 탐색.

---

## 1. 기존 코퍼스 공백 분석

### 조성 — 7개 루트 노트 0건
| Root | 코퍼스 곡수 | → S_INST200 배분 |
|------|-----------|-----------------|
| E | 73 | **2** (의도적 축소) |
| G | 88 | **0** (의도적 배제) |
| **A** | **0** | **36** |
| **Bb** | **0** | **30** |
| **Db** | **0** | **27** |
| **Eb** | **0** | **25** |
| **Ab** | **0** | **24** |
| **F#** | **0** | **18** |
| **C#** | **0** | **14** |

### 장단조 — Major 84% 편향
| Mode | 코퍼스 | → S_INST200 |
|------|--------|-------------|
| Major | 84% | **35%** |
| Minor | 16% | **54.5%** |
| Modal | 0% | **9.5%** (Dorian, Phrygian, Lydian, Mixolydian, Locrian, Pentatonic, Whole Tone) |

### BPM — 70-79 과잉, 극값 부재
| 구간 | 코퍼스 | → S_INST200 |
|------|--------|-------------|
| <60 | **0건** | **34곡 (17%)** |
| 70-79 | 141(31.7%) | 축소 |
| 150+ | 25(5.6%) | **42곡 (21%)** |
| 범위 | 65-210 | **20-300** |

### 박자 — 4/4 외 사실상 미검증
| 박자 | 코퍼스 | → S_INST200 |
|------|--------|-------------|
| 4/4 | 228 (98%) | **115 (57.5%)** |
| 3/4 | 3 (1.3%) | **31 (15.5%)** |
| 6/8 | 1 (0.4%) | **16 (8%)** |
| 7/8 | 0 | **9 (4.5%)** |
| 5/4 | 0 | **8 (4%)** |
| 12/8 | 0 | **8 (4%)** |
| 2/4 | 0 | **5 (2.5%)** |
| 9/8 | 0 | **4 (2%)** |
| 11/8 | 0 | **4 (2%)** |

---

## 2. 설계 결과

| 항목 | 수치 |
|------|------|
| 고유 장르 | **200** (전곡 다른 장르) |
| 고유 악기 표현 | **344** |
| 송폼 | **26종** |
| 박자 | **9종** (비-4/4 = 42.5%) |
| BPM | **20~300** |
| 보컬 | **19곡 / 16개 언어** |
| 인스트루먼탈 | **181곡** |

### 보컬 언어 (19곡)
Italian(2), Korean(2), Portuguese(2), Urdu(1), Mongolian(1), Japanese(1), French(1), Spanish(1), German(1), Hindi(1), Swahili(1), Arabic(1), Mandarin(1), Irish Gaelic(1), Hawaiian(1), Turkish(1)

---

## 4. 세션 구조

| 세션 | ID 범위 | 곡수 | 보컬 | 특징 |
|------|---------|------|------|------|
| 1 | SI001–SI040 | 40 | 0 | 기본 장르 전역 스캔 |
| 2 | SI041–SI080 | 40 | 1 | frontier 장르 집중 |
| 3 | SI081–SI120 | 40 | 2 | 전자/R&B/World 확장 |
| 4 | SI121–SI160 | 40 | 5 | 민족악기 + 전통음악 집중 |
| 5 | SI161–SI200 | 40 | 10 | 보컬 집중 + 크로스장르 + 솔로 |

### 세션 워크플로우
```
1. /clear → 새 세션 시작
2. s_inst200_plan.json에서 해당 범위 40곡 로드
3. 각 곡별 SP 텍스트 생성 (sp_builder.py 참조 + 수동 커스텀)
4. 보컬 곡은 가사도 작성
5. JSON 배열로 저장 → data/s_inst200/session_N_sps.json
6. git add + commit + push
7. KANBAN 업데이트
8. /clear → 다음 세션
```

---

## 5. SP 생성 규칙

### 5.1 기본 구조 (§1.11 7문장 공식 준수)
1. **Genre opening**: `{Genre} [featuring {Vocal}] instrumental.`
2. **주악기**: 악기명 + 주법/수식어 + plays/provides/features
3. **보조악기**: 동일 패턴
4. **드럼/퍼커션**: The drums feature ...
5. **보컬** (보컬곡만): 보컬 묘사
6. **어레인지**: The arrangement is ...
7. **템포**: {BPM} BPM in {Key}, {time_sig} time signature.

### 5.2 글자수 제한
- **목표**: 400~600자 (코퍼스 평균 522자 기준)
- **최대**: 800자 (1000자 Suno 한계의 80%)
- 솔로/듀오 곡: 250~400자 허용

### 5.3 악기 묘사 규칙
- Suno 네이티브 어휘 우선 (사전 v3.1 참조)
- 브랜드명 사용 금지 (Fender, Gibson X → electric guitar O)
- 예외: TB-303, TR-909 등 Suno가 인식하는 기기명은 허용
- 구체적 주법 포함: fingerpicked, slapped, palm-muted, arpeggiated 등

### 5.4 민족악기 SP 전략
코퍼스에 없는 악기는 Suno 인식 불확실 → 3단 방어:
1. 악기 정식 명칭 사용 (erhu, koto, sitar 등)
2. 음색 설명 추가 ("two-stringed bowed instrument with a haunting tone")
3. 장르 라벨로 컨텍스트 제공 ("Chinese Traditional instrumental")

### 5.5 보컬 곡 가사 규칙
- 해당 언어로 2~3절 + 코러스 (또는 Strophic 형식)
- 주제: 보편적 (자연, 그리움, 기쁨) — 저작권 이슈 없는 오리지널
- [섹션 태그] 영어로 통일 ([Verse 1], [Chorus] 등)

---

## 6. DB 저장 포맷

### songs_test_lab INSERT
```sql
INSERT INTO songs_test_lab (test_id, series, sp, lyrics, genre, bpm, key_sig, time_sig, notes)
VALUES ({id}, 'S_INST200', '{sp}', '{lyrics}', '{genre}', {bpm}, '{key}', '{time}', '{notes}');
```

### session_N_sps.json 구조
```json
[
  {
    "id": "SI001",
    "genre": "Synth Pop",
    "sp": "Synth Pop instrumental. Arpeggiated synthesizer creates...",
    "lyrics": null,
    "char_count": 487,
    "instruments": ["arpeggiated synthesizer", "synth bass", "gated snare"],
    "form": "Verse-Chorus",
    "time": "4/4",
    "bpm": 118,
    "key": "A Minor"
  }
]
```

---

## 7. sunomusic 발주 포맷

### 내일(2026-05-26) 아침 발송 예정
5개 세션 완료 후 200곡 SP + 18곡 가사를 sunomusic에 일괄 발주.

발주 JSON 형식:
```json
{
  "series": "S_INST200",
  "total": 200,
  "sp_count": 200,
  "lyrics_count": 18,
  "instructions": "각 SP로 1곡씩 생성, 보컬곡은 가사 포함, 인스트루먼탈은 가사 없이",
  "reanalysis": "전곡 재분석 필요"
}
```

---

## 8. 컨텍스트 실현 가능성

| 항목 | 추정 토큰 |
|------|----------|
| 시스템 프롬프트 + 메모리 | ~8K |
| plan.json 40곡 참조 | ~6K |
| SP 생성 (40 × 500자) | ~25K |
| 가사 생성 (최대 10곡) | ~10K |
| 커밋/저장 작업 | ~3K |
| **합계** | **~52K** |
| Claude 컨텍스트 | 200K |
| **여유율** | **74%** |

→ 40곡/세션은 컨텍스트 안전 범위 내. 문제 없음.

---

## 9. 성공 기준

- [ ] 200곡 SP 전부 생성 (400~800자)
- [ ] 18곡 가사 포함
- [ ] 200 고유 장르 (중복 0)
- [ ] 민족악기 80종+ 테스트
- [ ] 비-4/4 박자 35곡+
- [ ] BPM 40~200 분포
- [ ] sunomusic 발주 완료
- [ ] 재분석 결과 수신 후 코퍼스 합류
