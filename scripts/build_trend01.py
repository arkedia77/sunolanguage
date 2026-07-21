#!/usr/bin/env python3
# TREND01 — 최신 트렌드 반영 보컬 배치 10곡 빌드+적재+핸드오프
# LEO 직지시(kee 경유 07-21): 발주 시점 최신 음악 트렌드를 가사·장르 모두 반영. 완전 자율(무옵션) 진행.
# 자율 A&R 설계: 앨범 "로그오프(Log Off)" — 2026 글로벌 사운드 10종 × 온라인 세대 감정.
#   각 트랙 = 서로 다른 최신 글로벌 사운드 + 서로 다른 디지털 시대 감정. 한국어 가사, 보컬.
# 트랙설계 = 10 병렬 전문 서브에이전트 저작 → 본 스크립트가 검증·적재·핸드오프.
import os, json, datetime, psycopg2

THEME = "최신 트렌드 서베이 (Log Off) — 글로벌 사운드 × 온라인세대 감정"
ALBUM = "로그오프 (Log Off)"
BATCH = "TREND01"
GID0 = 30160  # 다음 가용: 30161~30170

SONGS = [
 {"pos":1,"title":"해 뜰 무렵 텅 빈 손","title_en":"Empty Hands at Sunrise",
  "genre":"Afro-house K-pop dance","genre_group":"Dance/Electronic",
  "sub":"Amapiano-inflected global crossover dance, groovy female vocal","bpm":115,"key":"F# minor","time_sig":"4/4",
  "trend":"Amapiano log-drum·shaker 그루브 + K-pop 훅 / 밤새 숏폼 도파민 소진 후 새벽의 공허를 역설적으로 춤추게",
  "sp":"A groovy Afro-house track with Amapiano-inflected K-pop dance energy, built for global crossover dance floors. Warm, rolling 4/4 groove at 115 BPM in F# minor. The foundation is a deep, bouncy log-drum bassline in classic Amapiano style, layered with soft shakers, crisp rimshots, tight hi-hats and airy percussion swing. Wide, warm synth pads bloom underneath a bright plucked synth lead and subtle piano stabs. Female lead vocal, smooth and soulful yet clubby, with breathy intimate verses and a confident, rhythmic delivery. Light vocal chops and airy harmonies fill the pre-chorus. The chorus is an irresistible, danceable hook — bittersweet melody over an uplifting Afro-house drop. Amapiano meets K-pop dance-pop: log-drum groove, shaker-driven percussion, lush pads, house four-on-the-floor kick, glossy modern production. Late-night, warm, hypnotic and groovy, made to move.",
  "lyrics":"""[Verse 1]
새벽 세 시 또 손끝만 움직여
끝없는 화면 빛에 눈이 시려
웃긴 클립에 웃다가 멈춰
왜 이렇게 텅 빈 걸까 내 안이

[Pre-Chorus]
한 번만 더 넘기면 채워질 것 같아
근데 채운 적 없잖아 밤새도록

[Chorus]
해가 뜨는데 내 손은 비었어
도파민을 좇다 다 흘려버렸어
텅 빈 채로 나 춤을 춰 춰
이 허무마저 비트에 실어 놔
오오오 빈손인데 왜 몸은 흔들려
오오오 새벽이 나를 밀어 밀어

[Verse 2]
좋아요 숫자가 날 안아주진 않아
스크롤 끝엔 아무도 없잖아
창밖은 벌써 파랗게 물들어
난 아직 어제에 갇혀 있는데

[Pre-Chorus]
눈 감으면 소리들이 아직 번쩍여
근데 남은 건 하나도 없잖아 정말

[Chorus]
해가 뜨는데 내 손은 비었어
도파민을 좇다 다 흘려버렸어
텅 빈 채로 나 춤을 춰 춰
이 허무마저 비트에 실어 놔
오오오 빈손인데 왜 몸은 흔들려
오오오 새벽이 나를 밀어 밀어

[Bridge]
로그드럼 위로 숨을 뱉어
공허도 리듬이 되면 견뎌
채우려 말고 그냥 흘러가
해 뜨는 이 방에서 나 혼자라도

[Chorus]
해가 뜨는데 내 손은 비었어
그래도 이 순간만은 진짜야
텅 빈 채로 나 춤을 춰 춰
이 허무마저 비트에 실어 놔
오오오 빈손인데 왜 몸은 흔들려
오오오 새벽이 나를 안아 안아"""},

 {"pos":2,"title":"우리 사이 뭐야","title_en":"What Are We",
  "genre":"Jersey club pop","genre_group":"Dance/Electronic",
  "sub":"밝은 신스 위 여성 보컬의 빠른 bounce 저지클럽 팝","bpm":138,"key":"F# minor","time_sig":"4/4",
  "trend":"저지클럽 bed-squeak 5연타 킥·chopped 보컬 / '우리 뭐냐' 못 묻는 시추에이션십 조바심을 초조하지만 신나게",
  "sp":"Jersey club pop, bright and bouncy, female vocal. This is club-ready Jersey club: fast bed-squeak kick pattern with the signature five-hit stutter (kick-kick-kick-kick-kick), snappy claps on the offbeat, rolling triplet bounce, 138 BPM in F# minor. Chopped and stuttered vocal samples flicker throughout, tiny pitched vocal chops used as a percussive hook. Airy female lead, bright and youthful, half-sung half-rapped in the verses then belting a sticky earworm chorus. Layered synths: glassy plucks, shimmering supersaw stabs, a warm sub bass locking to the kick. Bubbly, energetic, sugary pop production, radio-clean mix, punchy sidechained low end, crisp hi-hat rolls. Keep it playful, anxious-but-danceable, TikTok-catchy. Jersey club bounce, Jersey club pop, bright synth-pop with Jersey club drums, uptempo dance-pop, gummy hook energy throughout.",
  "lyrics":"""[Verse 1]
읽씹 삼 초 만에 좋아요 하나
그게 뭔데 왜 이렇게 신경 쓰여
프로필 사진 바뀐 거 또 확인해
나 지금 뭐 하는 거야 진짜

[Pre-Chorus]
물어보고 싶은데 못 물어봐
우리 이거 뭐냐고 뭐냐고
대답 대신 하트만 톡 톡 톡

[Chorus]
우리 사이 뭐야 뭐야 뭐야 (뭐야)
친구도 아니고 애인도 아냐 (아냐)
밀당인지 진심인지 몰라 몰라
그래도 좋아 미치겠어 어어어
우리 사이 뭐야 뭐야 뭐야 (뭐야)
답장은 안 와도 알림은 켜놔 (켜놔)
초조한데 왜 이렇게 신나 신나
말해줘 우리 뭐야 뭐야

[Verse 2]
안 읽은 척 읽고 읽은 척 안 읽고
너도 나처럼 재고 있는 거지
먼저 연락하면 지는 것 같아서
괜히 스토리만 다섯 번 봐

[Pre-Chorus]
물어보고 싶은데 못 물어봐
우리 이거 뭐냐고 뭐냐고
대답 대신 하트만 톡 톡 톡

[Chorus]
우리 사이 뭐야 뭐야 뭐야 (뭐야)
친구도 아니고 애인도 아냐 (아냐)
밀당인지 진심인지 몰라 몰라
그래도 좋아 미치겠어 어어어
우리 사이 뭐야 뭐야 뭐야 (뭐야)
답장은 안 와도 알림은 켜놔 (켜놔)
초조한데 왜 이렇게 신나 신나
말해줘 우리 뭐야 뭐야

[Bridge]
딱 한 번만 용기 내서
물어볼까 말까 말까
타이핑 지웠다 썼다
에라 모르겠다 전송

[Chorus]
우리 사이 뭐야 뭐야 뭐야 (뭐야)
친구도 아니고 애인도 아냐 (아냐)
밀당인지 진심인지 몰라 몰라
그래도 좋아 미치겠어 어어어
우리 사이 뭐야 뭐야 뭐야 (뭐야)
답장은 안 와도 알림은 켜놔 (켜놔)
초조한데 왜 이렇게 신나 신나
말해줘 우리 뭐야 뭐야"""},

 {"pos":3,"title":"메인캐릭터 병","title_en":"Main Character Syndrome",
  "genre":"Brazilian baile funk pop","genre_group":"Hip-Hop/Funk",
  "sub":"funk mandelão crossover with ironic self-mocking chant","bpm":130,"key":"F# minor","time_sig":"4/4",
  "trend":"funk mandelão(tamborzão·808·스타카토 chant) / 관종·메인캐릭터 아이러니를 당당한 후렴 속 텅 빈 자아 자기풍자",
  "sp":"Brazilian baile funk crossover pop, funk mandelão / tamborzão flavor. Hard-hitting sub 808 bass and punchy tamborzão drum pattern with syncopated staccato claps and rimshots, driving 130 BPM in F# minor, 4/4. Minimal detuned synth stabs, whistle-hook lead, sparse dark plucks leaving space for rhythm. Confident female vocal, bratty and playful, half-sung half-chanted with call-and-response gang chants and provocative ad-libs. Vocal delivery is punchy, staccato, on-the-beat, sassy and teasing with an ironic wink. Bass-heavy club energy, dancefloor-ready, low-end pressure, hype and viral. Funk carioca groove, favela funk swagger. Chorus is loud and anthemic with chanted hooks; verses rap-adjacent and rhythmic. Modern 2026 baile funk pop production, crisp mix, tight kick, wide stabs.",
  "lyrics":"""[Verse 1]
조명 없어도 스포트라이트 켜
지나가는 길이 다 내 무대야
표정 하나에 세상이 돌아
근데 집에 오면 아무도 없어

[Pre-Chorus]
찍고 지우고 또 찍고
좋아요 하나에 심장 뛰고
다 아는 척 웃지만
사실 나도 나를 몰라

[Chorus]
나야 나 메인캐릭터
세상은 다 내 엑스트라
(당당하게) 고개 들어
(솔직하게) 속은 텅 텅 텅
나야 나 주인공인 척
박수 소리에 숨어 사는 척
웃어 웃어 웃어
아무도 몰라 나만 알아

[Verse 2]
프로필 사진은 완벽한 나
실물은 조금 다르지만 뭐
댓글 하나에 하루가 무너져
근데 또 올려 또 웃어 또

[Pre-Chorus]
필터 뒤에 숨어서
반짝이는 척 연기해
다 부러운 척하지만
사실 내가 제일 부러워

[Chorus]
나야 나 메인캐릭터
세상은 다 내 엑스트라
(당당하게) 고개 들어
(솔직하게) 속은 텅 텅 텅
나야 나 주인공인 척
박수 소리에 숨어 사는 척
웃어 웃어 웃어
아무도 몰라 나만 알아

[Bridge]
불 꺼진 방 화면만 켜져
진짜 나는 여기 있는데
아무도 안 봐도 괜찮아
(거짓말) 괜찮아 (거짓말)

[Chorus]
나야 나 메인캐릭터
세상은 다 내 엑스트라
당당하게 밀어붙여
속은 조금 텅 텅 텅
나야 나 주인공이야
그렇게 믿어야 사니까
웃어 웃어 웃어
나만 알아 나만 알아"""},

 {"pos":4,"title":"새벽 세 시의 피드","title_en":"Feed at 3AM",
  "genre":"UK garage / 2-step pop","genre_group":"Dance/Electronic",
  "sub":"소울풀 2-step 리바이벌, 나른한 야간 그루브","bpm":130,"key":"F# minor","time_sig":"4/4",
  "trend":"2-step revival 셔플 하이햇·따뜻한 서브 / 새벽에 옛 연인 SNS 훔쳐보다 들킬까 조마조마한 감정을 나른한 훅으로",
  "sp":"UK garage, 2-step revival pop, soulful late-night groove. Classic 2-step garage feel: shuffled swung hi-hats, syncopated skippy drums, crisp rimshots, warm rounded sub-bass that bounces on the offbeat. Tempo around 130 BPM, F# minor, 4/4 with a loose swing. Smooth chopped-and-stuttered soul vocals, both a tender male falsetto and a breathy female lead trading lines, pitched-up vocal chops as texture. Lush reverse-reverb swells, dusty Rhodes chords, soft filtered pads, gentle vinyl crackle. Nocturnal, intimate, bittersweet mood. Production is clean and modern yet nostalgic UK garage: tight low end, airy top, tasteful sidechain. Verses hushed and close-miked, pre-chorus lifts, chorus opens into a laid-back but grooving hook with sighing harmonies. Keep it sleek, danceable, and emotional.",
  "lyrics":"""[Verse 1]
새벽 세 시 불 꺼진 방
엄지 끝이 자꾸 미끄러져
지우려 했던 그 이름 위
손가락이 멈춰 서 있어

[Pre-Chorus]
한 칸만 더 내리면 안 되는데
심장이 먼저 화면을 켜

[Chorus]
네 피드를 훔쳐봐 몰래몰래
좋아요는 절대 누르지 마
들킬까 봐 숨을 참아
그루브에 몸을 숨겨
나른하게 흔들려도
마음은 조마조마해

[Verse 2]
새 프로필 사진 웃는 너
옆에 누군진 확대 안 할래
스토리 끝까지 다 봤는데
조회 목록에 내 이름 뜰까

[Pre-Chorus]
손 떨려 창을 얼른 닫아도
다시 켜는 건 나야 또 나야

[Chorus]
네 피드를 훔쳐봐 몰래몰래
좋아요는 절대 누르지 마
들킬까 봐 숨을 참아
그루브에 몸을 숨겨
나른하게 흔들려도
마음은 조마조마해

[Bridge]
이 밤이 지나면 괜찮아질까
스크롤은 멈추질 않아
베이스가 낮게 나를 감싸
그냥 이대로 흔들릴래

[Chorus]
네 피드를 훔쳐봐 몰래몰래
좋아요는 절대 누르지 마
들킬까 봐 숨을 참아
그루브에 몸을 숨겨
나른하게 흔들려도
마음은 조마조마해

[Outro]
화면을 끄고 눈을 감아
새벽만 아는 내 비밀"""},

 {"pos":5,"title":"필터 없는 나","title_en":"No Filter Me",
  "genre":"warm hyperpop","genre_group":"Pop/Hyperpop",
  "sub":"cooled-down digicore, lo-fi warm pop with pitched vocals","bpm":150,"key":"F# minor","time_sig":"4/4",
  "trend":"식은 하이퍼팝(피치업이지만 멜로디컬·로파이 온기) / 보정·가면에 지쳐 날것의 나로 살고픈 AI시대 진정성 갈망을 해방감 후렴으로",
  "sp":"Warm cooled-down hyperpop, a gentle digicore ballad where the harsh edges have melted away. Melodic pitched-up vocals (gender-neutral pitch-shift, soft and intimate, close-mic bedroom delivery, not screamed) float over lo-fi warmth. Soft rounded synth pads, glassy bell plucks, light saturated distortion on the edges only. Bouncy round 808 bass, crisp finger-snap and clap percussion, tape hiss and vinyl crackle for cozy warmth. Half-time feel at 150 BPM, key of F# minor, 4/4. Bittersweet verses turning euphoric and wide-open on the chorus, big cathartic release, sidechained shimmer, airy reverb tails. Emotional autotune used as texture not correction. Genre: warm hyperpop, cooldown digicore, lo-fi bedroom pop, melodic hyperpop, glowcore. Intimate, tender, hopeful, liberating. Human breaths kept in, imperfect and real, heartfelt.",
  "lyrics":"""[Verse 1]
화면 속 나는 웃고 있는데
진짜 표정은 어디 갔지
필터 한 겹 벗기면 무서워
근데 그게 나야, 그게 나야

[Pre-Chorus]
보정된 하늘 말고
금 간 진짜 내 목소리로
숨 한 번 크게 들이쉬고

[Chorus]
필터 없는 나로 살래
떨려도 이게 진짜야
픽셀 뒤에 숨지 않을래
날것 그대로 빛날래
오 오 오, 가면을 벗어
오 오 오, 숨이 트여

[Verse 2]
완벽한 척 지친 하루 끝에
지운 사진들이 쌓여가
AI가 대신 웃어주는 시대
그래도 난 나이고 싶어

[Pre-Chorus]
다듬어진 말 말고
갈라진 진짜 내 마음으로
한 걸음 더 나아갈게

[Chorus]
필터 없는 나로 살래
떨려도 이게 진짜야
픽셀 뒤에 숨지 않을래
날것 그대로 빛날래
오 오 오, 가면을 벗어
오 오 오, 숨이 트여

[Bridge]
못난 부분까지 다 안아줘
지워지지 않는 흉터도 나야
로딩 없이, 그냥 이대로
처음으로 나를 사랑해

[Chorus]
필터 없는 나로 살래
떨려도 이게 진짜야
픽셀 뒤에 숨지 않을래
날것 그대로 빛날래
오 오 오, 가면을 벗어
오 오 오, 숨이 트여"""},

 {"pos":6,"title":"흙 밟으러 갈래","title_en":"Gonna Go Touch Grass",
  "genre":"modern country-pop","genre_group":"Country/Roots",
  "sub":"어쿠스틱 루츠 감성의 컨트리-팝 크로스오버, 싱어롱 해방가","bpm":100,"key":"G major","time_sig":"4/4",
  "trend":"2024~26 컨트리 붐(밴조·슬라이드·스톰프클랩) / touch grass·디지털 디톡스, 도시·온라인 떠나 흙 밟는 해방적 후렴",
  "sp":"A modern country-pop crossover, warm and radiant, built for a wide-open singalong. Think 2024-2026 country boom: bright acoustic guitar strumming up front, rolling banjo licks, a touch of slide guitar bending in the background, and a driving stomp-clap groove that grounds the whole track. Contemporary pop production polishes it — clean punchy drums, a fat kick, subtle synth pads, and a big layered gang-vocal chorus. Roots-pop with a radio sheen. Tempo around 100 BPM, key of G major, 4/4. A warm, emotive male lead vocal, slightly raspy and earnest, delivered close and conversational in the verses, then opening up wide and anthemic in the chorus with soaring harmonies. Dynamic build from an intimate verse into a liberating, hands-in-the-air chorus. Handclaps, foot stomps, and a joyful, freeing, breathe-out-and-run feeling throughout. Uplifting modern country, singalong hook, festival-ready.",
  "lyrics":"""[Verse 1]
화면 불빛에 밤을 다 태웠어
알림 소리에 심장이 뛰던 날
손끝은 차갑고 눈은 시린데
창밖 저 들판은 초록으로 번져

[Pre-Chorus]
신발 끈을 묶고 문을 열어
와이파이 없는 곳으로 가

[Chorus]
흙 밟으러 갈래, 맨발로 달려
젖은 풀냄새에 숨을 크게 쉬어
로그아웃, 이 도시 뒤로하고
탁 트인 저 하늘 아래 나를 던져
오, 흙 밟으러 갈래 (갈래)
오, 나 살러 갈래 (갈래)

[Verse 2]
좋아요 숫자로 날 재던 세상
오늘은 강물에 발을 담가
밴조 소리처럼 마음이 굴러
오래 잊고 산 웃음이 터져

[Pre-Chorus]
전화기 꺼두고 바람을 따라
길이 없는 곳으로 가

[Chorus]
흙 밟으러 갈래, 맨발로 달려
젖은 풀냄새에 숨을 크게 쉬어
로그아웃, 이 도시 뒤로하고
탁 트인 저 하늘 아래 나를 던져
오, 흙 밟으러 갈래 (갈래)
오, 나 살러 갈래 (갈래)

[Bridge]
박수 소리, 발 구르는 소리
다 같이 목청껏 불러 봐
화면 밖에도 세상은 있어
여기, 지금, 진짜 여기

[Chorus]
흙 밟으러 갈래, 맨발로 달려
젖은 풀냄새에 숨을 크게 쉬어
로그아웃, 이 도시 뒤로하고
탁 트인 저 하늘 아래 나를 던져
오, 흙 밟으러 갈래 (갈래)
오, 나 살러 갈래 (갈래)"""},

 {"pos":7,"title":"읽씹 새벽 세시","title_en":"Left On Read, 3AM",
  "genre":"K-R&B, alt-R&B trap-soul","genre_group":"R&B/Soul",
  "sub":"하프타임 트랩 슬로우잼, 야간 미련의 slow jam","bpm":74,"key":"F# minor","time_sig":"4/4",
  "trend":"트랩 하이햇롤+808 서브 K-R&B slow jam / 읽씹·늦은 밤 답장 없는 미련을 애절하고 그루비한 후렴으로",
  "sp":"A moody K-R&B / alt-R&B trap-soul slow jam, nocturnal and soulful. Half-time trap groove at 74 BPM in F# minor, 4/4. Deep, heavy 808 sub-bass with soft rounded glides, crisp rattling trap hi-hat rolls and stuttered triplet hats, sparse rim-click snare landing lazily on the backbeat. Warm Rhodes electric piano chords, airy pad keys, and spacey plate reverb drifting through the mix. Late-night, intimate, bedroom-R&B atmosphere with a hazy blue tone. A tender male vocal in soft falsetto, breathy and close-mic'd, delivered smooth and conversational with delicate melodic runs and layered background harmonies. Emotional, yearning, and vulnerable. The chorus opens up groovy and aching, hook-driven and memorable, with a wide reverberant vocal stack over the sliding 808. Subtle vinyl crackle and finger-snap textures. Slow, swaying, hypnotic trap-soul with lush low-end and dreamy space. Modern 2026 K-R&B production, polished yet raw and heartfelt.",
  "lyrics":"""[Verse 1]
새벽 세시 화면만 밝아
읽음 표시 하나에 멈춰 선 나
보낸 말은 저 위에 떠 있고
답장 칸은 여전히 비어 있어

[Pre-Chorus]
타이핑 세 점이 떴다 사라져
괜히 심장이 다시 내려앉아

[Chorus]
읽씹 당한 이 밤이 길어
답장 없는 네 이름을 붙들고
서성이다 새벽이 와도
난 아직 여기 이 자리에 서 있어
오늘도 읽고 지나쳐도
나는 또 너를 못 지워

[Verse 2]
마지막 온점 하나가 아파
무심한 그 침묵이 날 삼켜
스크롤 올려 우리를 읽다가
또 웃다가 눈물이 번져

[Pre-Chorus]
지웠다 다시 쓰는 이 문장
보낼 용기가 자꾸 무너져

[Chorus]
읽씹 당한 이 밤이 길어
답장 없는 네 이름을 붙들고
서성이다 새벽이 와도
난 아직 여기 이 자리에 서 있어
오늘도 읽고 지나쳐도
나는 또 너를 못 지워

[Bridge]
딱 한 글자만 남겨줘
잘 지내냐는 그 말이라도
이 새벽 끝에 걸린 나를
제발 한 번만 붙잡아줘

[Chorus]
읽씹 당한 이 밤이 길어
답장 없는 네 이름을 붙들고
서성이다 새벽이 와도
난 아직 여기 이 자리에 서 있어
오늘도 읽고 지나쳐도
나는 또 너를 못 지워

[Outro]
화면은 어두워지고
난 아직 읽씹된 채 멈춰 있어"""},

 {"pos":8,"title":"나를 위한 파티","title_en":"Party For Myself",
  "genre":"Reggaeton","genre_group":"Latin",
  "sub":"Latin-pop crossover reggaeton, summer party anthem","bpm":95,"key":"F# minor","time_sig":"4/4",
  "trend":"2026 레게톤/라틴팝 크로스오버(dembow·브라스 스탭) / 이별·번아웃 후 자기애 회복을 나를 위한 파티 선언으로",
  "sp":"A bright, confident reggaeton track, Latin-pop crossover, modern 2026 summer party anthem. Reggaeton at its core: punchy dembow rhythm, syncopated kick-and-snare groove, deep round bass. Latin-pop reggaeton crossover with glossy synth plucks, bright staccato brass stabs, shimmering plucked arpeggios, and airy percussion shakers. Female lead vocal, confident and playful delivery, sassy and self-assured, with catchy melodic hooks and a couple of short Spanish ad-libs (vamos, dale) shouted in the chorus. Tempo around 95 BPM, key F# minor, 4/4. Verses feel flirty and cool over a spacious dembow groove; pre-chorus builds tension with rising synths; chorus explodes with full brass stabs, thick bass, layered vocal harmonies and party energy. Feel-good, sun-soaked, danceable, radio-ready urbano-pop. Clean punchy mix, tight low end, festival club vibe.",
  "lyrics":"""[Verse 1]
거울 앞에 서서 웃어봐
어제까진 울던 얼굴에
오늘은 립스틱을 발라
나 이제 나를 데리러 왔어

[Pre-Chorus]
무너진 밤은 뒤로 던져
번아웃 다 태워버려
비트가 심장을 깨워
올라가 더 크게, vamos

[Chorus]
오늘 밤은 나를 위한 파티
dale, 나 혼자여도 빛나지
손 들어 나를 사랑해, 사랑해
다시 뜨겁게 타올라 baby
오늘 밤은 나를 위한 파티
vamos, 내 이름을 불러줘 크게
흔들어 나를 사랑해, 사랑해
이 밤의 주인공은 나야

[Verse 2]
네가 없어도 난 완벽해
상처는 별처럼 반짝여
스텝을 밟아 흔들려
이 리듬이 날 안아줘

[Pre-Chorus]
미련은 창밖에 흘려
새로운 나로 갈아입어
비트가 심장을 깨워
올라가 더 크게, vamos

[Chorus]
오늘 밤은 나를 위한 파티
dale, 나 혼자여도 빛나지
손 들어 나를 사랑해, 사랑해
다시 뜨겁게 타올라 baby
오늘 밤은 나를 위한 파티
vamos, 내 이름을 불러줘 크게
흔들어 나를 사랑해, 사랑해
이 밤의 주인공은 나야

[Bridge]
무너져도 괜찮아
나는 나를 일으켜
이 도시가 다 알아
내가 나를 선택해

[Chorus]
오늘 밤은 나를 위한 파티
dale, 나 혼자여도 빛나지
손 들어 나를 사랑해, 사랑해
다시 뜨겁게 타올라 baby
오늘 밤은 나를 위한 파티
vamos, 내 이름을 불러줘 크게
흔들어 나를 사랑해, 사랑해
이 밤의 주인공은 나야"""},

 {"pos":9,"title":"좋아요 하나에 서사 완성","title_en":"A Whole Story From One Like",
  "genre":"indie bedroom pop","genre_group":"Indie/Bedroom",
  "sub":"lo-fi sad-girl bedroom pop with hazy dream-pop haze","bpm":92,"key":"F# minor","time_sig":"4/4",
  "trend":"sad-girl bedroom pop(뮤트기타·로파이 온기·헤이지 리버브) / 딜루루 짝사랑 망상을 몽롱·달콤씁쓸 자조로",
  "sp":"Intimate lo-fi indie bedroom pop, sad-girl bedroom pop, hazy dream-pop. Female vocal, breathy and airy, close-mic whisper-singing right against the ear, soft and vulnerable, with gentle doubled harmonies drifting in the reverb. Warm lo-fi production, tape hiss and vinyl crackle, cozy intimate room sound. Muted clean electric guitar, palm-muted with soft chorus and long hazy reverb tails, mellow and blurry. Soft mellow drum machine, laid-back boom-bap groove with brushed low-velocity snare and rounded kick, unhurried and dreamy. Warm round sustained bass, muffled dusty synth pads washing underneath, faint bell-like Rhodes twinkles. Melancholic, wistful, bittersweet mood, delicate and drowsy. Slow to mid tempo around 92 BPM, F# minor, 4/4. Verses hushed and confessional; chorus opens into a soft airy hook with layered breathy harmonies, still cozy and low-key. Modern 2026 sad-girl indie, understated, nostalgic, tender lo-fi warmth.",
  "lyrics":"""[Verse 1]
새벽 두 시 반 또 켜버린 화면
네가 누른 좋아요 하나
그거 하나에 나는 벌써
결혼식 하객까지 다 불렀어

[Pre-Chorus]
아무 의미 없단 거 알아
근데 알면서도 자꾸
혼자 소설을 써 내려가
주인공은 너와 나

[Chorus]
딜루루 딜루루 나 좀 이상해
좋아요 하나로 우주를 만들어
너의 프사 배경까지 나를 향한 신호래
몽롱하게 달콤하게 나 혼자 사랑해
딜루루 딜루루 웃기지 그치
그래도 오늘 밤은 이대로 둘래

[Verse 2]
스토리에 뜬 노래 가사가
왠지 나한테 하는 말 같아
0.5초 본 걸 들킬까 봐
손끝만 괜히 떨려와

[Pre-Chorus]
친구들은 말리지 정신 차리라고
근데 이 착각이 좋은걸
달콤한 거짓말 속에서
조금만 더 살래

[Chorus]
딜루루 딜루루 나 좀 이상해
좋아요 하나로 우주를 만들어
너의 프사 배경까지 나를 향한 신호래
몽롱하게 달콤하게 나 혼자 사랑해
딜루루 딜루루 웃기지 그치
그래도 오늘 밤은 이대로 둘래

[Bridge]
내일이면 부끄러워 이불을 차겠지
그래도 지금 이 밤엔
네가 나를 좋아한다고
딱 한 번만 믿어볼래

[Chorus]
딜루루 딜루루 나 좀 이상해
좋아요 하나로 우주를 만들어
너의 프사 배경까지 나를 향한 신호래
몽롱하게 달콤하게 나 혼자 사랑해
딜루루 딜루루 웃기지 그치
그래도 오늘 밤은 이대로 둘래

[Outro]
좋아요 하나에 또 하루를 살아
바보 같지 나도 알아"""},

 {"pos":10,"title":"다시 뛰는 심장","title_en":"Heartbeat Again",
  "genre":"liquid drum & bass pop","genre_group":"Dance/Electronic",
  "sub":"소울풀 여성 보컬 리퀴드 DnB 팝, 따뜻한 피아노 브레이크비트","bpm":170,"key":"F# minor","time_sig":"4/4",
  "trend":"2025~26 리퀴드 DnB 팝 부흥(롤링 리스·따뜻한 피아노·소울풀 청) / 번아웃 회복→질주 서사를 상승감 후렴으로",
  "sp":"Liquid drum and bass pop, a warm and emotional liquid DnB anthem at 170 BPM in F# minor, 4/4. Rolling, syncopated breakbeat drums with crisp snares and shuffling hi-hats drive relentless forward momentum, layered over a deep, smooth Reese bassline that rolls and glides in the low end. Lush, warm piano chords ring out with spacious hall reverb, soft pads and shimmering atmospheric textures fill the stereo field. This is liquid drum and bass, soulful and uplifting, cinematic yet dancefloor-ready. A female vocal leads: soulful, warm, breathy in the verses and soaring with powerful belted runs in the chorus, full of longing that blooms into hope. Emotional but racing energy, that classic liquid DnB sound. Sidechained bass, ethereal reverb tails, gentle vocal chops as texture. Modern 2026 liquid drum and bass pop revival, euphoric drop, driving rolling groove, bright and hopeful lift into the chorus.",
  "lyrics":"""[Verse 1]
숨이 턱까지 차서 멈춰 섰던 밤
텅 빈 방 안에 나 혼자 남아
다 타버린 재 같던 나의 하루들
더는 못 뛰겠다 그렇게 접었어

[Pre-Chorus]
근데 작은 불씨 하나
가슴 깊은 곳에서 다시
툭툭 두드려 나를 깨워

[Chorus]
다시 뛰어 내 심장아 크게
멈췄던 그 자리 박차고 나가
소진된 줄 알았던 나의 숨이
다시 달려 바람을 가르고
벅차올라 이 밤을 넘어서
끝난 게 아니야 이제 시작이야

[Verse 2]
넘어진 무릎에 다시 힘을 주고
식어버린 두 발에 온기를 담아
느려도 괜찮아 멈추지만 않으면
한 걸음 또 한 걸음 나를 믿어

[Pre-Chorus]
이제 작은 불씨 하나
온몸을 태우는 불꽃으로
번져 나를 다시 세워

[Chorus]
다시 뛰어 내 심장아 크게
멈췄던 그 자리 박차고 나가
소진된 줄 알았던 나의 숨이
다시 달려 바람을 가르고
벅차올라 이 밤을 넘어서
끝난 게 아니야 이제 시작이야

[Bridge]
지쳐 쓰러진 밤도
나를 만든 조각이야
이 상처 위에 딛고
더 멀리 더 높이

[Chorus]
다시 뛰어 내 심장아 크게
멈췄던 그 자리 박차고 나가
소진된 줄 알았던 나의 숨이
다시 달려 바람을 가르고
벅차올라 이 밤을 넘어서
끝난 게 아니야 이제 시작이야

[Outro]
다시 달려 다시 뛰어
이제 시작이야"""},
]

