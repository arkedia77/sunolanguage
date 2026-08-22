# 이대 관현악과 특집 시리즈 (S002–S004)

## 이 시리즈는 무엇인가

S002부터 S004까지는 하나의 연속된 실험이다. 이화여대 관현악과에서 다루는 15개 악기 — 바이올린, 비올라, 첼로, 더블베이스, 하프, 플루트, 오보에, 클라리넷, 바순, 프렌치 호른, 트럼펫, 트롬본, 튜바, 팀파니, 그리고 다양한 타악기 — 를 세 가지 완전히 다른 각도에서 Suno에게 던져본다.

왜 하필 관현악기인가? sunolanguage 코퍼스 437곡을 분석해보니, Suno가 자발적으로 사용하는 악기 어휘는 놀라울 정도로 편향되어 있었다. electric bass가 693회, electric guitar가 547회 등장하는 반면, 오보에·더블베이스·프렌치 호른·튜바·팀파니는 단 한 번도 나타나지 않았다. 바이올린 7회, 플루트 1회. 관현악기는 Suno의 어휘에서 사실상 사각지대다.

그렇다면 질문은 세 가지로 나뉜다:
1. Suno가 이 악기들을 **아예 모르는 건가**, 아니면 스스로 **쓰지 않을 뿐인가**?
2. 알아듣는다면, **주법의 차이**까지 구분하는가?
3. 클래식이 아닌 **다른 장르**에 넣어도 알아듣는가?

S002·S003·S004는 정확히 이 세 질문에 답하기 위해 설계되었다.

---

## S002 — "이 악기가 나오는가?" (존재 테스트)

**12곡 · 15악기 전수 · 2026-04-25 설계**

### 무엇을 테스트하는가

가장 기본적인 질문부터 시작한다. Suno에게 "바이올린을 연주해"라고 말하면, 실제로 바이올린 소리가 나오는가? "팀파니 롤을 넣어줘"라고 하면, 팀파니가 들리는가?

S002는 15개 악기를 다양한 조합으로 배치한 12곡이다. 현악만 모은 곡, 목관만 모은 곡, 금관만 모은 곡, 타악만 모은 곡을 만들고, 그 다음에는 코퍼스에서 한 번도 등장하지 않은 악기들 — 오보에, 더블베이스, 프렌치 호른, 튜바, 팀파니 — 을 주인공으로 세운 듀오·솔로 곡을 만들었다. 마지막에는 15악기 전부를 하나의 풀 오케스트라 곡에 넣어봤다.

### 12곡 구성

| 곡 | 제목 | 무엇을 확인하는가 |
|---|---|---|
| 01 | Dawn Over the Han River | 현악 5중주 — violin, viola, cello, double bass, harp가 각각 들리는가 |
| 02 | The Woodwind Garden | 목관 4중주 — flute, oboe, clarinet, bassoon이 구분되는가 |
| 03 | Fanfare for the Forgotten | 금관 5중주 — trumpet, french horn, trombone, tuba가 나오는가 |
| 04 | Percussion Ritual | 타악 앙상블 — timpani, snare, cymbals, triangle 등이 개별 인식되는가 |
| 05 | Elegy in Amber | 오보에 + 하프 듀오 — 코퍼스 0회 악기 2개를 주인공으로 |
| 06 | The Iron Waltz | 튜바 + 트롬본 듀오 — 코퍼스 0회 저음 금관의 무거운 왈츠 |
| 07 | Sunlight Through Stained Glass | 풀 오케스트라 — 15악기 전부 한 곡에 |
| 08 | 한강의 밤 | 한국어 가사 + 관현악 — Suno가 K-Pop으로 분류하는가, Orchestral로 분류하는가? |
| 09 | Bassoon Midnight | 바순 + 피아노 재즈 크로스오버 — 코퍼스 1회 악기의 장르 넘나들기 |
| 10 | Double Bass Dreams | 더블베이스 솔로 — 코퍼스 0회 악기의 무반주 독주 |
| 11 | Clarinet Noir | 클라리넷 + 현악 — 필름 누아르 분위기에서 클라리넷의 음색 |
| 12 | Luce Notturna | 이탈리아어 가사 + 소프라노 + 관현악 — 저작권 필터 + 장르 편향 이중 테스트 |

