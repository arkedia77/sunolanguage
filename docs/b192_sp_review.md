# B192 10곡 SP 검토 — v3 어휘/문법 준수 실측

sunolanguage가 배포한 v3 어휘와 문법을 기준으로, 각 SP에 (a) v3에도 없고 (b) 파일럿이 inferred_vocab_used로 선언하지도 않은 **novel 단어**가 뭔지 스캔. 쓸데없이 들어간 건지, 확장 어휘로 추가할 가치가 있는지 Leo 판정 필요.

**v3 어휘 범위**: phrase 총 1191개 (토큰화 시 유니크 단어 663개)

## 1. 곡별 요약

| gid | 제목 | 상태 | SP자 | novel단어 | declared inferred |
|---:|---|---|---:|---:|---|
| 1773 | 삼십 년 가마솥 | ✅ generated | 842 | 10 | controlled sob |
| 1774 | 붉은 띠 | ✅ generated | 990 | 12 | layback phrasing, mixed-to-falsetto transition |
| 1775 | 삼각김밥 | ✅ generated | 969 | 24 | whispered verse |
| 1776 | 삼 킬로 | ❌ pending (폐기) | 996 | 10 | chest-forward belt |
| 1777 | 하하 이모지 | ❌ pending (폐기) | 997 | 14 | - |
| 1778 | 빨간 풍선 | ❌ pending (폐기) | 999 | 17 | airy head voice, warm daegeum flute |
| 1779 | 빌린 립스틱 | ❌ pending (폐기) | 973 | 9 | chesty open delivery, melismatic runs |
| 1780 | 오 초 공백 | ❌ pending (폐기) | 964 | 13 | gutsy belt |
| 1781 | 미역국 | ❌ pending (폐기) | 995 | 11 | controlled sob |
| 1782 | 삼십 초 | ❌ pending (폐기) | 966 | 14 | chesty open delivery, layback phrasing |

## 2. Leo 확인 요청 — v3 밖 novel 단어 (선언 없이 SP에 투입됨)

**판정 요청**: 각 단어에 대해 ① Suno가 반응 가능한 정상 어휘인가 ② v3 어휘에 추가할 확장 후보인가 ③ 쓸데없이 들어간 건가.

### 2-1. 2곡 이상 등장 (공통 novel — 더원 규칙이 밀어넣는 상수 후보)

| 단어 | 등장곡수 | 등장 gid | 성공/폐기 |
|---|---:|---|---|
| `final` | 4 | 1773, 1776, 1778, 1780 | ✅1/❌3 |
| `only` | 4 | 1774, 1778, 1781, 1782 | ✅1/❌3 |
| `hushed` | 3 | 1775, 1778, 1781 | ✅1/❌2 |
| `sixteenth-notes` | 3 | 1774, 1776, 1780 | ✅1/❌2 |
| `stacked` | 3 | 1774, 1778, 1780 | ✅1/❌2 |
| `alto` | 2 | 1779, 1782 | ✅0/❌2 |
| `around` | 2 | 1775, 1781 | ✅1/❌1 |
| `closed` | 2 | 1774, 1779 | ✅1/❌1 |
| `detuned` | 2 | 1775, 1777 | ✅1/❌1 |
| `field` | 2 | 1775, 1778 | ✅1/❌1 |
| `focusing` | 2 | 1779, 1782 | ✅0/❌2 |
| `foley` | 2 | 1775, 1781 | ✅1/❌1 |
| `gradually` | 2 | 1773, 1778 | ✅1/❌1 |
| `hum` | 2 | 1774, 1782 | ✅1/❌1 |
| `lift` | 2 | 1773, 1778 | ✅1/❌1 |
| `nail-on-string` | 2 | 1778, 1781 | ✅0/❌2 |
| `programmed` | 2 | 1774, 1777 | ✅1/❌1 |
| `recording` | 2 | 1775, 1778 | ✅1/❌1 |
| `thirds` | 2 | 1773, 1782 | ✅1/❌1 |

### 2-2. 곡별 고유 novel 단어 (해당 곡에만 등장)

**gid 1773 (삼십 년 가마솥) [✅ generated]**

- `bowed` (×1)
- `eighth-notes` (×1)
- `felt-hammer` (×1)
- `k-korean` (×1)
- `piano-driven` (×1)
- `softness` (×1)

**gid 1774 (붉은 띠) [✅ generated]**

- `airplane` (×1)
- `cabin` (×1)
- `evolution` (×1)
- `lifting` (×1)
- `mixed-to-falsetto` (×1)
- `phaser` (×1)

**gid 1775 (삼각김밥) [✅ generated]**

