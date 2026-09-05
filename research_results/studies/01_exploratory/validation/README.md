# 1연구 검증 자료

이 디렉터리는 1연구 설계와 실행 결과에 직접 귀속되는 검증 자료를 저장한다.

주요 검증 항목:

- roster 수와 중복 제외 검증
- 성장 표본 설계 검증
- 환경축 조합 수 검증
- 애장품 캐릭터 SR15 canonical floor 적용 검증
- scenario 생성 수 검증
- close-call 및 sign flip 재검증 기록
- 이상치 재현 결과
- 연구 실행 전후의 focused regression 기록

현재 기록:

```text
01_연구_인프라_보강_검증_2026-09-06.md
02_저장소_정리_점검_2026-09-06.md
03_1연구_후보군_재구성_검증_2026-09-06.md
04_성장설계_3단계_완전교차_검증_2026-09-06.md
```

각 문서의 성격은 다음과 같다.

- `01_...`: 재현성·입력 무결성·UI 초기화·패키징 보강 및 hardening 검증
- `02_...`: active 문서/브랜치/아카이브 구조 정리 점검
- `03_...`: B1 5 / Main 6 / Secondary 3 후보군 재구성 당시의 검증 기록. 당시 성장축은 16-point pairwise였으며, **현재 성장설계는 04 문서에 의해 대체됨**
- `04_...`: 현재 1연구 성장설계인 `g2/g3/g4` 3단계 × B1/Main/Secondary 완전교차 27-point 설계 검증

현재 canonical 표본 산술은 다음과 같다.

```text
87 valid rosters
27 growth points
12 environments
324 scenarios / roster
28,188 expected scenarios
```

`03_...`의 16 growth / 16,704 scenario 수치는 후보군 재구성 당시의 역사적 검증값이며 현재 실행 설계값으로 사용하지 않는다.

현재 공식 연구 실행 전에는 다음 gate가 남아 있다.

- Moran Favorite Item model-specific 재검증
- Scarlet: Black Shadow model-specific 재검증
- Liberalio model-specific 재검증
- 기존 full regression의 초미세 numerical baseline 실패 3건 분류 및 clean regression 확보
- 최종 87/27/12/28,188 preflight 및 manifest 실행값 동결

프로젝트 전체 엔진의 pytest 테스트 코드는 루트 `tests/`에 유지한다. 여기에는 그 테스트의 연구별 실행 결과, 재현 로그, 표본 검증 결과 등 **1연구에 귀속되는 검증 산출물**을 보관한다.

현재는 정식 연구 표본 batch를 실행하지 않는다. 사용자 명시 승인 전에는 28,188 scenario aggregate를 실행하지 않는다.