# --- validate SP length (<=1000) ---
over=[s for s in SONGS if len(s["sp"])>1000]
for s in SONGS:
    print(f"  {BATCH}-{s['pos']:<2} {s['genre_group']:<16} {s['title']:<20} {s['key']:<9} {s['bpm']}BPM  SP={len(s['sp'])} LYR={len(s['lyrics'])}{'  OVER!' if len(s['sp'])>1000 else ''}")
assert not over, f"SP over 1000: {[s['pos'] for s in over]}"
assert len({s['pos'] for s in SONGS})==10, "pos not unique/10"
print(f"SP gate: ALL {len(SONGS)} PASS (<=1000)")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

# --- DB insert gid 30161-30170 ---
conf={}
for ln in open(os.path.expanduser('~/.config/leofamily_music/db_sunolanguage.conf')):
    ln=ln.strip()
    if '=' in ln and not ln.startswith('#'):
        k,v=ln.split('=',1); conf[k.strip()]=v.strip()
c=psycopg2.connect(host=conf['DB_HOST'],port=conf.get('DB_PORT',5432),dbname=conf['DB_NAME'],user=conf['DB_USER'],password=conf.get('DB_PASSWORD',''))
cur=c.cursor()
cur.execute(f"SELECT COUNT(*) FROM songs WHERE global_id BETWEEN {GID0+1} AND {GID0+len(SONGS)};")
assert cur.fetchone()[0]==0, "gid range not free!"
gids=[]
for s in SONGS:
    gid=GID0+s["pos"]
    cur.execute("""INSERT INTO songs
      (global_id, source_project, batch, creator, status, title, lyrics,
       style_prompt, genre, genre_group, subgenre, bpm, key_signature, theme,
       album_title, album_concept, lyrics_language, char_count)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING global_id""",
      (gid,'sunolanguage',BATCH,'sunolanguage','pending_suno', s["title"], s["lyrics"],
       s["sp"], s["genre"], s["genre_group"], s["sub"], s["bpm"], s["key"], THEME,
       ALBUM, s["trend"], 'ko', len(s["sp"])))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED songs gid:", gids)
