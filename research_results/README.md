# Crown–Mast Research Results

이 디렉터리는 **공식 연구 결과를 수집·보존하는 전용 공간**이다.

## 목적

기존 `docs/RAID14_CHECKPOINT_*` 문서와 개발 중 실험값은 엔진 검증·탐색·회귀 확인을 위한 역사적 checkpoint다. 이 디렉터리의 자료와 섞지 않는다.

공식 연구 결과는 연구 설계가 확정된 뒤 현행 검증 엔진으로 새로 수집한다.

## 운영 원칙

1. 연구 결과를 생성하기 전 엔진/캐릭터 메커니즘/시간축 검증을 끝낸다.
2. 결과 파일에는 최소한 다음을 기록한다.
   - engine rule revision
   - skill-hook revision
   - branch / commit SHA
   - RAID14 timeline revision
   - roster
   - 성장 프로필
   - core 조건
   - main elemental-advantage 조건
   - 비교 rotation
3. 기존 checkpoint 숫자를 공식 결과로 복사하지 않는다.
4. 연구 batch는 사용자 명시 승인 후에만 실행한다.
5. 원자료와 요약/해석을 분리한다.
6. 승패 빈도만 보지 않고 **효과크기와 역전 조건의 구조**를 함께 기록한다.
7. 각 grid point는 확률 표본이 아니라 통제된 결정론적 scenario다. 승리 비율을 실전 발생확률로 해석하지 않는다.

## 현재 연구 질문

외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때:

- 관습적인 `강한 메인 딜러 → Mast 몰아주기`가 실제로 얼마나 넓은 조건에서 유효한가?
- 유효한 경우 이득 폭은 얼마나 큰가?
- 유효 조건이 정상적인 실전 파티 구조에서 자주 만들어질 만한가?

정확한 보편 임계값을 추정하는 것이 주목적은 아니다.

## 현재 초안

- Secondary B3 experimental anchors: `Epinel / Helm / Snow White: Heavy Arms`
- 상세 취지: `SECONDARY_B3_ANCHORS_DRAFT.md`
- 공식 결과: 아직 없음