### 왜 이렇게 설계했는가

단순히 "악기 15개를 테스트한다"면 15곡 솔로를 만들면 될 일이다. 하지만 그건 Suno의 실제 사용 맥락과 동떨어져 있다. 음악에서 악기는 혼자 존재하지 않는다. 현악 5중주에서 비올라가 제 역할을 하는지, 금관 합주에서 프렌치 호른이 튜바와 분리되어 들리는지, 풀 오케스트라에서 15개가 동시에 존재할 때 뭉개지지 않는지 — 이런 것들이 실전에서 중요하다.

또 하나의 축은 **() 디렉션 확장 테스트**다. 가사 영역에서 `(instrumental)`을 넘어 `(humming, 아아아~)`, `(spoken softly)`, `(melismatic run on 'tu')`, `(resonant, from the belly of the instrument)` 같은 보컬/악기 행위 지시를 넣었다. S001에서 4개 모두 유효했던 () 디렉션을 9개로 확장하여 경계선을 탐색한다.

마지막 축은 **언어·장르 편향**이다. 한국어 가사를 넣으면 Suno가 자동으로 K-Pop으로 분류하는가? 이탈리아어를 넣으면 Opera로 가는가? 관현악 편성을 명시했는데도 장르 분류가 언어에 끌려가는지 확인한다.

---

## S003 — "주법에 따라 달라지는가?" (기법 테스트)

**12곡 · 주법/기법 40종 이상 · 2026-04-27 설계**

### S002와 무엇이 다른가

S002가 "오보에가 나오는가?"를 물었다면, S003은 "오보에의 비브라토와 스타카토가 다르게 들리는가?"를 묻는다.

음악 전공자에게 악기는 하나의 소리가 아니다. 바이올린 하나만 해도 arco legato(활로 부드럽게 긋기), spiccato(활을 튕기기), col legno(활의 나무 부분으로 치기), sul ponticello(브릿지 근처에서 긋기)는 완전히 다른 음색이다. 피아니시시모(ppp)와 포르티시시모(fff)는 단순한 볼륨 차이가 아니라 음악의 질감 자체가 바뀐다.

S003은 이 주법·기법 용어들을 Suno가 얼마나 세밀하게 이해하는지 테스트한다. 동시에, sunolanguage 코퍼스에서 **한 번도 등장하지 않은 기법 용어들** — ppp, fff, sfz(스포르잔도), fp(포르테피아노), al niente(소멸까지), sul ponticello, bisbigliando 같은 전공자 용어 — 이 Dead Zone에 속하는지 아니면 Suno가 이해하지만 스스로 쓰지 않는 수동 이해 영역인지 판별한다.

### 12곡 구성

