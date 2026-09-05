# Crown–Mast Engine 연구 인수인계 — 2026-09-05

이 문서는 `research/14-burst-baseline`에서 Crown–Mast 연구를 **전면 재검증 후 재시작**하기 위한 최신 인계문서다.

## 0. 현재 상태

기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`과 29,952 scenario 결과는 **폐기 / superseded** 상태다.

과거 자료는 삭제하지 않고 다음 archive로 격리했다.

```text
archive/pre-revalidation-2026-09-05/
```

과거 결과는 provenance·회귀·역사 확인에만 사용한다. 새 연구의 결론·목표값·사전 기대값·파라미터 조정 근거로 사용하지 않는다.

현재 공용 전투 규칙과 다수 캐릭터는 재검증이 상당 부분 진행됐지만, 모든 캐릭터를 동일한 수준의 검증 완료 상태로 보지는 않는다.

2026-09-05 기준 주요 교정:

- generic boss DEF 기본값 12,000
- Min Firing Rounds Adjustment ON 기준 SMG 24 pulls/s
- Rapi: Red Hood B3 2808% packet의 잘못된 120 normal attack 선행 조건 제거
- Liberalio B3 1.1초 landing delay + Full Burst eligibility 반영
- 검증된 표준 캐릭터의 reload input을 표시 재장전시간 기반 raw body frame으로 정규화
- 전체 regression 302 tests 통과
- 추적 중이던 `__pycache__`/`.pyc` 제거 및 `.gitignore` 추가

세부 재장전 근거는 `docs/RELOAD_TIMING_AUDIT_2026-09-05.md`, 남은 불확실성과 연구 gate는 `docs/OPEN_MODEL_RISKS_2026-09-05.md`를 따른다.

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
docs/RELOAD_TIMING_AUDIT_2026-09-05.md
docs/OPEN_MODEL_RISKS_2026-09-05.md
research_results/README.md
research_results/RESEARCH_STATUS_2026-09-05.md
```

과거 자료가 필요할 때만:

```text
archive/README.md
archive/pre-revalidation-2026-09-05/
```

## 3. 현재 open-model gate

모든 미해결 항목을 해결할 때까지 연구 전체를 중지하지 않는다. 대신 **전역 blocker와 캐릭터별 blocker를 분리**한다.

### 전역 비차단 / 조건부 비차단

- **Mast Hit Rate Down**: baseline 직접 normal-damage loss는 0 유지. 0~22%/stack의 가혹한 proxy 진단에서도 대표 standard/RAID14/Cinderella/CCW 조건의 승패가 뒤집히지 않았다. 경계 근처 결과만 별도 sensitivity 확인한다.
- **100% 초과 reload speed**: Crown 44.35% + Mast 3 stack 45.12% = 89.47%이므로 현행 기본 연구만으로 cap에 닿지 않는다. Cube/Anchor/추가 reload buffer를 넣으면 다시 blocker로 연다.
- **공용 post-reload 미세 지연**: 검증된 표준 캐릭터에는 추가 공용값을 발명하지 않는다.
- **차지 마지막 탄 recovery/reload overlap**: Helm 시간 대조와 맞는 현행 직렬 처리 유지.
- **Raid DEF exact 단일값**: 새 연구가 상대 손익 탐색인 동안에는 여러 DEF 조건을 명시적 민감도 축으로 두어 처리할 수 있다.

### 캐릭터별 blocker

다음 캐릭터는 reload/recovery timing의 독립 근거가 충분하지 않아 **verified-core Wave A에서 제외**한다.

```text
Scarlet: Black Shadow
Raven
Liberalio
Moran (Favorite Item)
```

Milk: Blooming Bunny는 AUTO-only 연구 구현이므로 첫 verified-core 표본 범위 밖으로 둔다.

이 캐릭터들의 구현을 삭제하거나 임의 수정하지 않는다. diagnostic 사용은 허용하되 timing 문제 해결 전에는 verified aggregate에 합치지 않는다.

