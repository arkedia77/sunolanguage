#!/usr/bin/env python3
# MOM10 — 컨셉앨범 「엄마」: 어머니 미움·그리움(어릴적 버림) 같은 컨셉, 다양한 곡 10곡.
# LEO 직지시(07-24): '같은 컨셉으로 한 배치를 다양하게'. 앨범=미움→원망→그리움→이해→수용 감정여정.
#   각 트랙 = 서로 다른 facet(감정각도) + 장르, 다른 가사. 10 병렬 전문 서브에이전트 저작→검증.
import os, json, psycopg2

THEME = "어머니에 대한 미움과 그리움 (어릴적 버림) — 미움→원망→그리움→이해→수용 감정여정 컨셉앨범"
ALBUM = "엄마 (Mom)"
BATCH = "MOM10"
GID0 = 30178  # 다음 가용: 30179~30188

SONGS = [
 {"pos":1,"title":"빈자리","title_en":"The Empty Seat","genre":"Acoustic Folk Ballad","genre_group":"Folk/Acoustic","sub":"Intimate confessional fingerstyle folk, minimal room-sound","bpm":76,"key":"D major","time_sig":"4/4","facet":"결핍 — 엄마 없이 자란 텅 빈 자리를 담담히 회상하되 속은 시린",
  "sp":"An intimate acoustic folk ballad, a bare confessional folk song built around soft fingerpicked steel-string acoustic guitar. Warm, close, minimal room-sound recording. Gentle fingerstyle folk in D major, slow and unhurried at 76 BPM, 4/4. Sparse arrangement: fingerpicked acoustic guitar as the sole harmonic foundation, with a faint low upright bass entering softly in the choruses. A quiet, breathy male vocal, tender and restrained, singing close to the mic with audible breath and a slight ache. The delivery is understated and reflective, never belting, holding back tears rather than crying. Subtle finger noise on the strings, natural woody resonance. No drums, no percussion, no electric instruments. The mood is nostalgic, aching and quietly lonely, a memory of an empty space where a mother should have been. Let the chorus hook land clearly and warmly, then dissolve back into solitary picking.",
  "lyrics":"""[Verse 1]
소풍 가는 아침 다른 애들 손엔
김밥 도시락이 꼭 쥐어져 있었지
나는 빈 가방 흔들며 웃었어
괜찮은 척 그게 제일 쉬웠으니까

[Verse 2]
운동회 날 관중석 저 끝을 봤어
엄마 하고 부르면 돌아볼 얼굴을
찾다가 그냥 신발끈만 묶었지
먼지 묻은 무릎을 털어내면서

[Pre-Chorus]
남들에겐 당연한 그 한 글자가
내 입 안에선 자꾸 얼어붙었어

[Chorus]
엄마라는 자리 내겐 텅 빈 자리
아무도 앉지 않은 낡은 그 의자
부르지 못한 이름 삼킨 채로 컸어
텅 빈 그 자리가 나를 키웠어

[Verse 3]
밤이 오면 벽에 등을 기대고
창밖 불빛들을 하나씩 세었지
저 집들 안엔 다 있을 것만 같아
내게만 없던 그 따뜻한 온기

[Bridge]
미워한 것도 아니야 그리운 것도 아니야
그냥 처음부터 비어 있던 자리
채울 수 없어서 그냥 안고 살았어

[Chorus]
엄마라는 자리 내겐 텅 빈 자리
아무도 앉지 않은 낡은 그 의자
부르지 못한 이름 삼킨 채로 컸어
텅 빈 그 자리가 나를 키웠어

[Outro]
오늘도 그 자리 조용히 비어 있어
이젠 익숙한 나의 빈자리"""},
 {"pos":2,"title":"왜 날 버렸어","title_en":"Why Did You Leave Me","genre":"Alternative Rock / Post-Rock","genre_group":"Rock","sub":"quiet-loud dynamic build from whispered verse to screamed catharsis","bpm":132,"key":"E minor","time_sig":"4/4","facet":"원망·분노 — 참았던 분노가 크레센도 타고 절규로 폭발, 답을 요구",
  "sp":"Alternative rock meets post-rock, a slow-burning quiet-loud eruption. Opens in half-time at 132 BPM in E minor: a single clean reverb-drenched guitar arpeggio, soft brushed drums, distant fragile male vocals whispered close to the mic, trembling. Post-rock crescendo architecture, layers accumulating patiently, tremolo-picked delayed guitars over a swelling low tom pulse. Pre-chorus tightens: palm-muted crunch guitar, driving bass, building snare. The chorus detonates into a full distorted guitar wall, cranked overdrive, crashing cymbals, pounding kick and toms, the male voice cracking from restraint into a raw impassioned scream, desperate and accusatory. Anthemic alt-rock hook, huge and cathartic. Bridge collapses to near-silence (feedback drone, whispered vocal), then a final towering post-rock climax, wall-of-sound distortion, layered screamed harmonies. Emotional, dynamic, explosive. Gritty analog production, live-band energy, wide stereo guitars.",
  "lyrics":"""[Verse 1]
텅 빈 방 불 꺼진 창가에
혼자 남겨진 그 밤을 기억해
네 발소리 멀어지던 복도
난 아직도 그 문 앞에 서 있어

[Pre-Chorus]
참고 참았던 이 말이
목구멍을 타고 올라와
더는 삼킬 수가 없어

[Chorus]
왜 날 버렸어 대답해 봐
어린 나를 두고 어디로 갔어
왜 날 버렸어 말해 보라고
내가 뭘 잘못했는지 말해 보라고

[Verse 2]
네가 없던 밤마다 난 울었고
네 이름을 부르다 잠들었어
돌아온다던 그 약속은
먼지처럼 바닥에 흩어졌어

[Pre-Chorus]
이제 와 웃으며 손 내밀지 마
그 손을 난 기억해
날 밀어냈던 그 손

[Chorus]
왜 날 버렸어 대답해 봐
어린 나를 두고 어디로 갔어
왜 날 버렸어 말해 보라고
내가 뭘 잘못했는지 말해 보라고

[Bridge]
엄마…
난 그저 안기고 싶었어
근데 넌 왜 왜 날 버렸어

[Chorus]
왜 날 버렸어 소리쳐도
돌아오지 않는 텅 빈 메아리
왜 날 버렸어 부서지도록
이 밤이 다 타버리도록 소리쳐"""},
 {"pos":3,"title":"얼굴도 기억 안 나는데","title_en":"I Can't Even Remember Your Face","genre":"neo-soul, alt-R&B slow jam","genre_group":"R&B/Soul","sub":"따뜻한 로즈와 스페이시 리버브 위 소울풀 미드나잇 슬로우잼","bpm":72,"key":"F# minor","time_sig":"4/4","facet":"그리움·사무침 — 미움 내려놓고 얼굴도 흐릿한 엄마를 순수하게 그리워하는 밤",
  "sp":"A tender neo-soul, alt-R&B slow jam that breathes and aches. Warm, mellow Fender Rhodes electric piano at the heart, chords voiced with soft seventh and ninth extensions, drenched in spacious plate reverb. Slow, laid-back R&B groove with brushed, cushioned drums, soft rimshots and a gentle pocket, deep round fingered bass sitting low and warm. Tempo around 72 BPM in F# minor, 4/4, unhurried and floating. Midnight neo-soul, quiet-storm slow jam, contemporary alt-R&B balladry. Lead vocal is a soulful female voice, breathy and intimate, close-miked, with delicate melisma and gospel-tinged runs that trail into silence. Airy layered background harmonies, soft oohs drifting like memory. Subtle warm analog tape saturation, glassy electric piano bell tones. Emotionally it is longing and yearning, aching tenderness, a night of pure missing after letting the anger fall away. Dynamics stay soft and restrained, swelling only slightly in the chorus. Neo-soul, alt-R&B, slow jam, soul ballad.",
  "lyrics":"""[Verse 1]
창문에 김이 서린 이런 밤이면
괜히 오래된 사진첩을 꺼내요
흐릿한 웃음 하나 손끝에 닿는데
엄마 얼굴은 자꾸만 지워져가

[Pre-Chorus]
미워했던 마음 오늘은 내려놓고
그냥 아이처럼 불러보고 싶어

[Chorus]
얼굴도 잘 기억 안 나는데
왜 이렇게 사무치게 보고 싶을까
이름 두 글자 삼키다 목이 메어
엄마, 이 밤이 너무 길어요
보고 싶다는 말밖엔 없어

[Verse 2]
내 손을 놓던 그 골목은 잊었어
원망도 이젠 다 바래버렸죠
남은 건 어릴 적 등에 업힌 온기
그 하나가 오늘 나를 울려요

[Pre-Chorus]
돌아오라 말하는 게 아니에요
그저 한 번만 안겨보고 싶어

[Chorus]
얼굴도 잘 기억 안 나는데
왜 이렇게 사무치게 보고 싶을까
이름 두 글자 삼키다 목이 메어
엄마, 이 밤이 너무 길어요
보고 싶다는 말밖엔 없어

[Bridge]
미움은 이렇게 옅어지는데
그리움은 왜 더 짙어만 가
어디에 있든 잘 지내나요
나는요, 나는 아직도 그날에 서 있어

[Chorus]
얼굴도 잘 기억 안 나는데
사무치게, 사무치게 보고 싶어
이름 두 글자 끝내 부르지 못해
엄마, 이 밤을 건너가요
보고 싶다는 말만 남겨

[Outro]
보고 싶어요
그저 보고 싶어요"""},
 {"pos":4,"title":"엄마를 닮을까 봐","title_en":"Afraid I'll Become You","genre":"indie pop rock, jangle-pop","genre_group":"Indie/Rock","sub":"밝고 쌉싸름한 밴드 사운드의 자기성찰 인디록","bpm":112,"key":"D major","time_sig":"4/4","facet":"대물림 두려움 — 사랑을 못 배워 대물림할까 겁내는 성인 화자의 자기성찰",
  "sp":"Bright but bittersweet indie band pop, jangle-pop in the vein of college-radio indie rock. Warm, chiming clean electric guitars with bright jangly arpeggios and open-chord strums, layered with a second capo'd guitar for shimmer. Bouncy, melodic bass that walks and skips between the beat. Live-kit drums with a driving but relaxed backbeat, brushy hi-hats, natural room tone. Tempo 112 BPM, D major, 4/4. Male lead vocal, mid-20s timbre, slightly breathy and vulnerable, conversational in the verses, opening up earnest and full-throated in the choruses. Layered gang-vocal harmonies and oohs for a singalong, anthemic chorus hook. Tambourine and handclaps in the chorus. Verses sparse and reflective; pre-chorus builds; chorus blooms wide and jangly. Youthful, hopeful, tender, self-aware mood, warm and major-key even as the lyric confesses fear. Clean indie production, analog warmth, live and organic.",
  "lyrics":"""[Verse 1]
거울 앞에 서면 가끔 니가 보여
웃는 입꼬리가 어쩜 이리 닮았을까
무서워진 밤엔 이불을 뒤집어써
나도 언젠가 누굴 아프게 할까 봐

[Pre-Chorus]
사랑한다는 말
난 배운 적이 없어서
손 내미는 법을 몰라 자꾸 뒷걸음쳐

[Chorus]
엄마를 닮을까 봐, 그게 제일 무서워
받은 적 없는 걸 어떻게 다 주겠어
그래도 나는, 그래도 나는
너한텐 다르고 싶어, 정말 다르고 싶어
오오오 오오오, 다르고 싶어

[Verse 2]
너의 눈을 보면 마음이 자꾸 떨려
안아주고 싶은데 팔이 굳어버리네
놓아버릴까 봐, 상처를 줄까 봐
차라리 혼자가 편했던 나였는데

[Pre-Chorus]
따뜻한 그 온기
난 낯설기만 해서
도망치고 싶다가도 니 앞에 멈춰 서

[Chorus]
엄마를 닮을까 봐, 그게 제일 무서워
받은 적 없는 걸 어떻게 다 주겠어
그래도 나는, 그래도 나는
너한텐 다르고 싶어, 정말 다르고 싶어
오오오 오오오, 다르고 싶어

[Bridge]
어쩌면 대물림은 여기서 끝날지 몰라
내가 처음으로 사랑을 배운다면
떨리는 이 손을
용기 내 너에게 내밀어 볼게

[Chorus]
엄마완 다를 거야, 이젠 두렵지 않아
서툴러도 매일 조금씩 배워갈게
그래서 나는, 그래서 나는
너에게 처음이 되고 싶어, 좋은 처음이
오오오 오오오, 사랑할게
오오오 오오오, 사랑할게"""},
 {"pos":5,"title":"너도 무서웠니","title_en":"Were You Afraid Too","genre":"tender piano ballad","genre_group":"Ballad/Piano","sub":"미니멀 그랜드 피아노 발라드+후반 스트링, 감정 억제된 보컬","bpm":70,"key":"D major","time_sig":"4/4","facet":"그녀의 사정 상상 — 엄마의 입장에 서서 '너도 어리고 무서웠니' 묻는 흔들림",
  "sp":"A tender, restrained piano ballad built almost entirely around a soft solo grand piano. Slow, intimate, sparse. BPM 70, 4/4, key of D major. The heart is a warm, close-miked grand piano playing gentle broken chords and simple arpeggios with generous sustain-pedal resonance and quiet room air. Keep the first half nearly bare: just piano and a single female voice. The vocal is a soft, emotionally suppressed female voice, breathy and low in the mix, almost a whisper-confession, measured and aching, holding tears back. Phrasing is conversational and unhurried, with fragile head-voice on sustained notes. In the second half, introduce a subtle string section, muted cellos and small violin ensemble swelling softly under the chorus and bridge, never overpowering the piano. No drums, no percussion, no bass groove, only piano, voice and late strings. Melancholic, forgiving, bittersweet, cinematic and understated, like a quiet letter read aloud in an empty room.",
  "lyrics":"""[Verse 1]
이제야 너의 나이가 되어
거울 앞에 서 본다
스물 몇 살의 너는
무얼 그리 두려워했을까

[Verse 2]
작은 방 한 칸도 버거웠던
그 겨울의 손끝
나를 안기엔 네 품이
너무 어렸던 걸까

[Pre-Chorus]
미워하려 했는데
자꾸만 네가 보여

[Chorus]
너도 무서웠니
벼랑 끝에 홀로 서서
울음을 삼키던 밤
너도 어렸던 거니
엄마라는 이름이
너에겐 너무 무거웠니

[Verse 3]
돌아서던 네 뒷모습이
실은 떨고 있었단 걸
이제야 조금은
알 것도 같아서

[Pre-Chorus]
원망하려 했는데
자꾸만 목이 메어

[Chorus]
너도 무서웠니
벼랑 끝에 홀로 서서
울음을 삼키던 밤
너도 어렸던 거니
엄마라는 이름이
너에겐 너무 무거웠니

[Bridge]
용서한다 말은 못 해도
이해하고 싶어
너를 미워한 만큼
너를 안아보고 싶어

[Chorus]
너도 힘들었니
나를 두고 가던 길이
네게도 아팠던 거니
너도 그리웠던 거니
엄마라는 그 자리가
우리 둘 다 처음이었잖아

[Outro]
너도… 무서웠구나"""},
 {"pos":6,"title":"만약 골목에서 너를","title_en":"If I Met You on the Street","genre":"Dream Pop / Shoegaze","genre_group":"Dream Pop/Shoegaze","sub":"리버브에 젖은 몽환적 기타 월과 아득한 보컬의 부유하는 슈게이즈","bpm":90,"key":"B major","time_sig":"4/4","facet":"재회 상상 — 길에서 마주친 엄마를 상상, 무슨 말 건넬지 되뇌는 몽환",
  "sp":"Dream pop drenched in shoegaze haze, a slow floating reverie at 90 BPM in B major, 4/4. This is wall-of-reverb dream pop, hazy shoegaze, glide-guitar dreamscape music. Layer chiming, heavily reverbed electric guitars with slow chorus and tremolo, guitar walls washed in cathedral reverb and tape delay, one clean arpeggio glimmering far in the mix. Add warm analog synth pads, foggy and glassy, drifting under everything like slow tide. Bass is soft, round, patient. Drums are muted and distant, brushed and blurry, a gentle heartbeat rather than a beat. The voice is a female vocal, airy and breathy, soaked in reverb, sounding far away as if remembered, half-whispered and dreamlike, floating on top of the mist with soft doubled harmonies. Delivery is tender, wistful, suspended between waking and dreaming. Dynamics swell and recede like breathing. Melancholic, longing, weightless. Keep it lush, blurred, and gently aching, guitars blooming into a hazy shimmering chorus.",
  "lyrics":"""[Verse 1]
흐린 오후 낯선 거리를 걷다
네 뒷모습을 본 것 같아
스쳐가는 사람들 틈에서
숨이 잠깐 멎었어

[Pre-Chorus]
돌아보면 아무도 없고
안개 같은 네 얼굴만

[Chorus]
만약 골목에서 너를 만난다면
난 뭐라고 말할까
미워했다고 보고 싶었다고
둘 다 삼켜버릴까
꿈결처럼 흐릿한 그 자리에서
네 손을 잡아볼까

[Verse 2]
신호등이 붉게 물드는 사이
네 목소리가 들린 것 같아
엄마라고 부르려다
입술이 얼어붙어

[Pre-Chorus]
눈을 뜨면 사라질 너
조금만 더 머물러줘

[Chorus]
만약 골목에서 너를 만난다면
난 뭐라고 말할까
미워했다고 보고 싶었다고
둘 다 삼켜버릴까
꿈결처럼 흐릿한 그 자리에서
네 손을 잡아볼까

[Bridge]
현실인지 꿈인지 모를 빛 속에
어린 내가 너를 부르고 있어
이번엔 등 돌리지 마
이번엔 나를 안아줘

[Chorus]
만약 골목에서 너를 만난다면
난 웃어볼게 처음으로
미웠던 만큼 그리웠다고
작게 속삭여볼게
안개가 걷히기 전에 한 번만
네 이름을 불러볼게"""},
 {"pos":7,"title":"두 글자","title_en":"Two Syllables","genre":"alternative hip-hop, spoken word","genre_group":"Hip-Hop","sub":"미니멀 로파이 랩·스포큰워드 벌스에 노래하는 멜랑콜리 훅","bpm":86,"key":"F# minor","time_sig":"4/4","facet":"호명의 무게 — '엄마' 두 글자가 목에 걸려 안 나오는, 부를 대상 없는 호칭의 아이러니",
  "sp":"Alternative hip-hop with spoken word at its core. A minimal lo-fi hip-hop beat, dusty and unhurried at 86 BPM in F# minor, 4/4. Soft vinyl crackle and tape hiss. A melancholy piano loop, three or four lonely chords with heavy sustain, circling like a thought that won't resolve. A muted round sub-bass and a laid-back boom-bap kick and rimshot, swung slightly off the grid. Verses are restrained male rap and spoken word, close-mic'd and intimate, almost whispered, breath audible, conversational and confessional, no bravado, plain honest delivery just above the beat. The pre-hook eases into half-time. The hook is sung, not rapped: a fragile breathy male voice, low and aching, a small unadorned melody with quiet reverb and a faint double. Warm synth pads bloom under the hook. Space and silence between phrases; the track breathes. Sparse, sad, sincere, bedroom lo-fi warmth, late-night mood. End soft, piano loop and crackle fading alone.",
  "lyrics":"""[Verse 1]
두 글자야, 딱 두 글자
남들은 하품처럼 뱉는 그 말인데
내 혀 위에선 자꾸 무게가 실려
입천장에 붙어 안 떨어지는 이름 하나

식당에서 애가 그 말을 부를 때
나도 모르게 고개가 돌아가
아니야, 나 부른 거 아니야
난 그 말을 걸 데가 없는 사람이야

[Pre-Chorus]
혀끝까지 왔다가
목에서 그냥 멈춰
소리가 되기 전에
삼켜버린 그 두 글자

[Hook]
엄, 마
딱 두 글자면 되는데
엄, 마
왜 나는 못 부르나
부를 사람이 없는 이름을
입 안에서만 굴려봐
엄, 마

[Verse 2]
사전엔 있어, 뜻도 또렷해
근데 내 문장엔 주소가 없어
편지 첫 줄에 그 말을 쓰다가
펜을 놓고 종이를 접어

다들 쉽게 사는 그 흔한 단어가
왜 나한텐 돌덩이가 됐나
무겁지도 않은 두 음절이
나를 통째로 눌러 앉혀

[Pre-Chorus]
연습해봤어 거울 앞에서
입 모양만 만들다
소리는 끝내 안 나오고
또 그냥 삼킨 두 글자

[Hook]
엄, 마
딱 두 글자면 되는데
엄, 마
왜 나는 못 부르나
부를 사람이 없는 이름을
입 안에서만 굴려봐
엄, 마

[Bridge]
어쩌면 나는 그 말을 아껴둔 걸지도 몰라
언젠가 부를 데가 생기면
그때 딱 한 번, 온전히
목에 걸리지 않게

[Outro]
두 글자야, 딱 두 글자
오늘도 입 안에서만 살다 가
엄…
마…"""},
 {"pos":8,"title":"아무 일도 없었던 것처럼","title_en":"As If Nothing Ever Happened","genre":"ambient minimal electronic","genre_group":"Electronic/Ambient","sub":"차갑고 넓은 신스 패드 위 미니멀 펄스·글리치, 리버브에 잠긴 아득한 보컬","bpm":96,"key":"A minor","time_sig":"4/4","facet":"무감·망각 시도 — 감정을 눌러 끈 마비, 무감함 자체가 상처의 증거",
  "sp":"Cold, spacious ambient minimal electronic. A wide, slow-drifting synth pad stretches across an empty stereo field, glassy and detached. Underneath, a minimal muted pulse ticks at 96 BPM, steady and mechanical, almost heartbeat-flat, never building. Sparse glitch textures flicker like static memory, clicks and grains far back in the mix. Deep sub-bass hums low and hollow. Everything drenched in long reverb and gentle low-pass filtering, as if heard underwater or through a wall. The lead vocal is androgynous and breathy, sung close but processed distant, heavy reverb tails, subtle pitch-shifted doubles, whispered and numb, almost speaking. No emotional swell; the delivery stays flat, muted, resigned, as if feeling were switched off. Key of A minor, 4/4, downtempo, around 96 BPM but felt slower. Long empty pauses between phrases. Faint tape hiss. A cold, weightless, floating void, beautiful but anesthetized. No crash, no climax, only slow drift and fade.",
  "lyrics":"""[Verse 1]
괜찮아 나는 아무렇지 않아
오래전 일이야 이제 다 지웠어
네 이름 석 자쯤 흐릿해졌고
창밖은 오늘도 조용히 밝아

[Pre-Chorus]
울지 않아 웃지도 않아
그냥 이렇게 텅 빈 채로

[Chorus]
아무 일도 없었던 것처럼
숨을 쉬고 밥을 먹고 잠을 자
아무도 없었던 것처럼
네가 놓은 그 손을 기억 못 해
괜찮아 정말 괜찮아
(괜찮아… 괜찮아…)

[Verse 2]
사진 속 얼굴에 먼지가 앉고
나는 하루하루 무표정해져
감정이란 건 어디로 갔을까
스위치를 끈 듯 아무것도 안 느껴

[Pre-Chorus]
미워하지도 그립지도 않아
다 지운 자리 하얀 여백

[Chorus]
아무 일도 없었던 것처럼
숨을 쉬고 밥을 먹고 잠을 자
아무도 없었던 것처럼
네가 놓은 그 손을 기억 못 해
괜찮아 정말 괜찮아
(괜찮아… 괜찮아…)

[Bridge]
근데 왜 이렇게 아무렇지 않을까
아무렇지 않다는 게 왜 이렇게 시릴까
텅 빈 방 한가운데 서서
나는 나에게 조용히 물어

[Outro]
괜찮아… 괜찮아…
아무 일도… 없었던 것처럼…
(없었던 것처럼…)"""},
 {"pos":9,"title":"부치지 못한 편지","title_en":"The Letter I Never Sent","genre":"Cinematic String Ballad","genre_group":"Ballad/Orchestral","sub":"웅장한 오케스트라 스트링과 그랜드 피아노의 극적 크레센도 발라드","bpm":70,"key":"D minor","time_sig":"6/8","facet":"부치지 못한 편지 — 주소 없는 편지에 원망·그리움이 한 문장에 뒤엉킨 고백",
  "sp":"Cinematic string ballad, a grand orchestral confession built for tears. Slow, aching 6/8 at 70 BPM in D minor. Opens with a lone grand piano, felt hammers, intimate and close-miked, single notes falling like ink onto paper. A solo cello enters low and mournful, then a full string section swells underneath in long legato bows. Female lead vocal, mid-to-low alto, breathy and cracked at the edges, singing as if reading a letter aloud, restrained in verses then breaking open. Pre-chorus adds subtle timpani rolls and rising string tremolo. The chorus is a massive orchestral crescendo: soaring high violins, harp glissando, distant brass swells, dramatic lift from whisper to full-throated belt, raw and pleading. Bridge strips to piano and a trembling solo violin, near silence, before the final chorus explodes with choir-like string overdubs and a last desperate high note. Reverb-heavy cinematic hall ambience, wide stereo strings, film-score grandeur. Emotional, tragic, longing, tearful.",
  "lyrics":"""[Verse 1]
첫 줄부터 지웠어 몇 번을 다시 썼는지
엄마 잘 지내 그 말이 왜 이리 어려운지
주소도 없는 봉투에 마음만 눌러 담고
부칠 수 없는 편지를 오늘도 접어 두네

[Pre-Chorus]
미워했다고 쓰려다
보고 싶었다 적어버린 이 손

[Chorus]
잘 지내 잘 지내 나는 잘 지내고 있어
보고 싶었어 그 말을 이제야 꺼내 봐
왜 그랬어 왜 나를 그 골목에 두고 갔어
답장 없을 걸 알면서 또 부르는 그 이름 엄마

[Verse 2]
네 손이 차가웠던 그 겨울을 기억해
돌아설 때 네 등이 흔들렸던 것도 봤어
원망과 그리움이 같은 줄에 나란히
번진 잉크 사이로 눈물이 또 스며드네

[Pre-Chorus]
이해한다 쓰려다
용서 못 해 지워버린 이 밤

[Chorus]
잘 지내 잘 지내 나는 잘 지내고 있어
보고 싶었어 그 말을 이제야 꺼내 봐
왜 그랬어 왜 나를 그 골목에 두고 갔어
답장 없을 걸 알면서 또 부르는 그 이름 엄마

[Bridge]
혹시 너도 어딘가 이런 편지 쓰고 있을까
부치지 못한 채로 나를 접어 두었을까

[Final Chorus]
잘 있어 잘 있어 부디 거기선 잘 있어
미웠던 만큼 딱 그만큼 그리웠단 걸 알아줘
돌아와 달란 말은 이제 하지 않을게
다만 이 한 줄만 닿기를 사랑했어 나의 엄마"""},
 {"pos":10,"title":"이제 놓아줄게","title_en":"I Let You Go Now","genre":"Gospel Soul","genre_group":"R&B/Soul","sub":"따뜻한 Hammond 오르간과 가스펠 합창이 이끄는 정화의 소울 발라드","bpm":76,"key":"G major","time_sig":"4/4","facet":"화해·놓아주기(수용) — 미움을 나를 위해 내려놓는 벅찬 정화, 앨범의 귀결",
  "sp":"Warm, cathartic gospel soul ballad, slow and swelling at around 76 BPM in G major, 4/4. A tender soul ballad that grows into full gospel. Rooted in a warm, breathing Hammond B3 organ with slow Leslie swell, rich gospel piano with rolling triplet fills, soft brushed drums, round upright-style bass, and gentle rising strings in the later half. Gospel-soul feel throughout: church-organ warmth, soulful phrasing, hand-clap lift near the climax. Lead vocal is a warm female alto, intimate and slightly husky in the verses, breathy and confessional, then opening up with soulful melisma and gospel runs in the choruses. Verses stay quiet and prayerful; pre-chorus builds; the chorus blooms wide. A late gospel choir enters in call-and-response, layered harmonies, cathartic and uplifting, ascending and purifying toward a warm, resolved, forgiving ending. Emotional, redemptive, letting-go gospel soul.",
  "lyrics":"""[Verse 1]
오래 쥐고 있었어 이 무거운 돌 하나
네 이름만 스쳐도 아직 손이 떨렸지
어린 나를 두고 간 그 골목의 겨울을
난 여태 껴안고서 여기 서 있었어

[Pre-Chorus]
그런데 오늘은 조금 다르게
숨을 쉬어 보려 해 처음으로

[Chorus]
이제 놓아줄게 미움도 원망도
용서라 부르진 않아 그냥 날 위한 일
상처는 안은 채로 한 걸음 나아갈게
무거웠던 이 손 이제 펴고 놓아줄게

[Verse 2]
엄마도 아이였겠지 두려움에 떨던
그 밤이 어땠는지 난 다 알진 못해도
미워하던 마음마저 이젠 내려놓을 때
네가 아닌 나를 위해 나를 자유케 해

[Pre-Chorus]
눈물이 흘러도 이건 무너짐이 아냐
씻겨 내려가는 오래된 강물이야

[Chorus]
이제 놓아줄게 미움도 원망도
용서라 부르진 않아 그냥 날 위한 일
상처는 안은 채로 한 걸음 나아갈게
무거웠던 이 손 이제 펴고 놓아줄게

[Bridge]
(놓아줄게) 이 겨울을
(놓아줄게) 그 골목을
안녕이라 말할게 미움 없이 이젠
벅찬 이 가슴으로 앞으로 걸어갈게

[Chorus]
이제 놓아줄게 다 놓아줄게
용서보다 깊은 건 나를 사랑하는 일
상처를 빛으로 바꿔 앞으로 나아갈게
활짝 편 이 두 손 하늘 향해 놓아줄게

[Outro]
이제 미워하지 않을게
이제 나를 놓아줄게"""},
]

