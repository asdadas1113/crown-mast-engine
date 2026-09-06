# Crown–Mast Engine 연구 인수인계 — 2026-09-05

이 문서는 `research/14-burst-baseline`에서 Crown–Mast 연구를 **전면 재검증 후 재시작**하기 위한 최신 인계문서다.

## 0. 현재 상태

기존 공식 연구 1 `crown-mast-secondary-opportunity-v1`과 29,952 scenario 결과는 **폐기 / superseded** 상태다.

과거 자료는 삭제하지 않고 다음 archive로 격리했다.

```text
archive/pre-revalidation-2026-09-05/
```

과거 결과는 provenance·회귀·역사 확인에만 사용한다. 새 연구의 결론·목표값·사전 기대값·파라미터 조정 근거로 사용하지 않는다.

현재 공용 전투 규칙과 Wave A verified-core 후보는 재검증이 상당 부분 진행됐지만, 모든 캐릭터를 동일한 수준의 검증 완료 상태로 보지는 않는다.

2026-09-05 기준 주요 교정:

- generic boss DEF 기본값 12,000
- Min Firing Rounds Adjustment ON 기준 SMG 24 pulls/s
- Rapi: Red Hood B3 2808% packet의 잘못된 120 normal attack 선행 조건 제거
- Liberalio B3 1.1초 landing delay + Full Burst eligibility 반영
- 검증된 표준 캐릭터의 reload input을 표시 재장전시간 기반 raw body frame으로 정규화
- Mast Hit Rate Down을 검증되지 않은 동일 비율 직접 normal-damage loss로 치환하지 않음
- 추적 중이던 `__pycache__`/`.pyc` 제거 및 `.gitignore` 추가

최종 Wave A preflight validation:

```text
Wave A focused tests: 8 / 8 passed
full regression: 310 / 310 passed
active temporary workflow: 없음
tracked __pycache__: 없음
```

세부 재장전 근거는 `docs/RELOAD_TIMING_AUDIT_2026-09-05.md`, 남은 불확실성과 연구 gate는 `docs/OPEN_MODEL_RISKS_2026-09-05.md`, Wave A 설계는 `research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md`를 따른다.

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
research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md
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
- **100% 초과 reload speed**: Crown 44.35% + Mast 3 stack 45.12% = 89.47%이므로 현행 Wave A만으로 cap에 닿지 않는다. Cube/Anchor/추가 reload buffer를 넣거나 추가 reload-speed source 캐릭터를 넣으면 다시 blocker로 연다.
- **공용 post-reload 미세 지연**: 검증된 표준 캐릭터에는 추가 공용값을 발명하지 않는다.
- **차지 마지막 탄 recovery/reload overlap**: Helm 시간 대조와 맞는 현행 직렬 처리 유지.
- **Raid DEF exact 단일값**: 새 연구가 상대 손익 탐색인 동안에는 여러 DEF 조건을 명시적 민감도 축으로 두어 처리한다.

### 캐릭터별 blocker / 범위 제한

첫 verified-core Wave A aggregate에서 제외:

```text
Scarlet: Black Shadow
Raven
Liberalio
Moran (Favorite Item)
Quency: Escape Queen
Milk: Blooming Bunny
```

- SBS / Raven / Liberalio / Moran FI: reload/recovery timing 또는 source conflict unresolved.
- Quency: skill 값은 확인됐지만 hit/spread가 실제 normal/core DPS에 크게 영향을 주는 캐릭터이고, 현행 엔진은 weapon spread/body miss를 모델링하지 않는다.
- Milk BB: AUTO-only 연구 구현이며 수동/특수 reload route는 범위 밖이다.

이 캐릭터들의 구현을 삭제하거나 임의 수정하지 않는다. diagnostic 사용은 허용하되 해당 이슈 해결 전에는 verified aggregate에 합치지 않는다.

## 4. Wave A verified-core 설계

### 후보군

B1 4명:

```text
liter
anis-star
little-mermaid
rapi-red-hood
```

Main B3 6명:

```text
rapi-red-hood
cinderella
cinderella-crystal-wave
neon-vision-eye
phantom
bready
```

Secondary B3 3명:

```text
epinel
helm
snow-white-heavy-arms
```

Raw roster 72개에서 Rapi B1 + Rapi Main 중복 3개를 제외해 **69 valid rosters**다.

### 성장 screening

기존 realistic-v3의 4수준 성장 정의는 유지하되 B1/Main/Secondary 4×4×4=64 완전교차 대신 **16점 pairwise OA**를 1차 screening에 사용한다.

```text
B1 = i
Main = j
Secondary = (i + j) mod 4
```