## 4. 다음 연구 실행 전 필수 단계

### A. verified-core 연구 범위 동결

현재 재검증이 완료된 캐릭터에서 Wave A 후보를 새로 선정한다.

- unresolved actor가 후보 생성에 들어가지 않도록 preflight gate를 둔다.
- 후보군은 과거 29,952 study의 roster list를 관성적으로 재사용하지 않는다.
- Wave A 결과는 '검증 완료 범위의 변수 탐색'으로 해석하며 전체 캐릭터 보편 결론으로 확대하지 않는다.

### B. 방어력 축 검증

기존 폐기 연구는 `boss_def=140` 단일 기준이었다.

새 연구에서는 하나의 universal exact DEF를 전제하기보다 목적에 맞는 명시적 민감도 축을 우선 검토한다.

예시 개념:

```text
low DEF
representative raid DEF
high DEF
```

현재 generic baseline은 12,000이다. 실제 Solo Raid 특정 보스의 절대 피해를 재현한다고 주장하려면 별도의 exact DEF 근거가 필요하다.

방어력은 `effective_atk - boss_def_now`에 직접 들어가므로 성장 수준과 캐릭터별 공격력 차이에 따라 팀 딜 지분과 상대 운용 손익을 바꿀 수 있다. 따라서 정식 탐색 변수 후보로 취급한다.

### C. 연구 설계 재동결

verified-core 범위와 DEF 설계 이후에만 아래를 동결한다.

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

### D. unresolved actor 재진입

Wave A 이후 SBS / Raven / Liberalio / Moran FI는 각자 timing 근거가 확보되는 순서대로 별도 검증한다.

각 캐릭터는 재검증을 통과한 뒤에만 Wave A 설계에 재진입시킨다. 재진입 전 결과는 verified aggregate와 혼합하지 않는다.

## 5. 신데렐라 anomaly watch

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
2. 여러 DEF 조건에서도 독립적으로 이상치 재현
3. 성장/core/우월/Secondary 변화에서도 다른 Main 대비 구조적 차이가 반복됨

그때만 버스트 집중도, Mast 당김 구간 gain, 다음 cycle M3 상실 offset, 인접 cycle 상쇄 같은 가설을 별도 연구에서 검증한다.

재현되지 않으면 과거 신데렐라 관찰은 폐기 자료로 끝낸다.

## 6. 흑련 / 헬름 등 과거 관찰의 취급

과거 흑련 케이스 스터디, 헬름과 스화의 opportunity-cost 역전 등은 archive에 보존한다.

이 자료는 새 연구의 결과를 예측하는 결론으로 사용하지 않는다. 새 연구에서 같은 현상이 다시 독립적으로 나타날 때만 후속 질문을 만드는 역사적 참고자료로 쓴다.

특히 Scarlet: Black Shadow는 현재 캐릭터별 timing blocker이므로 Wave A의 검증 표본에는 넣지 않는다.

## 7. archive 구조

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

## 8. 금지사항

- 기존 29,952건의 승패 비율, `g`, `l`, break-even을 새 연구 기준으로 사용하지 않기
- 과거 결과가 재현되도록 엔진을 조정하지 않기
- 신데렐라가 다시 튈 것이라고 전제하지 않기
- DEF 점유율을 실제 발생확률로 해석하지 않기
- unresolved actor를 verified aggregate에 섞지 않기
- 100% 이상 reload가 가능한 설계를 미검증식으로 실행하지 않기
- 새 설계 동결 전에 대규모 batch 실행하지 않기
- `main` 수정/병합하지 않기

## 9. 다음 단일 체크포인트

**verified-core Wave A의 B1 / Main / Secondary 후보군과 성장 / core / 우월 / DEF 축을 다시 설계하고 preflight gate를 고정한다.**

그 다음 scenario 수와 새 study ID를 확정한다. 새 대규모 batch는 그 이후 사용자 명시 승인 단계다.