cur.execute(f"SELECT global_id,title,genre,bpm,key_signature,status,(lyrics IS NOT NULL) has_lyr FROM songs WHERE batch='{BATCH}' ORDER BY global_id;")
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

# --- batch JSON ---
os.makedirs('data/trend', exist_ok=True)
batch={"batch":BATCH,"album":ALBUM,"line":"sunolanguage","theme":THEME,
 "created":"2026-07-21","gid_range":f"{GID0+1}~{GID0+len(SONGS)}",
 "origin":"LEO 직지시(kee 경유 07-21): 발주 시점 최신 음악 트렌드를 가사·장르 모두 반영. 완전 자율(무옵션) 진행. 동일 발주 5라인 병렬.",
 "design_note":"앨범 '로그오프(Log Off)' — 2026 글로벌 사운드 10종(Afro-house/Jersey club/Baile funk/UK garage 2-step/warm hyperpop/country-pop/K-R&B trap-soul/Reggaeton/bedroom pop/liquid DnB) × 온라인 세대 감정(도파민 소진·시추에이션십·메인캐릭터 아이러니·전연인 피드·무필터 진정성·touch grass·읽씹 미련·자기애 회복·딜루루·번아웃 회복). 전곡 한국어 가사 보컬.",
 "self_review":"F# minor 9/10 클러스터링(서브에이전트 독립 기본값) — SP↔DB key 정합 유지 위해 보정 안 함, 차기 배치 key 다양성 지시 필요. country-pop만 G major.",
 "songs":[{"gid":GID0+s["pos"],"id":f"{BATCH}-{s['pos']}","title":s["title"],"title_en":s["title_en"],
   "genre":s["genre"],"genre_group":s["genre_group"],"subgenre":s["sub"],
   "is_instrumental":False,"bpm":s["bpm"],"key":s["key"],"time_sig":s["time_sig"],
   "trend_note":s["trend"],"style_prompt":s["sp"],"sp_length":len(s["sp"]),"lyrics":s["lyrics"]} for s in SONGS]}
json.dump(batch, open('data/trend/TREND01_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/trend/TREND01_batch.json")
