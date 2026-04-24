#!/bin/bash
set -e
OUT=data/upload_batch_wave1
TMPDIR=data/upload_batch_wave1/tmp
mkdir -p $TMPDIR

# 20001 사랑인가 봐 (TROT)
curl -sL "https://cdn1.suno.ai/8fc676d6-737f-4d10-891d-632ee817bd03.mp3" -o "$TMPDIR/20001_사랑인가_봐_full.mp3"
ffmpeg -y -i "$TMPDIR/20001_사랑인가_봐_full.mp3" -t 60 -c copy "$OUT/20001_사랑인가_봐.mp3" 2>/dev/null

# 20002 놀아보자 (TROT)
curl -sL "https://cdn1.suno.ai/104ff554-d671-44f6-8fbc-f13303083279.mp3" -o "$TMPDIR/20002_놀아보자_full.mp3"
ffmpeg -y -i "$TMPDIR/20002_놀아보자_full.mp3" -t 60 -c copy "$OUT/20002_놀아보자.mp3" 2>/dev/null

# 20003 다시 만났네 (TROT)
curl -sL "https://cdn1.suno.ai/d4e2cf16-6b6f-4e31-84e4-a0406cf483a6.mp3" -o "$TMPDIR/20003_다시_만났네_full.mp3"
ffmpeg -y -i "$TMPDIR/20003_다시_만났네_full.mp3" -t 60 -c copy "$OUT/20003_다시_만났네.mp3" 2>/dev/null

# 20004 살 만해요 (TROT)
curl -sL "https://cdn1.suno.ai/a9de55d1-2850-4d45-bebd-2e60810363a9.mp3" -o "$TMPDIR/20004_살_만해요_full.mp3"
ffmpeg -y -i "$TMPDIR/20004_살_만해요_full.mp3" -t 60 -c copy "$OUT/20004_살_만해요.mp3" 2>/dev/null

# 20005 정이라는 게 (TROT)
curl -sL "https://cdn1.suno.ai/ab447137-5616-4567-9e2f-4d9badb23e6e.mp3" -o "$TMPDIR/20005_정이라는_게_full.mp3"
ffmpeg -y -i "$TMPDIR/20005_정이라는_게_full.mp3" -t 60 -c copy "$OUT/20005_정이라는_게.mp3" 2>/dev/null

# 20006 미련이야 (TROT)
curl -sL "https://cdn1.suno.ai/8f4be928-5375-4122-845a-3d039e2620f8.mp3" -o "$TMPDIR/20006_미련이야_full.mp3"
ffmpeg -y -i "$TMPDIR/20006_미련이야_full.mp3" -t 60 -c copy "$OUT/20006_미련이야.mp3" 2>/dev/null

# 20007 보고 싶다 (TROT)
curl -sL "https://cdn1.suno.ai/67f1b3d6-ece7-4a6d-b3c5-0424c3458b8c.mp3" -o "$TMPDIR/20007_보고_싶다_full.mp3"
ffmpeg -y -i "$TMPDIR/20007_보고_싶다_full.mp3" -t 60 -c copy "$OUT/20007_보고_싶다.mp3" 2>/dev/null

# 20008 어머니 (TROT)
curl -sL "https://cdn1.suno.ai/8cba524f-1560-4824-8066-fd5f8df756ac.mp3" -o "$TMPDIR/20008_어머니_full.mp3"
ffmpeg -y -i "$TMPDIR/20008_어머니_full.mp3" -t 60 -c copy "$OUT/20008_어머니.mp3" 2>/dev/null

# 20009 건배 (TROT)
curl -sL "https://cdn1.suno.ai/ada926f5-e1d8-4f95-99e1-dd09c55655bd.mp3" -o "$TMPDIR/20009_건배_full.mp3"
ffmpeg -y -i "$TMPDIR/20009_건배_full.mp3" -t 60 -c copy "$OUT/20009_건배.mp3" 2>/dev/null

# 20010 고향이 그립습니다 (TROT)
curl -sL "https://cdn1.suno.ai/f0ef6d21-b04d-444a-8cfa-e4294438cf9c.mp3" -o "$TMPDIR/20010_고향이_그립습니다_full.mp3"
ffmpeg -y -i "$TMPDIR/20010_고향이_그립습니다_full.mp3" -t 60 -c copy "$OUT/20010_고향이_그립습니다.mp3" 2>/dev/null

