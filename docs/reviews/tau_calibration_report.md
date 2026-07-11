# τ 캘리브레이션 데이터셋 — reklcli 100곡 (2026-07-11T11:45:57)

- 프래그먼트 총 338개 · M1 best-vector 분포: p10=0.441 p25=0.522 p50=0.593 p75=0.657

## τ 후보별 gap율 (vector 단독 기준)

| τ | gap율 |
|---|---:|
| 0.35 | 1.5% |
| 0.40 | 6.5% |
| 0.45 | 11.2% |
| 0.50 | 19.2% |
| 0.55 | 34.3% |

현행 잠정 τ=0.45 (M2·M3 무적중 동시조건이라 실제 gap율은 위보다 낮음)

## 파일럿 10건 (Leo 검토·청음 대상 — 층화: 최저2+최고2+장르다양 6)

| track_id | 제목 | 아티스트 | 장르 | mean_vec | 판정 포인트 |
|---|---|---|---|---:|---|
| 77 | Raga Jog | Ravi Shankar | World Music | 0.445 | 저스코어(코퍼스 공백 의심) |
| 96 | Nangs | Tame Impala | Contemporary Instrumental | 0.447 | 저스코어(코퍼스 공백 의심) |
| 25 | Chariots of Fire | Vangelis | Film Score / OST | 0.698 | 고스코어(매칭 신뢰 확인용) |
| 27 | Heart of Courage | Two Steps From Hell (Thomas Bergersen) | Hybrid / Cinematic | 0.705 | 고스코어(매칭 신뢰 확인용) |
| 1 | Clair de Lune | Claude Debussy | Classical / Orchestral | 0.545 | 중간대(경계 판정용) |
| 84 | Solitude | Jinsang | Lo-fi / Neo-classical / Piano | 0.545 | 중간대(경계 판정용) |
| 37 | Silk Road (Theme) | Kitaro | New Age | 0.548 | 중간대(경계 판정용) |
| 54 | Watermelon Man | Herbie Hancock | Jazz | 0.551 | 중간대(경계 판정용) |
| 66 | Love on a Real Train | Tangerine Dream (Risky Business OST) | Electronic / Ambient | 0.565 | 중간대(경계 판정용) |
| 72 | Surfing with the Alien | Joe Satriani | Guitar Instrumental | 0.574 | 중간대(경계 판정용) |

판정 방법: 각 곡 `match --track-id N` 리포트의 치환표를 Leo가 검토 — "이 치환이 원곡 뉘앙스를 담는가" Y/N → Y/N 경계의 vec 스코어로 τ 확정.