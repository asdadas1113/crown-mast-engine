# Crown–Mast Research Engine

NIKKE의 Crown + Mast: Romantic Maid 운용을 통제 조건에서 비교하기 위한 개인 연구용 엔진이다.

## 현재 상태 — 2026-09-05

기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`과 그 29,952개 결과는 **폐기 / superseded** 상태다.

기존 결과는 새 연구의 결론·목표값·사전 기대값으로 사용하지 않는다. 과거 자료는 모두 다음 archive 아래에 격리한다.

```text
archive/pre-revalidation-2026-09-05/
```

현재 작업은 **새 연구를 돌리는 단계가 아니라 엔진 전면 재검증 단계**다.

## 앞으로의 연구 1 목적

새 연구 1은 하나의 보편적 최적 운용 규칙을 확정하는 연구가 아니다.

주목적은 다음과 같다.

> Crown/Mast 운용의 상대 손익을 실제로 움직이는 유의미한 변수와 상호작용, 재현되는 이상치 후보를 탐색한다.

따라서 연구 1의 핵심 산출물은 다음이다.

- 결과를 크게 움직이는 강한 변수
- 영향이 작은 변수
- `Main × Secondary`, `Main × DEF` 같은 상호작용
- 후속 기전 연구가 필요한 재현성 있는 이상치

승패 점유율을 실전 승률이나 보편 규칙으로 해석하지 않는다.

## 재시작 순서

1. 엔진 및 캐릭터 메커니즘 독립 재검증
2. damage formula와 방어력 처리 검증
3. 사격장 계열 `DEF=140`과 검증된 실제 레이드 방어력 수준을 포함한 방어력 축 설계
4. B1 / Main / Secondary / 성장 / core / 우월 / DEF 변수 재동결
5. 새 study ID와 새 revision 확정
6. 사용자 명시 승인 후 새 raw를 처음부터 실행
7. 결과에서 유의미한 변수와 재현 이상치를 선별
8. 필요한 경우에만 별도 후속 기전 연구로 분리

## 신데렐라 anomaly watch

과거 폐기 연구에서 신데렐라가 유독 튀는 결과를 보였다는 사실은 **새 연구의 증거로 사용하지 않는다**.

다만 재검증 과정에서 놓치지 않기 위한 감시 대상으로만 둔다.

재검증된 엔진과 방어력 축을 포함한 새 연구에서도 독립적으로 다시 이상치가 재현될 때만, 버스트 집중도·인접 사이클 상쇄 등의 가설을 별도 후속 연구로 넘긴다.

## 현재 읽을 문서

```text
docs/CURRENT_RESEARCH_HANDOFF.md
docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/RESEARCH_STATUS_2026-09-05.md
```

과거 자료 인덱스:

```text
archive/README.md
```

## 코드 취급

`crown_mast_engine/`과 `tests/`는 archive하지 않는다. 이 코드는 새 연구의 신뢰 근거가 아니라 **재검증 대상**이다.

기존 `official_study.py` 등 연구 생성 코드도 재검증/재설계 전에는 새 공식 batch에 사용하지 않는다.

## 운영 원칙

- `main`은 사용자 명시 지시 없이 수정하거나 병합하지 않는다.
- 엔진 재검증 전에 새 대규모 공식 batch를 실행하지 않는다.
- 레이드 DEF는 출처를 검증해 exact value를 동결하기 전까지 임의 확정하지 않는다.
- 과거 폐기 결과가 재현되도록 엔진이나 파라미터를 조정하지 않는다.
- 각 deterministic grid point를 실전 발생확률로 해석하지 않는다.