# 20011 읽씹하지 마 (TROT)
curl -sL "https://cdn1.suno.ai/7694e9ca-c27c-4655-b87a-35bfc90bc3c9.mp3" -o "$TMPDIR/20011_읽씹하지_마_full.mp3"
ffmpeg -y -i "$TMPDIR/20011_읽씹하지_마_full.mp3" -t 60 -c copy "$OUT/20011_읽씹하지_마.mp3" 2>/dev/null

# 20012 자유다 (TROT)
curl -sL "https://cdn1.suno.ai/6d0015fd-891d-4964-9ae1-972d60458fff.mp3" -o "$TMPDIR/20012_자유다_full.mp3"
ffmpeg -y -i "$TMPDIR/20012_자유다_full.mp3" -t 60 -c copy "$OUT/20012_자유다.mp3" 2>/dev/null

# 1024 완행열차 마지막 칸 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/3235b0f0-8505-4d16-ae65-5d5caffd9638.mp3" -o "$TMPDIR/1024_완행열차_마지막_칸_full.mp3"
ffmpeg -y -i "$TMPDIR/1024_완행열차_마지막_칸_full.mp3" -t 60 -c copy "$OUT/1024_완행열차_마지막_칸.mp3" 2>/dev/null

# 1067 새벽 다섯 시 플랫폼 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/13548a24-1b9c-49f1-a968-ed81e0ca96d4.mp3" -o "$TMPDIR/1067_새벽_다섯_시_플랫폼_full.mp3"
ffmpeg -y -i "$TMPDIR/1067_새벽_다섯_시_플랫폼_full.mp3" -t 60 -c copy "$OUT/1067_새벽_다섯_시_플랫폼.mp3" 2>/dev/null

# 1183 창가 자리 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/0bea37ff-973a-4617-beeb-6adc38f2096f.mp3" -o "$TMPDIR/1183_창가_자리_full.mp3"
ffmpeg -y -i "$TMPDIR/1183_창가_자리_full.mp3" -t 60 -c copy "$OUT/1183_창가_자리.mp3" 2>/dev/null

# 1399 돌길 끝 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/1a6e8d1e-f57f-4acb-8d89-ab608cb78ca2.mp3" -o "$TMPDIR/1399_돌길_끝_full.mp3"
ffmpeg -y -i "$TMPDIR/1399_돌길_끝_full.mp3" -t 60 -c copy "$OUT/1399_돌길_끝.mp3" 2>/dev/null

# 1513 여수행 버스는 새벽 다섯 시 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/290777b0-9d7e-4517-b515-e9a809770c46.mp3" -o "$TMPDIR/1513_여수행_버스는_새벽_다섯_시_full.mp3"
ffmpeg -y -i "$TMPDIR/1513_여수행_버스는_새벽_다섯_시_full.mp3" -t 60 -c copy "$OUT/1513_여수행_버스는_새벽_다섯_시.mp3" 2>/dev/null

# 1544 경유지 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/bac9ddd3-4613-4387-adc6-8a1306204434.mp3" -o "$TMPDIR/1544_경유지_full.mp3"
ffmpeg -y -i "$TMPDIR/1544_경유지_full.mp3" -t 60 -c copy "$OUT/1544_경유지.mp3" 2>/dev/null

# 1571 서른두 번째 도장 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/d00ff53b-05bb-4ceb-9e03-d3c0707fb640.mp3" -o "$TMPDIR/1571_서른두_번째_도장_full.mp3"
ffmpeg -y -i "$TMPDIR/1571_서른두_번째_도장_full.mp3" -t 60 -c copy "$OUT/1571_서른두_번째_도장.mp3" 2>/dev/null

# 1612 여섯 번째 수저 (Bossa Nova)
curl -sL "https://cdn1.suno.ai/c400ac23-b43a-4a58-b01c-31616710468c.mp3" -o "$TMPDIR/1612_여섯_번째_수저_full.mp3"
ffmpeg -y -i "$TMPDIR/1612_여섯_번째_수저_full.mp3" -t 60 -c copy "$OUT/1612_여섯_번째_수저.mp3" 2>/dev/null

# 1066 제출 버튼 (Neo-Soul)
curl -sL "https://cdn1.suno.ai/28a72449-d731-4daf-8a5f-d6837c2f2381.mp3" -o "$TMPDIR/1066_제출_버튼_full.mp3"
ffmpeg -y -i "$TMPDIR/1066_제출_버튼_full.mp3" -t 60 -c copy "$OUT/1066_제출_버튼.mp3" 2>/dev/null

