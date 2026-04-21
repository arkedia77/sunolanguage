# 외부 음원 소스 리드 — Suno 업로드 테스트용

작성일: 2026-04-20  ·  목적: 비기본 악기 solo + 이펙트 샘플을 Suno 앱에 업로드하여 네이티브 어휘 수집

## 1. 비서구/전통악기 solo

### 한국 전통악기
- **Splice: Sonic Collective - Gayageum Live Sounds Pack** (204 samples, 유료) — 가야금 라이브 샘플 pack
  - https://splice.com/sounds/packs/sonic-collective/gayageum/samples
- **YouTube: Echoes of Korea** — 가야금·해금·장구·대금 퓨전 (instrumental, 구간 추출용)
  - https://www.youtube.com/watch?v=r7fmFPunFgY
- **Sound of Asia (LA 악기점)** — gayageum/geomungo/janggu/buk/nantabuk 실물 판매 사이트 — 참고 페이지에 악기별 소개
  - https://www.soundofasia.com/
- freesound.org 직접 검색 필요: `daegeum`, `gayageum`, `haegeum`, `janggu`, `buk` — 일반 검색은 결과 희박
  - https://www.freesound.org/

### 중국 전통악기
- **Freesound: tarane468 — Chinese Erhu pack** — 얼후 샘플 팩
  - https://freesound.org/people/tarane468/packs/26451/
- **Sounds of China (Noiiz)** — pipa/yangqin/hulusi/xiao 24-bit wav 팩 (유료)
  - https://www.noiiz.com/sounds/packs/1126
- **Kong Audio - Chinese Orchestra Individuals** — 중국 전통악기 개별 라이브러리
  - https://chineekong.com/en/chinese-orchestra-individuals/

### 일본 전통악기
- **Freesound: zagi2 — koto and shamisen loop** — 코토+샤미센 루프 (CC)
  - https://freesound.org/people/zagi2/sounds/222655/

### 인도 전통악기
- **Freesound: cmlooi — sitar/tabla/bell 변환 샘플**
  - https://freesound.org/people/cmlooi/sounds/330350/
- **Freesound tags/sitar**
  - https://freesound.org/browse/tags/sitar/
- **Sample Focus: sitar**
  - https://samplefocus.com/categories/sitar

## 2. 특이 서구 악기 solo

### Theremin
- **Freesound: realtheremin user profile** — 실제 테레민 기반 업로더 (100% genuine theremin sounds)
  - https://freesound.org/people/realtheremin/
- **Freesound: NoiseCollector — Virtual Theremin pack**
  - https://freesound.org/people/NoiseCollector/packs/423/

### Hurdy Gurdy (허디거디)
- **Freesound: fallbackcrush — Hurdy Gurdy Battle Hymn** (88.2 kHz WAV)
  - https://freesound.org/people/fallbackcrush/sounds/365190/
- **Freesound: missionariojose — Hurdy Gurdy Textures 02**
  - https://freesound.org/people/missionariojose/sounds/205623/
- **Sonokinetic Hurdy Gurdy** (Kontakt 무료, 참고용) — 라이브러리 기반 톤 레퍼런스
  - https://www.sonokinetic.net/products/classical/hurdygurdy/

### Mellotron / 기타
- Freesound 직접 검색 필요 (표준 검색 결과 희박)

## 3. 이펙트 샘플

### Riser / Sweep / Whoosh / Impact
- **Freesound: MikeOscarFoxtrot — Risers, Sweeps and Drops pack**
  - https://freesound.org/people/MikeOscarFoxtrot/packs/27382/
- **Freesound: original_sound — Tension Building Riser Whoosh SFX** (.wav)
  - https://freesound.org/people/original_sound/sounds/493542/
- **Freesound tags/Riser** — 전체 riser 태그 브라우즈
  - https://freesound.org/browse/tags/Riser/
- **Mixkit Whoosh** (완전 무료, royalty-free)
  - https://mixkit.co/free-sound-effects/whoosh/
- **Pixabay risers** (무료)
  - https://pixabay.com/sound-effects/search/riser/
- **Abletunes 200+ riser pack (무료)**
  - https://abletunes.com/blog/free-riser-sound-effects-sample-pack/

### Vinyl Crackle / Tape Hiss
- **Freesound: Anthousai — Vinyl Crackle pack**
  - https://freesound.org/people/Anthousai/packs/22442/
- **Freesound: lulyc — Vinyl start/end crackle sounds**
  - https://freesound.org/people/lulyc/packs/19233/
- **99Sounds: Free Vinyl Noise SFX** (CC)
  - https://99sounds.org/vinyl-noise-sfx/
- **Brian Funk Ableton Pack #60 — Tape Hiss Vinyl Crackle**
  - https://brianfunk.com/blog/2012/07/19/free-ableton-pack-60-tape-hiss-vinyl-crackle

### Bitcrush / Granular / Lo-fi
- **Sample Focus: Bitcrushed tag**
  - https://samplefocus.com/tag/bitcrushed
- Freesound 직접 검색 권장: `bitcrush`, `granular`, `lo-fi texture`

## 4. 다음 액션 (발신 일괄 대기 중)

1. 위 리드 중 각 카테고리에서 **3~5개씩 구체 파일 선별**
2. 다운로드 → 10초 슬라이스 추출 (Audacity/ffmpeg)
3. Suno 앱 업로드 → 생성 프롬프트 수집
4. 결과 → `suspicion_tracker.json` + novel 어휘 v3 확장 후보 풀
5. sunomusic에 일괄 발신할 업로드 큐 포함

**현재 수집 범위**:
- 악기 9개 계열 (한국/중국/일본/인도 + theremin/hurdy gurdy)
- 이펙트 3개 계열 (riser·sweep / vinyl·tape / bitcrush·granular)
- leomusic 생성곡 novel-word 랭킹 100곡 (`data/reanalysis_v2/upload_queue.json`)