- `bed` (×1)
- `drone` (×1)
- `evolving` (×1)
- `filtered` (×1)
- `gaining` (×1)
- `glass` (×1)
- `grounding` (×1)
- `hiss` (×1)
- `k-dream` (×1)
- `lo-pass` (×1)
- `oscillators` (×1)
- `presence` (×1)
- `rain` (×2)
- `restraint` (×1)
- `saturation` (×1)
- `slowly` (×1)
- `tape` (×2)
- `toward` (×1)

**gid 1776 (삼 킬로) [❌ pending (폐기)]**

- `anthemic` (×2)
- `chest-forward` (×1)
- `chugs` (×1)
- `crowd` (×1)
- `hat` (×1)
- `octave-doubled` (×1)
- `stadium` (×1)
- `unison` (×1)

**gid 1777 (하하 이모지) [❌ pending (폐기)]**

- `belt` (×1)
- `big` (×1)
- `bleeps` (×1)
- `chalky` (×1)
- `clap` (×1)
- `full-band` (×1)
- `playful` (×1)
- `post-chorus` (×1)
- `quirky` (×1)
- `snaps` (×1)
- `toy` (×1)
- `whisper` (×1)

**gid 1778 (빨간 풍선) [❌ pending (폐기)]**

- `claps` (×1)
- `euphoric` (×1)
- `fairground` (×1)
- `glockenspiel` (×1)
- `starts` (×1)
- `storybook` (×1)
- `ukulele` (×2)
- `whimsical` (×1)

**gid 1779 (빌린 립스틱) [❌ pending (폐기)]**

- `bedroom` (×1)
- `crackle` (×1)
- `k-neo-soul` (×1)
- `off-beat` (×1)
- `persists` (×1)
- `vinyl` (×1)

**gid 1780 (오 초 공백) [❌ pending (폐기)]**

- `clavinet-adjacent` (×1)
- `drop` (×1)
- `dropping` (×1)
- `k-funk` (×1)
- `near` (×1)
- `retro` (×1)
- `retro-funk` (×1)
- `silence` (×2)
- `static` (×1)
- `wah-wah` (×1)

**gid 1781 (미역국) [❌ pending (폐기)]**

- `bedside` (×1)
- `folk-tinged` (×1)
- `k-acoustic` (×1)
- `kitchen` (×1)
- `per` (×1)
- `single` (×1)

**gid 1782 (삼십 초) [❌ pending (폐기)]**

- `counter-line` (×1)
- `elevator` (×1)
- `enclosed` (×1)
- `jazz-style` (×1)
- `k-jazz` (×1)
- `motor` (×1)
- `quarter-notes` (×1)
- `ride` (×1)
- `smoky` (×1)

## 3. 선언된 inferred_vocab (이미 추적 중)

이미 `inferred_vocab_used`로 명시 선언된 확장 어휘. 추적성은 확보됐지만 Suno 반응 보장은 없음 — 아래는 Leo 사전 승인 여부 확인 대상.

| phrase | 등장곡수 | 등장 gid | 성공/폐기 |
|---|---:|---|---|
| `chesty open delivery` | 2 | 1779, 1782 | ✅0/❌2 |
| `controlled sob` | 2 | 1773, 1781 | ✅1/❌1 |
| `layback phrasing` | 2 | 1774, 1782 | ✅1/❌1 |
| `airy head voice` | 1 | 1778 | ✅0/❌1 |
| `chest-forward belt` | 1 | 1776 | ✅0/❌1 |
| `gutsy belt` | 1 | 1780 | ✅0/❌1 |
| `melismatic runs` | 1 | 1779 | ✅0/❌1 |
| `mixed-to-falsetto transition` | 1 | 1774 | ✅1/❌0 |
| `warm daegeum flute` | 1 | 1778 | ✅0/❌1 |
| `whispered verse` | 1 | 1775 | ✅1/❌0 |

## 4. v3 10슬롯 문법 준수도 (휴리스틱 탐지)

| gid | genre | tempo_key_time | vocal_main | vocal_chorus | instrument | drums | arrangement | mixing | effect_electronic | effect_sound | 합계 |
|---:|---|---|---|---|---|---|---|---|---|---|---:|
| 1773 | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | · | 8 |
| 1774 | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 9 |
| 1775 | · | ✓ | ✓ | ✓ | ✓ | · | ✓ | ✓ | ✓ | ✓ | 8 |
| 1776 | · | ✓ | ✓ | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| 1777 | · | ✓ | · | ✓ | ✓ | · | ✓ | ✓ | ✓ | · | 6 |
| 1778 | · | ✓ | ✓ | · | ✓ | · | ✓ | ✓ | ✓ | ✓ | 7 |
| 1779 | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 9 |
| 1780 | · | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 9 |
| 1781 | · | ✓ | ✓ | ✓ | ✓ | · | ✓ | ✓ | ✓ | ✓ | 8 |
| 1782 | · | ✓ | ✓ | ✓ | ✓ | · | ✓ | ✓ | ✓ | · | 7 |
