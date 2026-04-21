# 배치 B192 SP 검토 — v3 + Suno corpus 기준

생성일: 2026-04-20  ·  v3 토큰 663 · Suno corpus 281,703자 (326 clips)

## 1. 곡별 요약

| gid | 제목 | 상태 | SP자 | novel단어 |
|---:|---|---|---:|---:|
| 1773 | 삼십 년 가마솥 | ✅ generated | 842 | 12 |
| 1774 | 붉은 띠 | ✅ generated | 990 | 12 |
| 1775 | 삼각김밥 | ✅ generated | 969 | 25 |
| 1776 | 삼 킬로 | ⏳ pending | 996 | 11 |
| 1777 | 하하 이모지 | ⏳ pending | 997 | 14 |
| 1778 | 빨간 풍선 | ⏳ pending | 999 | 19 |
| 1779 | 빌린 립스틱 | ⏳ pending | 973 | 12 |
| 1780 | 오 초 공백 | ⏳ pending | 964 | 15 |
| 1781 | 미역국 | ⏳ pending | 995 | 13 |
| 1782 | 삼십 초 | ⏳ pending | 966 | 16 |

## 2. novel 단어 — Suno corpus 교차 판정

| 단어 | 곡수 | gid | Suno corpus |
|---|---:|---|---|
| `final` | 4 | 1773, 1776, 1778, 1780 | ⚠️ Suno 2건 — 희귀 |
| `only` | 4 | 1774, 1778, 1781, 1782 | ⚠️ Suno 1건 — 희귀 |
| `belt` | 3 | 1776, 1777, 1780 | ✓ Suno 9건 — 네이티브 |
| `hushed` | 3 | 1775, 1778, 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `sixteenth-notes` | 3 | 1774, 1776, 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `stacked` | 3 | 1774, 1778, 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `alto` | 2 | 1779, 1782 | ⚠️ Suno 1건 — 희귀 |
| `around` | 2 | 1775, 1781 | ✓ Suno 5건 — 네이티브 |
| `chesty` | 2 | 1779, 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `closed` | 2 | 1774, 1779 | ✓ Suno 7건 — 네이티브 |
| `controlled` | 2 | 1773, 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `detuned` | 2 | 1775, 1777 | 🚨 Suno 0건 — 네이티브 아님 |
| `field` | 2 | 1775, 1778 | ✓ Suno 4건 — 네이티브 |
| `focusing` | 2 | 1779, 1782 | ✓ Suno 72건 — 네이티브 |
| `foley` | 2 | 1775, 1781 | ✓ Suno 4건 — 네이티브 |
| `gradually` | 2 | 1773, 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `hum` | 2 | 1774, 1782 | ✓ Suno 8건 — 네이티브 |
| `lift` | 2 | 1773, 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `nail-on-string` | 2 | 1778, 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `programmed` | 2 | 1774, 1777 | 🚨 Suno 0건 — 네이티브 아님 |
| `recording` | 2 | 1775, 1778 | ⚠️ Suno 2건 — 희귀 |
| `sob` | 2 | 1773, 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `thirds` | 2 | 1773, 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `airplane` | 1 | 1774 | 🚨 Suno 0건 — 네이티브 아님 |
| `anthemic` | 1 | 1776 | 🚨 Suno 0건 — 네이티브 아님 |
| `bed` | 1 | 1775 | ⚠️ Suno 1건 — 희귀 |
| `bedroom` | 1 | 1779 | 🚨 Suno 0건 — 네이티브 아님 |
| `bedside` | 1 | 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `big` | 1 | 1777 | ⚠️ Suno 2건 — 희귀 |
| `bleeps` | 1 | 1777 | 🚨 Suno 0건 — 네이티브 아님 |
| `bowed` | 1 | 1773 | 🚨 Suno 0건 — 네이티브 아님 |
| `cabin` | 1 | 1774 | 🚨 Suno 0건 — 네이티브 아님 |
| `chalky` | 1 | 1777 | 🚨 Suno 0건 — 네이티브 아님 |
| `chest-forward` | 1 | 1776 | 🚨 Suno 0건 — 네이티브 아님 |
| `chugs` | 1 | 1776 | 🚨 Suno 0건 — 네이티브 아님 |
| `clap` | 1 | 1777 | ⚠️ Suno 2건 — 희귀 |
| `claps` | 1 | 1778 | ✓ Suno 4건 — 네이티브 |
| `clavinet-adjacent` | 1 | 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `counter-line` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `crackle` | 1 | 1779 | ✓ Suno 13건 — 네이티브 |
| `crowd` | 1 | 1776 | 🚨 Suno 0건 — 네이티브 아님 |
| `daegeum` | 1 | 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `drone` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `drop` | 1 | 1780 | ✓ Suno 3건 — 네이티브 |
| `dropping` | 1 | 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `eighth-notes` | 1 | 1773 | 🚨 Suno 0건 — 네이티브 아님 |
| `elevator` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `enclosed` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `euphoric` | 1 | 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `evolution` | 1 | 1774 | 🚨 Suno 0건 — 네이티브 아님 |
| `evolving` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `fairground` | 1 | 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `felt-hammer` | 1 | 1773 | 🚨 Suno 0건 — 네이티브 아님 |
| `filtered` | 1 | 1775 | ⚠️ Suno 1건 — 희귀 |
| `flute` | 1 | 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `folk-tinged` | 1 | 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `full-band` | 1 | 1777 | ⚠️ Suno 2건 — 희귀 |
| `gaining` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `glass` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `glockenspiel` | 1 | 1778 | 🚨 Suno 0건 — 네이티브 아님 |
| `grounding` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `gutsy` | 1 | 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `hat` | 1 | 1776 | ✓ Suno 59건 — 네이티브 |
| `hiss` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `jazz-style` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-acoustic` | 1 | 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-dream` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-funk` | 1 | 1780 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-jazz` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-korean` | 1 | 1773 | 🚨 Suno 0건 — 네이티브 아님 |
| `k-neo-soul` | 1 | 1779 | 🚨 Suno 0건 — 네이티브 아님 |
| `kitchen` | 1 | 1781 | 🚨 Suno 0건 — 네이티브 아님 |
| `layback` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `lifting` | 1 | 1774 | 🚨 Suno 0건 — 네이티브 아님 |
| `lo-pass` | 1 | 1775 | 🚨 Suno 0건 — 네이티브 아님 |
| `melismatic` | 1 | 1779 | ⚠️ Suno 2건 — 희귀 |
| `mixed-to-falsetto` | 1 | 1774 | 🚨 Suno 0건 — 네이티브 아님 |
| `motor` | 1 | 1782 | 🚨 Suno 0건 — 네이티브 아님 |
| `near` | 1 | 1780 | ⚠️ Suno 1건 — 희귀 |
| `octave-doubled` | 1 | 1776 | 🚨 Suno 0건 — 네이티브 아님 |

## 3. Leo 확인 요청 — Suno 0건 단어 (네이티브 아님)

- `hushed` — 곡 1775, 1778, 1781
- `sixteenth-notes` — 곡 1774, 1776, 1780
- `stacked` — 곡 1774, 1778, 1780
- `chesty` — 곡 1779, 1782
- `controlled` — 곡 1773, 1781
- `detuned` — 곡 1775, 1777
- `gradually` — 곡 1773, 1778
- `lift` — 곡 1773, 1778
- `nail-on-string` — 곡 1778, 1781
- `programmed` — 곡 1774, 1777
- `sob` — 곡 1773, 1781
- `thirds` — 곡 1773, 1782
- `airplane` — 곡 1774
- `anthemic` — 곡 1776
- `bedroom` — 곡 1779
- `bedside` — 곡 1781
- `bleeps` — 곡 1777
- `bowed` — 곡 1773
- `cabin` — 곡 1774
- `chalky` — 곡 1777
- `chest-forward` — 곡 1776
- `chugs` — 곡 1776
- `clavinet-adjacent` — 곡 1780
- `counter-line` — 곡 1782
- `crowd` — 곡 1776
- `daegeum` — 곡 1778
- `drone` — 곡 1775
- `dropping` — 곡 1780
- `eighth-notes` — 곡 1773
- `elevator` — 곡 1782
- `enclosed` — 곡 1782
- `euphoric` — 곡 1778
- `evolution` — 곡 1774
- `evolving` — 곡 1775
- `fairground` — 곡 1778
- `felt-hammer` — 곡 1773
- `flute` — 곡 1778
- `folk-tinged` — 곡 1781
- `gaining` — 곡 1775
- `glass` — 곡 1775
- `glockenspiel` — 곡 1778
- `grounding` — 곡 1775
- `gutsy` — 곡 1780
- `hiss` — 곡 1775
- `jazz-style` — 곡 1782
- `k-acoustic` — 곡 1781
- `k-dream` — 곡 1775
- `k-funk` — 곡 1780
- `k-jazz` — 곡 1782
- `k-korean` — 곡 1773
- `k-neo-soul` — 곡 1779
- `kitchen` — 곡 1781
- `layback` — 곡 1782
- `lifting` — 곡 1774
- `lo-pass` — 곡 1775
- `mixed-to-falsetto` — 곡 1774
- `motor` — 곡 1782
- `octave-doubled` — 곡 1776
- `off-beat` — 곡 1779
- `oscillators` — 곡 1775
- `per` — 곡 1781
- `phaser` — 곡 1774
- `piano-driven` — 곡 1773
- `playful` — 곡 1777
- `post-chorus` — 곡 1777
- `quarter-notes` — 곡 1782
- `quirky` — 곡 1777
- `rain` — 곡 1775
- `restraint` — 곡 1775
- `retro-funk` — 곡 1780
- `silence` — 곡 1780
- `slowly` — 곡 1775
- `smoky` — 곡 1782
- `softness` — 곡 1773
- `stadium` — 곡 1776
- `starts` — 곡 1778
- `static` — 곡 1780
- `storybook` — 곡 1778
- `tape` — 곡 1775
- `toward` — 곡 1775
- `toy` — 곡 1777
- `ukulele` — 곡 1778
- `whimsical` — 곡 1778
- `whisper` — 곡 1777