| 곡 | 제목 | 무엇을 확인하는가 |
|---|---|---|
| 01 | Four Faces of the Violin | 같은 바이올린으로 arco legato → spiccato → col legno → sul ponticello 4가지 보잉을 순서대로 연주. 음색 차이가 나는가? |
| 02 | Cello: From Earth to Sky | 첼로의 가장 낮은 C현부터 thumb position 고음역, 그리고 하모닉스까지 — 음역 전체를 관통하는 여행. Suno가 음역별 음색 변화를 표현하는가? |
| 03 | Flute Breath | 플루트의 확장 기법 총집합 — flutter tonguing(혀를 굴리며 부는 트레몰로), overblowing(과도하게 불어 상위 배음 추출), multiphonics(연주하면서 동시에 노래하기), whistle tone(유령 같은 최약음 하모닉스). Suno가 "일반 플루트"와 구분되는 소리를 만드는가? |
| 04 | Oboe: Reed and Breath | 오보에와 잉글리시 호른의 더블 리드 표현력 — 비브라토 종류, 레가토 대 스타카토, 피아니시모에서 포르티시모까지의 다이내믹 범위. 더블 리드 특유의 음색이 나오는가? |
| 05 | Clarinet Chameleon | 클라리넷의 3개 음역(chalumeau 저음역의 어두운 우디 톤, clarion 중음역의 밝은 프로젝션, altissimo 고음역의 날카로운 집중) + Gershwin 스타일 포르타멘토 글리산도. 한 악기 안에서 세 가지 성격이 나오는가? |
| 06 | Horn Calls and Whispers | 프렌치 호른의 기법 5종 — open horn(영웅적), stopped horn(금속적), hand muting(점진적 변화), bell up(직접 프로젝션), echo horn(산 너머 메아리). 같은 호른에서 5가지 음색이 나오는가? |
| 07 | Three Mutes of the Trumpet | 트럼펫 뮤트 3종 비교 — straight mute(얇고 집중), cup mute(따뜻하고 머플), harmon mute(Miles Davis의 속삭임). 같은 멜로디를 4번(open + 3뮤트) 연주하여 직접 비교. Suno가 뮤트별 차이를 만드는가? |
| 08 | Trombone: The Slide as Voice | 트롬본 + 베이스 트롬본 — 슬라이드 글리산도, 립 트릴, 더블 텅잉, 멀티포닉스(연주하면서 노래), 페달 톤. 트롬본 고유의 슬라이드 기법이 반영되는가? |
| 09 | Harp: Colors of the Strings | 하프만의 고유 기법 — bisbigliando(인접 두 줄의 초고속 트레몰로), harmonics(줄 중간을 터치한 투명한 음), près de la table(공명판 근처 연주로 금속적 음색), 다양한 글리산도, 페달 버즈. 하프가 "아르페지오 기계" 이상의 존재가 되는가? |
| 10 | Timpani Master | 팀파니 기법의 모든 것 — 펠트 말렛 vs 나무 스틱의 음색 차이, 손가락 롤, 뮤트 스트로크, 페달 글리산도(연주 중 음높이 변화), 튜닝 체인지(연주 도중 리튜닝). 팀파니가 멜로디 악기가 될 수 있는가? |
| 11 | String Orchestra: Texture Lab | 현악 합주의 텍스처 사전 — con sordino(약음기, 은빛 베일), senza sordino(약음기 제거, 풍성한 원음), divisi(4성부 분리), sul tasto(지판 위 주법, 플루트 같은 음색), tremolo(급속 활 교체), col legno battuto(활 나무로 줄 두드리기, 비 내리는 소리). 6가지 텍스처가 각각 구분되는가? |
| 12 | Orchestra Dynamics: From Silence to Thunder | 풀 오케스트라 15악기의 다이내믹 스트레스 테스트 — ppp(거의 들리지 않는 속삭임)에서 시작하여 32마디에 걸쳐 fff(벽을 때리는 소리)까지 크레셴도. sfz(갑작스러운 폭발), fp(강하게 쳤다가 즉시 약하게), subito piano(경고 없이 볼륨 차단), diminuendo al niente(절대적 무음으로 소멸). Suno가 다이내믹 용어를 이해하는가? |

### 이 테스트가 왜 중요한가

sunolanguage 코퍼스 분석에서 흥미로운 패턴이 발견되었다. Suno는 음악을 묘사할 때 "key of D major"(652회)처럼 조성은 구체적으로 말하지만, "sforzando"나 "pianississimo" 같은 다이내믹 마킹은 단 한 번도 사용하지 않았다. 구체적인 코드명은 0회에 가깝다(출력층 1곡). ⚠**단 「코드 진행 0회」는 2026-08-22 반증됐다** — `chord progression`(단수) 출력층 **28곡** · `chords` **269곡**. Suno는 코드를 많이 말하고, **이름만 안 붙인다**(교재 §5.1 정정표).

이것은 Suno가 이 개념들을 **모르기** 때문인가, 아니면 자기만의 방식으로 표현할 뿐인가? 예를 들어 Suno는 "pianississimo"라고 쓰는 대신 "barely audible, a whisper"라고 쓸 수 있다. S003의 12번 곡은 바로 이 질문에 답한다 — 전공자 다이내믹 용어를 직접 넣었을 때 Suno가 어떻게 반응하고, 재분석 시 그 용어를 어떻게 번역하는지 관찰한다.