# 1433 거울 속 아버지 (Neo-Soul)
curl -sL "https://cdn1.suno.ai/6c42b296-6ce8-4986-9081-a43bdda01243.mp3" -o "$TMPDIR/1433_거울_속_아버지_full.mp3"
ffmpeg -y -i "$TMPDIR/1433_거울_속_아버지_full.mp3" -t 60 -c copy "$OUT/1433_거울_속_아버지.mp3" 2>/dev/null

# 1453 아직 1이에요 (Neo-Soul)
curl -sL "https://cdn1.suno.ai/3f133466-d403-4ea5-ad3d-acba32309318.mp3" -o "$TMPDIR/1453_아직_1이에요_full.mp3"
ffmpeg -y -i "$TMPDIR/1453_아직_1이에요_full.mp3" -t 60 -c copy "$OUT/1453_아직_1이에요.mp3" 2>/dev/null

# 1491 아직 거기 있어? (Neo-Soul)
curl -sL "https://cdn1.suno.ai/276a45d2-5061-4c74-a302-487e0753dae5.mp3" -o "$TMPDIR/1491_아직_거기_있어?_full.mp3"
ffmpeg -y -i "$TMPDIR/1491_아직_거기_있어?_full.mp3" -t 60 -c copy "$OUT/1491_아직_거기_있어?.mp3" 2>/dev/null

# 1725 같은 책이었다 (Neo-Soul)
curl -sL "https://cdn1.suno.ai/7ab08c5c-c9c1-48bc-bb78-a0163eefc19d.mp3" -o "$TMPDIR/1725_같은_책이었다_full.mp3"
ffmpeg -y -i "$TMPDIR/1725_같은_책이었다_full.mp3" -t 60 -c copy "$OUT/1725_같은_책이었다.mp3" 2>/dev/null

# 910 법정의 마침표 (K-POP)
curl -sL "https://cdn1.suno.ai/7217e438-732e-4ee8-b7c5-2e9af3216fd6.mp3" -o "$TMPDIR/910_법정의_마침표_full.mp3"
ffmpeg -y -i "$TMPDIR/910_법정의_마침표_full.mp3" -t 60 -c copy "$OUT/910_법정의_마침표.mp3" 2>/dev/null

# 920 결혼 소식 (K-POP)
curl -sL "https://cdn1.suno.ai/4d05b8f2-78a1-4331-a169-57a711bac659.mp3" -o "$TMPDIR/920_결혼_소식_full.mp3"
ffmpeg -y -i "$TMPDIR/920_결혼_소식_full.mp3" -t 60 -c copy "$OUT/920_결혼_소식.mp3" 2>/dev/null

# 930 약한 밤의 용기 (K-POP)
curl -sL "https://cdn1.suno.ai/740bc049-ed78-4a88-b8cc-cb2457fd5c09.mp3" -o "$TMPDIR/930_약한_밤의_용기_full.mp3"
ffmpeg -y -i "$TMPDIR/930_약한_밤의_용기_full.mp3" -t 60 -c copy "$OUT/930_약한_밤의_용기.mp3" 2>/dev/null

# 940 간호의 사랑 (K-POP)
curl -sL "https://cdn1.suno.ai/10b4aced-fef3-4df9-98ec-ffdf78a4c3a8.mp3" -o "$TMPDIR/940_간호의_사랑_full.mp3"
ffmpeg -y -i "$TMPDIR/940_간호의_사랑_full.mp3" -t 60 -c copy "$OUT/940_간호의_사랑.mp3" 2>/dev/null

# 960 우리만의 언어 (K-POP)
curl -sL "https://cdn1.suno.ai/8ff67487-7a33-4cbb-ba92-f8aa4afae7db.mp3" -o "$TMPDIR/960_우리만의_언어_full.mp3"
ffmpeg -y -i "$TMPDIR/960_우리만의_언어_full.mp3" -t 60 -c copy "$OUT/960_우리만의_언어.mp3" 2>/dev/null

# 10464 Horizon Step (Cinematic)
curl -sL "https://cdn1.suno.ai/af626d71-d820-48dc-a820-f6570d65c47b.mp3" -o "$TMPDIR/10464_Horizon_Step_full.mp3"
ffmpeg -y -i "$TMPDIR/10464_Horizon_Step_full.mp3" -t 60 -c copy "$OUT/10464_Horizon_Step.mp3" 2>/dev/null

