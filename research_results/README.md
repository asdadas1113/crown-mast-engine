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
../docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md
../docs/SOURCE_VALIDATION_POLICY.md
studies/README.md
studies/01_exploratory/human/01_연구_설계_초안.md
studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
studies/01_exploratory/validation/01_연구_인프라_보강_검증_2026-09-06.md
studies/01_exploratory/validation/02_저장소_정리_점검_2026-09-06.md
```

## 새 연구 저장 원칙

새 연구는 앞으로 `studies/` 아래에서 **연구 단위로 완전히 분리**한다.

```text
studies/
├─ 01_exploratory/
│  ├─ human/
│  ├─ machine/
│  └─ validation/
├─ 02_.../
│  ├─ human/
│  ├─ machine/
│  └─ validation/
└─ ...
```

- `human/`: 사람이 읽는 한글 연구 문서
- `machine/`: manifest, scenario, raw, aggregate, provenance 등 기계용 실행 데이터
- `validation/`: 해당 연구에 귀속되는 표본 검증, 민감도 점검, 이상치 재현, focused regression 기록

프로젝트 전체 엔진의 pytest 테스트 코드는 루트 `tests/`에 유지한다. 연구별 `validation/`은 특정 연구의 검증 산출물을 보관한다.

## 1연구의 역할

1연구는 보편적인 단일 임계값이나 최적 운용 규칙을 확정하는 것이 아니라, **대표적인 Crown/Mast 통제 조건에서 광범위한 조합을 탐색하고 우세 경향과 예외를 동시에 찾은 뒤 후속 연구 후보를 고르는 단계**다.

현재 canonical 설계는 다음 문서다.

```text
studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

동결된 study ID:

```text
crown-mast-study-01-exploratory-v1
```

동결된 A1 설계:

- 69 verified-core rosters
- B1/Main/Secondary 16-point pairwise growth screening
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 192 scenarios
- 전체 13,248 scenarios
- Crown/Mast OL5 + SR15 대표 build 고정
- 애장품 캐릭터 SR15 canonical floor

결과가 반복적으로 튀는 캐릭터/조건은 anomaly candidate로 표시하되, 엔진 재검증과 복수 환경에서 재현되기 전에는 기전 설명을 확정하지 않는다.

## 기존 `runs/` 영역

기존 전역 `runs/`는 과거 active 구조의 흔적으로 남아 있다. 앞으로 승인되는 새 연구 실행은 전역 `runs/`에 저장하지 않고 각 연구의 `studies/<연구>/machine/` 아래에 저장한다.

`runs/`는 기존 링크 호환을 위한 deprecated pointer로만 유지한다.

## 현재 실행 상태

현재는 **설계 동결 / 실행 미승인** 단계다.

- 공식/대규모 연구 실행: 미승인
- 13,248 scenario 1연구 A1 batch: 미실행
- study ID: `crown-mast-study-01-exploratory-v1`로 동결
- 실제 run ID: 미생성
- 실제 manifest: 미생성
- 결과 파일: 없음

현재 `crown_mast_engine/wave_a_study.py`의 case generator는 아직 과거 draft ID를 사용한다. 따라서 실제 실행 전에는 generator 식별자를 동결 study ID와 정렬하고 기존 invariant를 다시 검증해야 한다.

사용자의 별도 명시 승인 전에는 공식/대규모 batch를 실행하지 않는다.

## 과거 자료

```text
../archive/README.md
../archive/pre-revalidation-2026-09-05/research_results/
```

과거 케이스 스터디, Secondary anchor 초안, 공식 v1 설계, 폐기된 공식 결과는 역사·감사·가설 출처 확인용으로만 사용한다.