---

## S004 — "다른 장르에서도 알아듣는가?" (맥락 테스트)

**12곡 · 12개 장르 교차 · 2026-04-27 설계**

### 왜 장르를 바꿔보는가

S002에서 관현악기가 존재하는 것을 확인하고, S003에서 주법까지 세밀하게 테스트했다면, 마지막 질문이 남는다: **이 악기들은 클래식 맥락에서만 작동하는가?**

실제 현대 음악에서 관현악기는 온갖 장르에 등장한다. 바이올린은 EDM 트랙의 빌드업에, 첼로는 lo-fi hip hop의 샘플에, 트럼펫은 마리아치에, 하프는 켈틱 포크에, 팀파니는 심포닉 메탈에. 관현악기가 클래식 바깥에서도 자기 정체성을 유지하는지, 아니면 Suno가 장르에 끌려가서 "strings"나 "brass"라는 뭉뚱그린 표현으로 치환해버리는지 — 이것이 S004의 핵심이다.

### 12곡 구성 — 악기 하나 × 장르 하나

| 곡 | 제목 | 관현악기 | 교차 장르 | 무엇을 확인하는가 |
|---|---|---|---|---|
| 01 | Violin Drop | violin | Future Bass / EDM | 바이올린이 신스 리드를 대체할 수 있는가? 드롭에서 바이올린 아르페지오가 살아남는가? |
| 02 | Cello Beats | cello | Lo-fi Hip Hop | 첼로 루프 + 비닐 크래클 + boom-bap 드럼. Suno가 "classical"로 분류하는가 "lo-fi hip hop"으로 분류하는가? |
| 03 | Flauta na Praia | flute | Bossa Nova | 보사노바에서 기타 대신 플루트가 리드. 브라질 음악의 쇼루 전통과 맞닿는 자연스러운 조합인데, Suno는 이걸 아는가? |
| 04 | Oboe in the Machine | oboe | Ambient Electronic | 오보에의 리디한 음색이 그래뉼러 신디시스를 만나면? 어쿠스틱과 디지털의 경계. 재분석 시 "oboe"가 유지되는가 "reed instrument"로 바뀌는가? |
| 05 | Klezmer Clarinet | clarinet | Klezmer / Balkan Folk | 동유럽 민속 음악의 클라리넷 — krekhts(울음), 벤딩, 장식음. klezmer는 코퍼스 0건 장르인데 Suno가 이해하는가? |
| 06 | Horn of the Titans | french horn | Cinematic Epic Trailer | 8대의 프렌치 호른 유니즌 + 타이코 드럼. 시네마틱 트레일러는 Suno가 잘 아는 장르인데, 여기서 호른을 구체적으로 지정하면 "brass section"과 다르게 나오는가? |
| 07 | Trompeta Caliente | trumpet | Mariachi / Latin | 마리아치 트럼펫 듀엣 + 기타론 + 비우엘라. mariachi는 코퍼스 0건 — Suno가 멕시코 음악 스타일의 트럼펫을 알고 있는가? |
| 08 | Bone Funk | trombone | Funk / Soul | 펑크 호른 섹션의 트롬본 + 슬랩 베이스 + 클라비넷. 트롬본의 "growl"과 "플런저 뮤트 와와"가 펑크 맥락에서 나오는가? |
| 09 | Harp of the Highlands | harp | Celtic Folk / Irish | 콘서트 하프를 아이리시 전통 스타일로 — 오픈 5도 드론, AABB 릴 구조. 틴 휘슬과 보드란과 함께. 하프의 장르 적응력 테스트 |
| 10 | Bassoon Tango | bassoon | Argentine Tango | 바순이 반도네온을 대체한다! 피아솔라 스타일의 누에보 탱고에서 바순의 어두운 테너 음역이 탱고와 어울리는가? 재분석 시 "bassoon"이 "bandoneon"으로 바뀌는가? |
| 11 | Rockabilly Bull Fiddle | double bass | Rockabilly | 더블베이스의 슬랩 주법 — 줄을 지판에 때려 찰칵거리는 소리. 클래식 더블베이스가 로커빌리에서 "bull fiddle"로 변신. 재분석에서 "double bass"가 유지되는가 "upright bass"로 바뀌는가? |
| 12 | Timpani Thunder Metal | timpani | Symphonic Metal | 팀파니가 킥드럼을 대체하고, 디스토션 기타와 남성 합창과 공존. 심포닉 메탈에서 팀파니의 튜닝 체인지가 하모니를 따라가는가? |