각 역할 쌍의 4×4 성장 조합은 정확히 한 번씩 포함한다. 순수 3-way interaction은 완전히 식별하지 않으므로 sign reversal / close-call / 이상치가 나온 roster만 64점 full growth grid로 확대한다.

### 환경축

```text
DEF: 140 / 12,000 / 31,784
core: 0% / 100%
Main advantage: off / on
```

3×2×2 = **12 environment conditions**를 완전교차한다.

- 140: low/training-range sensitivity anchor
- 12,000: generic raid representative baseline
- 31,784: 현재 DILDORO Solo Raid 설정에서 확인되는 high/Solo-style sensitivity anchor

세 값 모두 발생확률이 아니며 31,784를 universal exact Solo Raid DEF로 주장하지 않는다.

### Wave A1 총량

```text
69 valid rosters × 16 growth OA × 12 environment = 13,248 scenarios
```

현재 `crown_mast_engine/wave_a_study.py`는 **case generation과 preflight gate만 구현**돼 있다. 13,248개 simulation batch는 아직 실행하지 않았다.

## 5. Preflight gate

`wave_a_study.py` / `tests/test_wave_a_study.py`에서 다음을 fail-closed로 확인한다.

- unresolved actor가 verified-core allowlist에 들어오지 않음
- duplicate actor roster 제외
- 16점 OA가 역할 쌍별 모든 4×4 조합을 정확히 한 번씩 포함
- DEF/core/advantage label과 실제 `CombatSettings` 일치
- 현재 allowlist에 Crown/Mast 외 추가 reload-speed skill source 없음
- modeled reload ceiling 89.47% < 100%
- 69 roster / 192 scenarios per roster / 13,248 total 산술 일치
- case ID 유일성
- draft / explicit approval required 상태 유지

최종 validation은 focused 8 tests와 전체 310 tests 모두 통과했다.

## 6. Wave A2 확대 조건

다음 중 하나면 해당 roster/환경을 64점 full growth grid로 확대한다.

1. 16 growth point 사이에서 Conventional/Funnel 방향이 뒤집힘
2. DEF 수준 변화로 정책 방향이 뒤집힘
3. core 또는 advantage 변화로 정책 방향이 뒤집힘
4. 상대 변화량 절대값 0.5% 이내 close-call 존재
5. 같은 Main/Secondary 계열 대비 반복적으로 튀는 이상치
6. pairwise screening으로 설명되지 않는 비선형 패턴 의심

0.5%는 승패 정의가 아니라 보수적 재검증 trigger다.

## 7. unresolved actor 재진입

Wave A 이후 보류 캐릭터는 각자 timing/hit-model 근거가 확보되는 순서대로 별도 검증한다.

재검증을 통과한 뒤에만 Wave A 설계에 재진입시키며, 재진입 전 결과는 verified aggregate와 혼합하지 않는다.

## 8. 신데렐라 anomaly watch

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

재현되지 않으면 과거 신데렐라 관찰은 폐기 자료로 끝낸다.

## 9. 과거 관찰의 취급

과거 흑련 케이스 스터디, 헬름과 스화의 opportunity-cost 역전 등은 archive에 보존한다.

이 자료는 새 연구의 결과를 예측하는 결론으로 사용하지 않는다. 새 연구에서 같은 현상이 다시 독립적으로 나타날 때만 후속 질문을 만드는 역사적 참고자료로 쓴다.

특히 Scarlet: Black Shadow는 현재 캐릭터별 timing blocker이므로 Wave A 검증 표본에는 넣지 않는다.

## 10. 금지사항

- 기존 29,952건의 승패 비율, `g`, `l`, break-even을 새 연구 기준으로 사용하지 않기
- 과거 결과가 재현되도록 엔진을 조정하지 않기
- 신데렐라가 다시 튈 것이라고 전제하지 않기
- DEF 점유율을 실제 발생확률로 해석하지 않기
- unresolved actor를 verified aggregate에 섞지 않기
- 100% 이상 reload가 가능한 설계를 미검증식으로 실행하지 않기
- 사용자 명시 승인 전 13,248-scenario Wave A1 batch 실행하지 않기
- `main` 수정/병합하지 않기

## 11. 다음 단일 체크포인트

**Wave A 설계를 최종 동결할지 사용자 판단을 받는다.**

승인 시에만:

1. 새 study ID 확정
2. engine / skill hook / catalog / timeline provenance 동결
3. run 저장구조와 manifest 필드 동결
4. 13,248-scenario Wave A1 batch 실행

승인 전에는 case generator와 gate까지만 유지한다.
