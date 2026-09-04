# Crown–Mast Engine 연구 인수인계 — 2026-09-05

이 문서는 `research/14-burst-baseline`에서 Crown–Mast 연구를 **전면 재검증 후 재시작**하기 위한 최신 인계문서다.

## 0. 현재 상태

기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`과 29,952 scenario 결과는 **폐기 / superseded** 상태다.

과거 자료는 삭제하지 않고 다음 archive로 격리했다.

```text
archive/pre-revalidation-2026-09-05/
```

과거 결과는 provenance·회귀·역사 확인에만 사용한다. 새 연구의 결론·목표값·사전 기대값·파라미터 조정 근거로 사용하지 않는다.

현재 `crown_mast_engine/`과 `tests/`는 신뢰 완료 상태가 아니라 **재검증 대상 코드**다.

## 1. 새 연구 1의 성격

새 연구 1은 하나의 확정적 최적 운용 규칙을 도출하는 연구가 아니다.

주목적:

> Crown/Mast 운용 손익을 실제로 움직이는 유의미한 변수, 상호작용, 재현되는 이상치 후보를 탐색한다.

따라서 결과물은 다음을 중심으로 정리한다.

1. 영향이 큰 변수
2. 영향이 작은 변수
3. 변수 간 상호작용
4. 조건 변화에서 우세 방향이 뒤집히는 영역
5. 반복적으로 튀는 이상치 후보
6. 후속 기전 연구로 넘길 질문

승패 grid 점유율을 실전 승률이나 보편 규칙으로 해석하지 않는다.

## 2. 재개 시 먼저 할 것

1. `research/14-burst-baseline` 최신 HEAD 확인
2. `main` 수정/병합 금지
3. 과거 archive 수치를 새 연구 판단에 사용하지 않음
4. 아래 현행 문서를 읽음

```text
README.md
docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/RESEARCH_STATUS_2026-09-05.md
```

과거 자료가 필요할 때만:

```text
archive/README.md
archive/pre-revalidation-2026-09-05/
```

## 3. 다음 연구 실행 전 필수 단계

### A. 엔진 전면 재검증

최소 검증 항목:

- Crown / Mast buff 적용 규칙
- Conventional / sustained funnel rotation
- RAID14 180초 시간축과 각 B1/B2/B3 입력 시점
- Main / Secondary 역할별 Mast stack 배치
- damage category별 Mast 적용
- distributed / sequential / sustained / projectile bucket
- attack / max HP / HP→ATK 변환
- core / element advantage / full burst / crit / range 배율
- boss DEF와 DEF 증감 처리
- ammo / reload / charge cadence
- 캐릭터별 source / cycle 단위 damage

가능하면 Moris, 공식/직접 자료, 독립 계산기 또는 수동 산식으로 교차검증한다.

### B. 방어력 축 검증

기존 폐기 연구는 `boss_def=140` 단일 기준이었다.

새 연구에서는 최소 다음 두 조건을 검토한다.

```text
DEF 140      -> 기존 사격장 계열 기준
Raid DEF     -> 외부 근거를 재확인한 실제 레이드 대표값
```

필요하면 low / representative / high raid DEF로 확장한다. exact value는 출처 검증 전 임의로 고정하지 않는다.

방어력은 `effective_atk - boss_def_now`에 직접 들어가므로 성장 수준과 캐릭터별 공격력 차이에 따라 팀 딜 지분과 상대 운용 손익을 바꿀 수 있다. 따라서 정식 탐색 변수 후보로 취급한다.

### C. 연구 설계 재동결

엔진/DEF 검증 이후에만 아래를 동결한다.

- B1 후보
- Main 후보
- Secondary 후보
- 성장 격자
- core 축
- 우월 축
- DEF 축
- scenario 수
- 새 study ID
- engine / skill hook revision

그 뒤 사용자 명시 승인 후 새 raw를 처음부터 생성한다.

## 4. 신데렐라 anomaly watch

과거 폐기 연구에서 신데렐라가 유독 큰 반응을 보였다는 사실은 **새 연구의 증거로 사용하지 않는다**.

다만 재검증에서 놓치지 않기 위한 감시 대상이다.

재검증 항목:

- HP→ATK 변환
- Beautiful stack 시간축
- 자기 B3 sequential burst packet
- 완충 추가타
- 특수 RL charge/reload cadence
- Mast가 위 source에 들어가는 damage bucket
- Main B3 사이클과 다음 Secondary B3 사이클의 source별 변화

새 연구에서도 다음 조건이 동시에 만족될 때만 후속 기전 연구로 넘긴다.

1. 엔진 재검증 통과
2. DEF 140뿐 아니라 레이드 DEF 조건에서도 독립적으로 이상치 재현
3. 성장/core/우월/Secondary 변화에서도 다른 Main 대비 구조적 차이가 반복됨

그때만 버스트 집중도, Mast 당김 구간 gain, 다음 cycle M3 상실 offset, 인접 cycle 상쇄 같은 가설을 별도 연구에서 검증한다.

재현되지 않으면 과거 신데렐라 관찰은 폐기 자료로 끝낸다.

## 5. 흑련 / 헬름 등 과거 관찰의 취급

과거 흑련 케이스 스터디, 헬름과 스화의 opportunity-cost 역전 등은 archive에 보존한다.

이 자료는 새 연구의 결과를 예측하는 결론으로 사용하지 않는다. 새 연구에서 같은 현상이 다시 독립적으로 나타날 때만 후속 질문을 만드는 역사적 참고자료로 쓴다.

## 6. archive 구조

```text
archive/pre-revalidation-2026-09-05/
  docs/
    handoffs/
    audits/
    raid14/
    plans/
  research_results/
    designs/
    diagnostics/
    runs/
  scripts/
  workflows/
  MANIFEST.sha256
```

과거 GitHub Actions workflow는 `.github/workflows`에서 제거해 자동/수동 실행 대상으로 보이지 않게 한다.

과거 study/benchmark 실행 스크립트도 active `scripts/`에서 archive로 이동한다.

## 7. 금지사항

- 기존 29,952건의 승패 비율, `g`, `l`, break-even을 새 연구 기준으로 사용하지 않기
- 과거 결과가 재현되도록 엔진을 조정하지 않기
- 신데렐라가 다시 튈 것이라고 전제하지 않기
- 레이드 DEF를 검증 없이 임의 확정하지 않기
- 엔진 재검증 전에 새 대규모 공식 batch 실행하지 않기
- `main` 수정/병합하지 않기

## 8. 다음 단일 체크포인트

**엔진 재검증 계획과 독립 대조 항목을 확정하고, 레이드 DEF exact value의 근거를 검증한다.**

새 공식 batch는 그 이후 별도 승인 단계다.