### 핵심 관찰 포인트

S004의 분석에서 가장 주목할 것은 **재분석 시 악기 이름의 생존율**이다.

sunolanguage 코퍼스를 보면, Suno는 자발적으로 "strings"(65회), "brass section"(54회) 같은 통합 표현을 즐겨 쓴다. 그런데 우리가 "violin"이라고 구체적으로 지정하면, Suno가 재분석할 때도 "violin"이라고 유지하는가? 아니면 "strings"로 뭉뚱그리는가?

이 질문은 단순한 호기심이 아니다. Suno가 구체적 악기명을 통합 표현으로 치환한다면, SP를 쓸 때 "violin"이라고 쓰는 것과 "strings"라고 쓰는 것 사이에 실제 음악적 차이가 없을 수도 있다는 뜻이다. 반대로 악기명이 유지된다면, 구체적으로 쓸수록 구체적인 결과를 얻는다는 증거가 된다.

또 하나는 **장르 태깅 편향**이다. "violin + EDM"을 Suno에게 주면, 재분석 시 장르가 "future bass"로 나오는가 "orchestral electronic"으로 나오는가? 악기가 장르를 끌어당기는가, 장르가 악기를 끌어당기는가?

---

## 3중 검증 프레임워크

S002, S003, S004는 같은 15개 악기를 세 가지 축으로 교차 검증한다:

```
         S002 (존재)          S003 (기법)          S004 (맥락)
         ──────────          ──────────          ──────────
질문     "나오는가?"          "구분하는가?"        "어디서든 되는가?"

violin   현악 5중주에서       arco/spiccato/      EDM 드롭에서
         소리가 나는가        col legno 차이가     리드 악기로 되는가
                             들리는가

oboe     하프와 듀오로        비브라토/레가토/     앰비언트 일렉트로닉에서
         나오는가             다이내믹 범위가      그래뉼러와 공존하는가
                             표현되는가

timpani  타악 앙상블에서      스틱 종류/뮤트/      심포닉 메탈에서
         개별 인식되는가      글리산도가           킥드럼을 대체하는가
                             구분되는가
```

이 3중 구조 덕분에, 결과가 나오면 각 악기에 대해 다음과 같은 레포트 카드를 작성할 수 있다:

- **존재 점수**: Suno가 이 악기의 소리를 생성할 수 있는가 (S002)
- **표현력 점수**: 주법·기법에 따른 음색 차이를 만들 수 있는가 (S003)  
- **범용성 점수**: 클래식 바깥 장르에서도 정체성을 유지하는가 (S004)

최종적으로 이 36곡(S002 12 + S003 12 + S004 12)의 라운드트립 결과를 분석하면, sunolanguage 코퍼스에 관현악 영역의 완전한 지도가 추가된다. 코퍼스 437곡에서 발견할 수 없었던 관현악기 어휘가 36곡의 제어된 실험에서 드러나는 것이다.

---

## 실험 순서와 의존 관계

```
S001 Dead Budget (완료)
  ↓ 클래식 전공 용어 기초 반응 확인
S002 존재 테스트 (sunomusic 생성+재분석 대기)
  ↓ 결과 수신 후 분석 → S003 발주
S003 기법 테스트 (프롬프트 설계 완료, 발주 완료)
  ↓ S002와 같은 악기이므로 비교 분석 가능
S004 장르 교차 테스트 (프롬프트 설계 완료, 발주 완료)
  ↓ S003 완료 후 순차 진행
통합 분석
  → 악기별 3차원 레포트 카드
  → 책 3·4장 데이터 기반
```