# 10469 Crack of Light (Cinematic)
curl -sL "https://cdn1.suno.ai/cc062635-7ada-4f70-8add-44bcbc9210b7.mp3" -o "$TMPDIR/10469_Crack_of_Light_full.mp3"
ffmpeg -y -i "$TMPDIR/10469_Crack_of_Light_full.mp3" -t 60 -c copy "$OUT/10469_Crack_of_Light.mp3" 2>/dev/null

# 10466 Hallway Hold (Cinematic Emotional)
curl -sL "https://cdn1.suno.ai/fbaf54a1-2310-4014-b800-8aa02d668406.mp3" -o "$TMPDIR/10466_Hallway_Hold_full.mp3"
ffmpeg -y -i "$TMPDIR/10466_Hallway_Hold_full.mp3" -t 60 -c copy "$OUT/10466_Hallway_Hold.mp3" 2>/dev/null

# 10472 Closing Frame (Cinematic Emotional)
curl -sL "https://cdn1.suno.ai/714fb48a-8536-4ae6-b21e-a40bb57c4033.mp3" -o "$TMPDIR/10472_Closing_Frame_full.mp3"
ffmpeg -y -i "$TMPDIR/10472_Closing_Frame_full.mp3" -t 60 -c copy "$OUT/10472_Closing_Frame.mp3" 2>/dev/null

# 1107 여행을 못 가는 이유 (Folk Pop)
curl -sL "https://cdn1.suno.ai/907cdc2a-3018-4c27-8b88-1fb082782d97.mp3" -o "$TMPDIR/1107_여행을_못_가는_이유_full.mp3"
ffmpeg -y -i "$TMPDIR/1107_여행을_못_가는_이유_full.mp3" -t 60 -c copy "$OUT/1107_여행을_못_가는_이유.mp3" 2>/dev/null

# 1149 오늘은 그림자만큼만 (Folk Pop)
curl -sL "https://cdn1.suno.ai/53efcd50-94f2-4f83-8b10-e68c4539f8de.mp3" -o "$TMPDIR/1149_오늘은_그림자만큼만_full.mp3"
ffmpeg -y -i "$TMPDIR/1149_오늘은_그림자만큼만_full.mp3" -t 60 -c copy "$OUT/1149_오늘은_그림자만큼만.mp3" 2>/dev/null

# 1389 크림빵 하나 (Folk Pop)
curl -sL "https://cdn1.suno.ai/ade141ed-c5cd-43c8-b320-6b3042d8d0bf.mp3" -o "$TMPDIR/1389_크림빵_하나_full.mp3"
ffmpeg -y -i "$TMPDIR/1389_크림빵_하나_full.mp3" -t 60 -c copy "$OUT/1389_크림빵_하나.mp3" 2>/dev/null

# 1404 닳은 운동화 (Folk Pop)
curl -sL "https://cdn1.suno.ai/6807656b-5050-4288-bd53-91b660110fd5.mp3" -o "$TMPDIR/1404_닳은_운동화_full.mp3"
ffmpeg -y -i "$TMPDIR/1404_닳은_운동화_full.mp3" -t 60 -c copy "$OUT/1404_닳은_운동화.mp3" 2>/dev/null

# 1057 캔버스의 숨소리 (Dream Pop)
curl -sL "https://cdn1.suno.ai/cb63afb5-c223-47c7-9245-ba1e10c3b8e6.mp3" -o "$TMPDIR/1057_캔버스의_숨소리_full.mp3"
ffmpeg -y -i "$TMPDIR/1057_캔버스의_숨소리_full.mp3" -t 60 -c copy "$OUT/1057_캔버스의_숨소리.mp3" 2>/dev/null

# 1102 고양이의 우주 (Dream Pop)
curl -sL "https://cdn1.suno.ai/e0c95114-05a4-4cbf-a6b5-2d9d07e66ab8.mp3" -o "$TMPDIR/1102_고양이의_우주_full.mp3"
ffmpeg -y -i "$TMPDIR/1102_고양이의_우주_full.mp3" -t 60 -c copy "$OUT/1102_고양이의_우주.mp3" 2>/dev/null