over=[s for s in SONGS if len(s["sp"])>1000]
for s in SONGS:
    print(f"  {BATCH}-{s['pos']:<2} {s['genre_group']:<18} {s['title']:<20} {s['key']:<9} {s['bpm']}BPM  SP={len(s['sp'])}  LYR={len(s['lyrics'])}{'  OVER!' if len(s['sp'])>1000 else ''}")
assert not over, f"SP over 1000: {[s['pos'] for s in over]}"
assert len({s['pos'] for s in SONGS})==10
print(f"SP gate: ALL {len(SONGS)} PASS (<=1000)")

if os.environ.get("DRYRUN"):
    print("DRYRUN — DB insert 생략"); raise SystemExit(0)

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
       ALBUM, f"facet: {s['facet']}", 'ko', len(s["sp"])))
    gids.append(cur.fetchone()[0])
c.commit()
print("INSERTED gids:", gids)
cur.execute(f"SELECT global_id,title,genre,bpm,key_signature,status FROM songs WHERE batch='{BATCH}' ORDER BY global_id;")
print("VERIFY:"); [print("  ",r) for r in cur.fetchall()]
c.close()

os.makedirs('data/concept', exist_ok=True)
batch={"batch":BATCH,"album":ALBUM,"line":"sunolanguage","theme":THEME,"created":"2026-07-24",
 "gid_range":f"{GID0+1}~{GID0+len(SONGS)}",
 "origin":"LEO 직지시 07-24: '같은 컨셉으로 한 배치를 다양하게'. JMOM 어머니 미움·그리움 컨셉을 다양한 곡(다른 가사·장르·각도)으로 앨범화.",
 "concept":"미움→원망→그리움→이해→수용 감정여정. 10 facet×10 장르. JMOM '그 골목 끝에서'와 가사 비중복(골목 모티프는 앨범 공통 이미지로 재등장).",
 "songs":[{"gid":GID0+s["pos"],"id":f"{BATCH}-{s['pos']}","title":s["title"],"title_en":s["title_en"],
   "genre":s["genre"],"genre_group":s["genre_group"],"facet":s["facet"],
   "bpm":s["bpm"],"key":s["key"],"time_sig":s["time_sig"],"is_instrumental":False,
   "style_prompt":s["sp"],"sp_length":len(s["sp"]),"lyrics":s["lyrics"]} for s in SONGS]}
json.dump(batch, open('data/concept/MOM10_batch.json','w'), ensure_ascii=False, indent=2)
print("batch JSON -> data/concept/MOM10_batch.json")