각 시리즈는 독립적으로 분석 가능하지만, 세 시리즈를 교차하면 훨씬 풍부한 인사이트가 나온다. 예를 들어 S002에서 오보에가 잘 나왔는데 S003에서 비브라토 표현이 안 되면, "Suno는 오보에를 알지만 피상적으로만 안다"는 결론이 나온다. S003에서 주법까지 잘 되는데 S004에서 앰비언트에 넣으니 사라지면, "Suno는 오보에를 클래식에서만 이해한다"는 결론이 된다.

---

## 부록: 전체 곡 목록 (36곡)

### S002 — 존재 테스트 (12곡)
| ID | 제목 | 악기 조합 |
|---|---|---|
| S002_01 | Dawn Over the Han River | violin, viola, cello, double bass, harp |
| S002_02 | The Woodwind Garden | flute, oboe, clarinet, bassoon |
| S002_03 | Fanfare for the Forgotten | trumpet, french horn, trombone, tuba |
| S002_04 | Percussion Ritual | timpani, snare, cymbals, triangle, tambourine, bass drum |
| S002_05 | Elegy in Amber | oboe, harp |
| S002_06 | The Iron Waltz | tuba, trombone |
| S002_07 | Sunlight Through Stained Glass | 15악기 전부 |
| S002_08 | 한강의 밤 | violin, cello, flute, french horn, harp + 바리톤 |
| S002_09 | Bassoon Midnight | bassoon, piano |
| S002_10 | Double Bass Dreams | double bass solo |
| S002_11 | Clarinet Noir | clarinet, violin, viola, cello |
| S002_12 | Luce Notturna | soprano, violin, cello, flute, oboe, french horn, harp, timpani |

### S003 — 기법 테스트 (12곡)
| ID | 제목 | 핵심 기법 |
|---|---|---|
| S003_01 | Four Faces of the Violin | arco legato / spiccato / col legno / sul ponticello |
| S003_02 | Cello: From Earth to Sky | 저음역 → thumb position → harmonics |
| S003_03 | Flute Breath | flutter tonguing / overblowing / multiphonics / whistle tone |
| S003_04 | Oboe: Reed and Breath | 더블 리드 비브라토 / 다이내믹 범위 |
| S003_05 | Clarinet Chameleon | chalumeau / clarion / altissimo / 글리산도 |
| S003_06 | Horn Calls and Whispers | stopped / open / muting / bell up / echo |
| S003_07 | Three Mutes of the Trumpet | straight / cup / harmon mute 비교 |
| S003_08 | Trombone: The Slide as Voice | 글리산도 / 립 트릴 / 더블 텅잉 / 멀티포닉스 |
| S003_09 | Harp: Colors of the Strings | bisbigliando / harmonics / près de la table |
| S003_10 | Timpani Master | 스틱 종류 / 뮤트 / 페달 글리산도 / 튜닝 체인지 |
| S003_11 | String Orchestra: Texture Lab | divisi / con sordino / sul tasto / tremolo / col legno battuto |
| S003_12 | Orchestra Dynamics | ppp→fff / sfz / fp / subito piano / al niente |

### S004 — 장르 교차 테스트 (12곡)
| ID | 제목 | 악기 × 장르 |
|---|---|---|
| S004_01 | Violin Drop | violin × EDM |
| S004_02 | Cello Beats | cello × Lo-fi Hip Hop |
| S004_03 | Flauta na Praia | flute × Bossa Nova |
| S004_04 | Oboe in the Machine | oboe × Ambient Electronic |
| S004_05 | Klezmer Clarinet | clarinet × Klezmer |
| S004_06 | Horn of the Titans | french horn × Cinematic Trailer |
| S004_07 | Trompeta Caliente | trumpet × Mariachi |
| S004_08 | Bone Funk | trombone × Funk |
| S004_09 | Harp of the Highlands | harp × Celtic Folk |
| S004_10 | Bassoon Tango | bassoon × Tango |
| S004_11 | Rockabilly Bull Fiddle | double bass × Rockabilly |
| S004_12 | Timpani Thunder Metal | timpani × Symphonic Metal |