# 1160 달리는 갤러리 (Dream Pop)
curl -sL "https://cdn1.suno.ai/1ecccae3-f96b-4bca-9115-422790014a3b.mp3" -o "$TMPDIR/1160_달리는_갤러리_full.mp3"
ffmpeg -y -i "$TMPDIR/1160_달리는_갤러리_full.mp3" -t 60 -c copy "$OUT/1160_달리는_갤러리.mp3" 2>/dev/null

# 1200 구름 창고 (Dream Pop)
curl -sL "https://cdn1.suno.ai/48538781-a850-436c-bff4-8a3e48ca2bbd.mp3" -o "$TMPDIR/1200_구름_창고_full.mp3"
ffmpeg -y -i "$TMPDIR/1200_구름_창고_full.mp3" -t 60 -c copy "$OUT/1200_구름_창고.mp3" 2>/dev/null

# 925 식탁의 노래 (Disco Pop)
curl -sL "https://cdn1.suno.ai/ebaa56a4-63d5-42f6-93c2-5f998958c49f.mp3" -o "$TMPDIR/925_식탁의_노래_full.mp3"
ffmpeg -y -i "$TMPDIR/925_식탁의_노래_full.mp3" -t 60 -c copy "$OUT/925_식탁의_노래.mp3" 2>/dev/null

# 955 너 없이는 (Disco Pop)
curl -sL "https://cdn1.suno.ai/1ef742bd-3618-4191-875b-fd0895629d6f.mp3" -o "$TMPDIR/955_너_없이는_full.mp3"
ffmpeg -y -i "$TMPDIR/955_너_없이는_full.mp3" -t 60 -c copy "$OUT/955_너_없이는.mp3" 2>/dev/null

# 965 벽 위의 그림자 (Disco Pop)
curl -sL "https://cdn1.suno.ai/cae6edf8-5a57-4ffe-96e6-6096517c500c.mp3" -o "$TMPDIR/965_벽_위의_그림자_full.mp3"
ffmpeg -y -i "$TMPDIR/965_벽_위의_그림자_full.mp3" -t 60 -c copy "$OUT/965_벽_위의_그림자.mp3" 2>/dev/null

# 1432 건네는 손 (Piano Ballad)
curl -sL "https://cdn1.suno.ai/6150ade9-40c2-47c1-bf47-320817ac47e9.mp3" -o "$TMPDIR/1432_건네는_손_full.mp3"
ffmpeg -y -i "$TMPDIR/1432_건네는_손_full.mp3" -t 60 -c copy "$OUT/1432_건네는_손.mp3" 2>/dev/null

# 1451 청소부 발소리 (Piano Ballad)
curl -sL "https://cdn1.suno.ai/450f82dc-1e04-46f1-85ab-d744f266dea9.mp3" -o "$TMPDIR/1451_청소부_발소리_full.mp3"
ffmpeg -y -i "$TMPDIR/1451_청소부_발소리_full.mp3" -t 60 -c copy "$OUT/1451_청소부_발소리.mp3" 2>/dev/null

# 10046 빛이 먼저 (Piano Ballad)
curl -sL "https://cdn1.suno.ai/06aa8ec4-c5c5-4176-b2d0-45e3f78cbb79.mp3" -o "$TMPDIR/10046_빛이_먼저_full.mp3"
ffmpeg -y -i "$TMPDIR/10046_빛이_먼저_full.mp3" -t 60 -c copy "$OUT/10046_빛이_먼저.mp3" 2>/dev/null

# 417 공실의 시계 (Indie Acoustic)
curl -sL "https://cdn1.suno.ai/b1c0ba77-ebc1-4747-ab82-cbc1843cace1.mp3" -o "$TMPDIR/417_공실의_시계_full.mp3"
ffmpeg -y -i "$TMPDIR/417_공실의_시계_full.mp3" -t 60 -c copy "$OUT/417_공실의_시계.mp3" 2>/dev/null

# 926 묻지 않는 사랑 (Indie Acoustic)
curl -sL "https://cdn1.suno.ai/b8ba1799-87d5-42ff-a9ba-00f996868fef.mp3" -o "$TMPDIR/926_묻지_않는_사랑_full.mp3"
ffmpeg -y -i "$TMPDIR/926_묻지_않는_사랑_full.mp3" -t 60 -c copy "$OUT/926_묻지_않는_사랑.mp3" 2>/dev/null

