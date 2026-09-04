# Crown–Mast Engine 연구 인수인계 — 2026-09-05

이 문서는 `research/14-burst-baseline`에서 Crown–Mast 연구를 재시작하기 위한 최신 인계문서다.

## 0. 가장 중요한 상태 변경

기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`은 **폐기 / superseded** 상태다.

기존 29,952 scenario raw와 후처리 결과는 삭제하지 않지만 다음 용도로만 보존한다.

- provenance 감사
- 회귀 비교
- 역사적 기록

다음 용도로는 **사용 금지**다.

- 새 연구 1의 결론
- 새 연구 1의 목표값
- 새 연구 1의 사전 기대값
- 새 연구 1의 파라미터 조정 근거
- 새 결과와의 합산

Canonical notice:

```text
research_results/runs/official-complete-2026-09-05/SUPERSEDED_DO_NOT_USE.md
research_results/RESEARCH_STATUS_2026-09-05.md
```

## 1. 재개 시 먼저 할 것

1. GitHub에서 `research/14-burst-baseline` 최신 HEAD 확인
2. `main`은 수정/병합하지 않음
3. 기존 연구 1 숫자를 결과 판단에 사용하지 않음
4. 아래 문서를 우선 읽음

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-05.md
research_results/RESEARCH_STATUS_2026-09-05.md
research_results/runs/official-complete-2026-09-05/SUPERSEDED_DO_NOT_USE.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

과거 공식 설계/결과 문서는 구조와 재현 정보 확인용으로만 읽고, 결과값을 새 연구 결론으로 승계하지 않는다.

## 2. 새 연구 1의 재시작 순서

새 공식 연구를 다시 돌리기 전에 다음을 순서대로 완료한다.

### A. 엔진 재검증

- Crown / Mast buff 적용 규칙
- Conventional / sustained funnel rotation
- 14-burst 시간축
- Main / Secondary 역할별 Mast stack 배치
- damage category별 Mast 적용
- distributed / sequential / sustained / projectile bucket
- 공격력 / 최대체력 / 공격력 변환
- core / 우월 / full burst / crit / range 배율
- 방어력 처리와 방깎/방증 처리
- ammo / reload / charge cadence
- 대표 캐릭터별 source / cycle 단위 대조

가능하면 Moris / 외부 계산기 / 수동 산식과 독립 대조한다.

### B. 방어력 축 재설계

기존 연구 1은 `CombatSettings.boss_def=140` 기본값만 사용했다.

새 연구 1에서는 방어력을 정식 민감도 축으로 검토한다.

최소 후보:

```text
DEF 140      -> 기존 기준선 / 사격장 계열 기준
Raid DEF     -> 실제 레이드 대표값, 외부 근거 재확정 후 동결
```

레이드 방어력 값은 실행 전에 출처를 다시 검증하고 exact value를 문서화한다. 필요하면 low / representative / high raid DEF로 확장하되, 임의 숫자를 먼저 고정하지 않는다.

방어력은 NIKKE damage formula에서 `effective_atk - boss_def_now`에 직접 들어가므로 캐릭터별 공격력과 성장 수준에 따라 상대 딜 지분 및 운용 손익을 바꿀 수 있다. 따라서 연구 1의 강건성 축으로 취급한다.

### C. 설계 재동결

엔진/방어력 검증 이후에만:

- B1 후보
- Main 후보
- Secondary 후보
- 성장 격자
- core 축
- 우월 축
- 방어력 축
- scenario 수
- study ID
- engine / skill hook revision

을 새로 동결한다.

그 뒤 새 raw를 처음부터 생성한다.

## 3. 신데렐라 anomaly watch

기존 폐기 연구에서 신데렐라는 다른 Main 대비 유독 큰 몰아주기 반응을 보였다. 별도 역할반전 탐색에서도 강한 비대칭이 관찰되었다.

**중요: 이 결과를 새 연구 1의 결론으로 참고하지 않는다.**

신데렐라는 단지 엔진 재검증 과정에서 놓치지 않기 위한 **우선 감시 대상(anomaly watch)** 이다.

재검증할 때 다음을 유심히 본다.

1. 신데렐라의 HP→ATK 변환
2. Beautiful stack 시간축
3. 자기 B3 sequential burst packet
4. 완충 추가타
5. 특수 RL charge/reload cadence
6. Mast buff가 위 source들에 적용되는 bucket
7. Main B3 사이클과 다음 Secondary B3 사이클의 source별 차이

새 연구 1 실행 이후에는 다음을 확인한다.

- DEF 140에서도 다시 이상치인가
- 레이드 방어력에서도 다시 이상치인가
- core / 우월 / 성장 / Secondary를 바꿔도 유독 튀는가
- 다른 Main과 비교한 상대적 `g` 또는 팀 Δ 이상치가 반복되는가

### 후속 기전 연구로 넘기는 조건

**엔진 재검증을 통과하고, 방어력 축을 포함한 새 연구 1에서도 신데렐라가 다시 독립적으로 튀는 결과를 보일 때만** 별도의 후속 연구를 연다.

그때 검토할 가설 후보:

- 자기 B3 구간의 딜 집중도
- 일반딜 대비 burst-window 딜 집중
- Mast를 앞 사이클로 당길 때의 gain
- 다음 사이클 M3 상실에 따른 offset
- 인접 cycle 상쇄

재현되지 않으면 기존 신데렐라 결과는 폐기 연구의 과거 이상치로 끝낸다.

## 4. 흑련 케이스 스터디의 취급

`research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md`는 독립 메커니즘 진단 자료로 보존한다.

여기서 확인된 인접 cycle 상쇄 개념은 새 가설을 만드는 참고 아이디어로는 사용할 수 있지만, 새 연구 1의 결과를 미리 설명하거나 신데렐라 결과를 정당화하는 근거로 사용하지 않는다.

새 연구 1에서 같은 현상이 독립적으로 관측된 뒤에만 후속 기전 연구에서 비교 대조군으로 사용한다.

## 5. 헬름 / 스노우 화이트: 헤비암즈 관련 관찰

기존 폐기 연구에서는 Secondary 개인 딜 지분과 rest-of-team opportunity loss가 단순 비례하지 않는 현상이 있었다. 헬름은 팀 버프 구조를 가지므로 가능한 설명 후보가 있지만, 이 역시 기존 연구의 결과를 새 연구 1 결론으로 승계하지 않는다.

새 연구에서 다시 비슷한 역전이 나타나면 source / actor / cycle 단위 분해를 통해 별도 검증한다.

## 6. 금지사항

- 기존 `69.21% / 26.99%` 등의 결과를 새 연구의 기준으로 사용하지 않기
- 기존 Main별 `g`, `l`, break-even을 목표값으로 사용하지 않기
- 신데렐라가 다시 몰아주기 우세일 것이라고 가정하지 않기
- 방어력 값을 검증 없이 임의 확정하지 않기
- 엔진 재검증 전에 새 공식 대규모 batch 실행하지 않기
- `main` 수정/병합하지 않기

## 7. 다음 단일 체크포인트

**엔진 재검증 설계와 독립 대조 항목을 확정하는 것.**

방어력 공식 값과 레이드 대표 DEF 출처 검증은 이 단계에 포함한다.

새 공식 batch는 그 이후 별도 승인 단계다.
