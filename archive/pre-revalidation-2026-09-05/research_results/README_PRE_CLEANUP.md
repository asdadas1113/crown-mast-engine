# Crown–Mast 연구 결과 / 현재 상태

## 먼저 읽을 것

2026-09-05 현재 기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`은 **폐기 / superseded** 상태다.

기존 29,952 scenario raw와 집계 결과는 삭제하지 않지만 **새 연구 1의 결론, 사전 기대값, 목표값으로 참고하지 않는다.** 감사·회귀 비교·역사적 기록용으로만 보존한다.

Canonical status:

```text
research_results/RESEARCH_STATUS_2026-09-05.md
research_results/runs/official-complete-2026-09-05/SUPERSEDED_DO_NOT_USE.md
docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md
```

새 작업을 시작할 때는 위 문서를 먼저 읽는다.

---

## 현재 연구 1 상태

기존 공식 배치는 완료됐었지만, 연구 1을 **처음부터 재시작**하기로 결정했다.

재시작 이유:

1. 엔진을 다시 독립 검증한다.
2. 기존 공식 grid는 `boss_def=140` 단일 방어력 기준이었다.
3. 실제 레이드 방어력 수준을 포함하는 방어력 민감도 검증이 빠져 있었다.
4. 따라서 기존 결과를 새 결론으로 승계하지 않고, 재검증된 엔진과 새 설계로 raw부터 다시 만든다.

다음 공식 batch 전 순서:

```text
엔진 재검증
-> 방어력 공식/레이드 대표값 검증
-> 방어력 축 포함 연구 설계 재동결
-> 새 study ID / revision 확정
-> 사용자 명시 승인
-> 새 공식 raw 실행
```

---

## 기존 결과의 취급

기존 결과 디렉터리:

```text
research_results/runs/official-complete-2026-09-05/
```

이 자료는 다음 용도로만 사용한다.

- provenance 감사
- 이전 엔진과 새 엔진의 회귀 비교
- 연구 이력 보존

다음은 금지한다.

- 기존 승패 비율을 새 연구 결론으로 인용
- 기존 Main별 `g`, `l`, break-even을 새 연구 목표값으로 사용
- 새 결과와 기존 29,952개 결과를 합산
- 기존 결과가 재현되도록 엔진/파라미터를 조정

---

## 신데렐라 anomaly watch

기존 폐기 연구에서 신데렐라는 다른 Main 대비 유독 큰 몰아주기 반응을 보였고, 별도 역할반전 탐색에서도 강한 비대칭이 관찰됐다.

이 관찰은 **결론으로 승계하지 않는다.**

다만 재검증 시 놓치지 않도록 신데렐라를 **우선 감시 대상(anomaly watch)** 으로 둔다.

확인할 내용:

- 엔진 재검증 후에도 이상치가 재현되는가
- `boss_def=140`과 새 레이드 방어력 조건 모두에서 유독 튀는가
- core / 우월 / 성장 / Secondary 조건을 바꿔도 구조적 차이가 유지되는가

**엔진 재검증 + 방어력 축 포함 새 연구 1에서도 독립적으로 다시 이상치가 나타날 때만** 시간축 / 버스트 집중도 / 인접 사이클 상쇄를 별도 후속 기전 연구로 넘긴다.

재현되지 않으면 기존 신데렐라 관찰은 폐기 연구의 과거 결과로만 남긴다.

---

## 독립 진단 / 케이스 스터디

### 흑련 몰아주기 반응 케이스 스터디

```text
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

흑련의 인접 사이클 상쇄 등 기존 메커니즘 진단은 감사·가설 생성 자료로 보존한다. 그러나 새 연구 1의 결과를 미리 설명하는 결론으로 사용하지 않는다.

### 헬름 / Secondary 관련 기존 관찰

기존 폐기 연구에서는 Secondary 개인 딜 지분과 rest-of-team opportunity loss가 단순 비례하지 않는 현상이 있었다. 헬름의 팀 버프 구조가 가능한 설명 후보지만, 새 연구에서 재현되기 전에는 확정 기전으로 취급하지 않는다.

---

## 과거 설계 문서

기존 설계와 구현 이력은 다음 문서에 남아 있다.

```text
research_results/OFFICIAL_STUDY_DESIGN_V1.md
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

이 문서들은 **과거 설계/감사 정보**로 사용하고, 새 연구 1의 frozen design으로 간주하지 않는다.

---

## 운영 원칙

1. `main`은 사용자 명시 지시 없이 수정/병합하지 않는다.
2. 엔진 재검증 전에 새 대규모 공식 batch를 실행하지 않는다.
3. 레이드 방어력 값은 외부 근거를 검증한 뒤 exact value를 동결한다.
4. 각 deterministic grid point를 실전 발생확률로 해석하지 않는다.
5. 기존 폐기 결과와 새 결과의 provenance를 완전히 분리한다.
6. 예상 밖 이상치는 먼저 재현성을 확인하고, 재현된 뒤에만 별도 기전 연구로 승격한다.
