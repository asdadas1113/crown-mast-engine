# 1연구 검증 자료

이 디렉터리는 1연구 설계와 실행 결과에 직접 귀속되는 검증 자료를 저장한다.

주요 검증 항목:

- roster 수와 중복 제외 검증
- 성장 표본 설계 검증
- 환경축 조합 수 검증
- 애장품 캐릭터 SR15 canonical floor 적용 검증
- scenario 생성 수 검증
- actor model-specific gate 검증
- 연구 실행 전후의 focused/full regression 기록
- close-call 및 sign flip 재검증 기록
- 이상치 재현 결과

현재 기록:

```text
01_연구_인프라_보강_검증_2026-09-06.md
02_저장소_정리_점검_2026-09-06.md
03_1연구_후보군_재구성_검증_2026-09-06.md
04_성장설계_3단계_완전교차_검증_2026-09-06.md
05_최종_실행전_검증_2026-09-06.md
```

각 문서의 성격은 다음과 같다.

- `01_...`: 재현성·입력 무결성·UI 초기화·패키징 보강 및 hardening 검증
- `02_...`: active 문서/브랜치/아카이브 구조 정리 점검
- `03_...`: B1 5 / Main 6 / Secondary 3 후보군 재구성 당시의 검증 기록. 당시 성장축은 16-point pairwise였으며 현재 성장설계는 04 문서에 의해 대체됨
- `04_...`: 현재 1연구 성장설계인 `g2/g3/g4` 3단계 × B1/Main/Secondary 완전교차 27-point 설계 검증
- `05_...`: numerical regression 분류, Moran/SBS/Liberalio model gate 종료, stale regression expectation 정리, 최종 322-test 회귀와 28,188 case-generation preflight 기록

현재 canonical 표본 산술은 다음과 같다.

```text
87 valid rosters
27 growth points
12 environments
324 scenarios / roster
28,188 expected scenarios
```

`03_...`의 16 growth / 16,704 scenario 수치는 후보군 재구성 당시의 역사적 검증값이며 현재 실행 설계값으로 사용하지 않는다.

## 현재 실행 전 gate 상태

최종 검증:

```text
GitHub Actions run: 34002759044
job: 101404457366
result: success
```

- focused Study 1/repaired actor tests: **68/68**
- full regression: **322/322**
- 28,188 case-generation preflight: **28,188/28,188**
- execution model gates: **0**
- `execution_ready=true`
- simulation executed: **no**

Moran Favorite Item, Scarlet: Black Shadow, Liberalio의 model-specific gate와 기존 numerical regression 분류는 모두 종료됐다.

현재 남아 있는 gate는 **사용자의 공식 연구 실행 승인**뿐이다. 승인 전에는 28,188 scenario 전투 시뮬레이션을 실행하지 않는다.

프로젝트 전체 테스트 코드는 루트 `tests/`에 유지한다. 여기에는 그 테스트의 연구별 실행 결과, 재현 로그, 표본 검증 결과 등 **1연구에 귀속되는 검증 산출물**을 보관한다.
