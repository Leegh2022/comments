## 🥩영양갱(건강한 식단 관리 서비스)🍜
202284057이건해 202204060 이승우.

### 동기및 목적

 다양한 식품 선택으로 인해 자신의 영양소 섭취를 체계적으로 관리하기가 쉽지 않습니다. 이러한 문제를 해결하기 위 이 프로젝트는 사용자가 간편하게 자신의 식단을 기록하고 분석할 수 있는 플랫폼을 제공하고자 합니다. 사용자들이 자신의 영양소 섭취를 쉽게 파악하고 균형 잡힌 식단을 유지할 수 있도록 돕습니다

## 시스템 구조
![image](image.png)
1. 사용자는 Streamlit 프론트엔드를 통해 시스템과 상호작용한다.
2. Streamlit 프론트엔드는 데이터 관리 모듈이나 인증 모듈과 통신한다.
3. 데이터 관리 모듈은 데이터베이스 모델과 상호작용하고, SQLite DB에서 데이터를 가져온다.
4. 인증 모듈은 데이터베이스와 상호작용하여 사용자 인증을 처리한다.
5. OpenFoodFacts API를 통해 외부 데이터도 불러온다.

## 관련 연구
*네이버 클린봇*

딥러닝 기반 자연어 처리 기술로 한국어 문맥 이해와 감성 분석으로 유해댓글을 실시간으로 탐지하고 차단하며, 사용자 피드백을 통해지속적으로 학습하여 진화하는 비방 표현에도 대응하는 AI 댓글 필터링 시스템

## 개발 방법론

-애자일 방법론을 기반으로 진행됩니다  2주 단위마다 기능을 개발하고, 테스트하며, 피드백을 반영하여 개선합니다.
- Python을 주요 프로그래밍 언어로 사용하며, Flask와 같은 간단한 웹 프레임워크를 활용합니다


## 주요 기능


|   주요기능    |      내용                            |
| ---------- | ----------------------------------------------- |
| 1. 댓글 분류모델(NLP 기반)   |실시간긍정/부정/중립분석, 로지스틱회귀, BERT,                 |
|2. 딥러닝 기반 감정분석    | BERT, CNN, RNN 모델 활용 모델분석최적화    |
|3. 댓글 패턴 분석  | 장기적댓글분석,주간/월간                    |
|4. 커뮤니티 및 피드백시스템 | 분석결과 제공, 긍정적인 커뮤니티참여지원                 |

## 일정

| 주차       |  표 작업                                   |
| ---------- | ----------------------------------------------- |
| 1~2주차    |프로젝트 기획 및 자료 조사                       |
| 3~4주차    | 계획서 발표                         |
| 5~6주차    | 데이터 수집 및 전처리                       |
| 7~8주차    | 감정 분석 모델 개발                     |
| 9~10주차   | 모바일 애플리케이션 개발                             |
| 11~12주차  |추가 데이터 및 성능 향상           |
| 13~14주차  | 최종 배포                      |
| 15주차     | 최종 발표                            |

## 기대효과

- 악플을 감지하고 차단하여 사용자들의 정신적피해를줄입니다.
- 선플을 장려하고 악플을 억제하여 건전한 소통 문화를 형성합니다.
- 악플 감소와 선플 증가로 커뮤니티의 신뢰도와 사용자 만족도가 향상됩니다.