# 941 우리의 기록 (Indie Acoustic)
curl -sL "https://cdn1.suno.ai/988b99f8-1d4d-436a-b230-3e224117664e.mp3" -o "$TMPDIR/941_우리의_기록_full.mp3"
ffmpeg -y -i "$TMPDIR/941_우리의_기록_full.mp3" -t 60 -c copy "$OUT/941_우리의_기록.mp3" 2>/dev/null

# 1173 일곱 번의 박수 (Jazz Ballad)
curl -sL "https://cdn1.suno.ai/ca926f7a-c342-4535-bfba-abf9fea25693.mp3" -o "$TMPDIR/1173_일곱_번의_박수_full.mp3"
ffmpeg -y -i "$TMPDIR/1173_일곱_번의_박수_full.mp3" -t 60 -c copy "$OUT/1173_일곱_번의_박수.mp3" 2>/dev/null

# 10009 한 정거장 전 (Jazz Ballad)
curl -sL "https://cdn1.suno.ai/e6e6e1f0-e3e5-4b06-bc36-63dfec07c366.mp3" -o "$TMPDIR/10009_한_정거장_전_full.mp3"
ffmpeg -y -i "$TMPDIR/10009_한_정거장_전_full.mp3" -t 60 -c copy "$OUT/10009_한_정거장_전.mp3" 2>/dev/null

# 10021 종이컵 하나의 무게 (Jazz Ballad)
curl -sL "https://cdn1.suno.ai/dad14c89-d885-4b8a-9635-e80391feb5eb.mp3" -o "$TMPDIR/10021_종이컵_하나의_무게_full.mp3"
ffmpeg -y -i "$TMPDIR/10021_종이컵_하나의_무게_full.mp3" -t 60 -c copy "$OUT/10021_종이컵_하나의_무게.mp3" 2>/dev/null

# 420 손잡이의 손들 (Dance Pop)
curl -sL "https://cdn1.suno.ai/307a433e-2090-4f5e-86d3-61782131e912.mp3" -o "$TMPDIR/420_손잡이의_손들_full.mp3"
ffmpeg -y -i "$TMPDIR/420_손잡이의_손들_full.mp3" -t 60 -c copy "$OUT/420_손잡이의_손들.mp3" 2>/dev/null

# 1150 야 어디야 (Dance Pop)
curl -sL "https://cdn1.suno.ai/10cc78a8-aa6b-4548-bf20-81456acbd221.mp3" -o "$TMPDIR/1150_야_어디야_full.mp3"
ffmpeg -y -i "$TMPDIR/1150_야_어디야_full.mp3" -t 60 -c copy "$OUT/1150_야_어디야.mp3" 2>/dev/null

# 1209 증인 (Art Pop)
curl -sL "https://cdn1.suno.ai/e64e9edd-50d6-45ad-a5aa-b5c2a309c54b.mp3" -o "$TMPDIR/1209_증인_full.mp3"
ffmpeg -y -i "$TMPDIR/1209_증인_full.mp3" -t 60 -c copy "$OUT/1209_증인.mp3" 2>/dev/null

# 1219 빈 방 (Art Pop)
curl -sL "https://cdn1.suno.ai/7bf4eb07-5ce6-449b-8e1d-39c8a1a419b8.mp3" -o "$TMPDIR/1219_빈_방_full.mp3"
ffmpeg -y -i "$TMPDIR/1219_빈_방_full.mp3" -t 60 -c copy "$OUT/1219_빈_방.mp3" 2>/dev/null

# 1100 빈 방석 (Acoustic Ballad)
curl -sL "https://cdn1.suno.ai/47d9f216-9c79-4102-9524-abbcd97d3b69.mp3" -o "$TMPDIR/1100_빈_방석_full.mp3"
ffmpeg -y -i "$TMPDIR/1100_빈_방석_full.mp3" -t 60 -c copy "$OUT/1100_빈_방석.mp3" 2>/dev/null

# 1153 이른 꽃잎 (Acoustic Ballad)
curl -sL "https://cdn1.suno.ai/7face89f-deeb-409e-b212-497b0d6121ba.mp3" -o "$TMPDIR/1153_이른_꽃잎_full.mp3"
ffmpeg -y -i "$TMPDIR/1153_이른_꽃잎_full.mp3" -t 60 -c copy "$OUT/1153_이른_꽃잎.mp3" 2>/dev/null

echo "Done: $(ls $OUT/*.mp3 2>/dev/null | wc -l) files"
rm -rf $TMPDIR