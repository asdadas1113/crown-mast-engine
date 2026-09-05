# Crown–Mast 연구 결과 / 현재 상태

이 디렉터리는 **앞으로 재검증된 새 연구의 상태와 결과만** 담는 active 영역이다.

과거 연구 설계·진단·결과는 다음 archive에 보존한다.

```text
archive/pre-revalidation-2026-09-05/research_results/
```

과거 29,952 scenario 결과는 새 연구의 결론·목표값·사전 기대값으로 사용하지 않는다.

## 현재 읽을 것

```text
RESEARCH_STATUS_2026-09-05.md
../docs/CURRENT_RESEARCH_HANDOFF_2026-09-06.md
../docs/SOURCE_VALIDATION_POLICY.md
studies/README.md
studies/01_exploratory/human/01_연구_설계_초안.md
studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
studies/01_exploratory/validation/01_연구_인프라_보강_검증_2026-09-06.md
studies/01_exploratory/validation/02_저장소_정리_점검_2026-09-06.md
```

## 새 연구 저장 원칙

새 연구는 `studies/` 아래에서 연구 단위로 분리한다.

- `human/`: 사람이 읽는 한글 연구 문서
- `machine/`: manifest, scenario, raw, aggregate, provenance
- `validation/`: 표본 검증, 민감도 점검, 이상치 재현, focused regression 기록

프로젝트 전체 pytest 코드는 루트 `tests/`에 유지한다.

## 1연구의 역할

1연구는 보편적인 단일 임계값이나 최적 운용 규칙을 확정하는 것이 아니라, **대표적인 Crown/Mast 통제 조건에서 광범위한 조합을 탐색하고 우세 경향과 예외를 찾은 뒤 후속 연구 후보를 고르는 단계**다.

현재 canonical 설계:

```text
studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

study ID:

```text
crown-mast-study-01-exploratory-v1
```

현재 후보군:

```text
B1
- liter
- anis-star
- moran-favorite-item
- little-mermaid
- rapi-red-hood

Main B3
- rapi-red-hood
- scarlet-black-shadow
- cinderella
- cinderella-crystal-wave
- liberalio
- neon-vision-eye

Secondary B3
- epinel
- helm
- snow-white-heavy-arms
```

현재 성장 설계:

```text
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

- `g1-base5-none`은 1연구에서 제외
- 세 성장 단계는 B1/Main/Secondary에 완전교차
- 3 × 3 × 3 = **27 growth points**
- 애장품 캐릭터는 SR15 canonical floor 유지

현재 전체 설계:

- raw roster 90
- Rapi B1/Main 중복 3개 제외
- **87 valid rosters**
- B1/Main/Secondary 27-point full growth grid
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 **324 scenarios**
- 전체 **28,188 scenarios**
- Crown/Mast OL5 + SR15 대표 build 고정

## 실행 전 model gate

다음 선택 캐릭터는 공식 실행 전 model-specific 재검증이 필요하다.

```text
moran-favorite-item
scarlet-black-shadow
liberalio
```

후보군에는 포함하지만 이 gate가 닫히기 전에는 공식 aggregate를 실행하지 않는다.

## 기존 `runs/` 영역

기존 전역 `runs/`는 deprecated migration pointer로만 유지한다. 새 연구 데이터는 각 연구의 `studies/<연구>/machine/` 아래에 저장한다.

## 현재 실행 상태

현재는 **후보군·성장설계 재동결 / 실행 gate 재검증 필요 / 실행 미승인** 단계다.

- 공식/대규모 연구 실행: 미승인
- 28,188 scenario 1연구 batch: 미실행
- study ID: 동결
- generator 후보군 및 성장 grid: 갱신
- 실제 run ID: 미생성
- 실제 manifest: 미생성
- 결과 파일: 없음
- Moran/SBS/Liberalio 재검증: 필요

사용자의 별도 명시 승인 전에는 공식/대규모 batch를 실행하지 않는다.

## 과거 자료

```text
../archive/README.md
../archive/pre-revalidation-2026-09-05/
```

과거 케이스 스터디, Secondary anchor 초안, 공식 v1 설계, 폐기된 공식 결과는 역사·감사·가설 출처 확인용으로만 사용한다.
