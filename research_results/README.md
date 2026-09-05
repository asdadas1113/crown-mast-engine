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

주요 탐색 후보:

- Main B3 identity
- Secondary B3 identity
- B1/Main/Secondary 성장 격차
- core 조건
- 우월 조건
- boss DEF
- Main 딜 구조와 정책 반응의 연관 후보
- 위 변수들의 상호작용

현재 Crown/Mast 성장치는 1연구에서 대표 조건으로 통제한다. Crown/Mast 상대 성장 변화에 대한 일반화는 후속 연구 대상으로 남긴다.

애장품 캐릭터는 실전 사용 전제를 반영해 **모든 성장 프로필에서 SR15를 canonical floor로 고정**한다.

결과가 반복적으로 튀는 캐릭터/조건은 anomaly candidate로 표시하되, 엔진 재검증과 복수 환경에서 재현되기 전에는 기전 설명을 확정하지 않는다.

## 기존 `runs/` 영역

기존 전역 `runs/`는 과거 active 구조의 흔적으로 남아 있다. 앞으로 승인되는 새 연구 실행은 전역 `runs/`에 저장하지 않고 각 연구의 `studies/<연구>/machine/` 아래에 저장한다.

새 연구 설계가 아직 최종 동결되지 않았으므로 과거 run schema를 현행 표준으로 간주하지 않는다.

## 현재 실행 상태

현재는 **문서와 저장 구조를 준비하는 단계**다.

- 공식/대규모 연구 실행 미승인
- 13,248 scenario Wave A1 batch 미실행
- 최종 study ID 미확정
- 최종 manifest 미작성

사용자의 명시적 승인 전에는 공식/대규모 batch를 실행하지 않는다.

## 과거 자료

```text
../archive/README.md
../archive/pre-revalidation-2026-09-05/research_results/
```

과거 케이스 스터디, Secondary anchor 초안, 공식 v1 설계, 폐기된 공식 결과는 역사·감사·가설 출처 확인용으로만 사용한다.
