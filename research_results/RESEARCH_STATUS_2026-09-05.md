# Crown–Mast 연구 상태 — 2026-09-05

## 현재 판정

기존 `crown-mast-secondary-opportunity-v1`은 **폐기 / superseded**다.

과거 문서·결과·배치 인프라는 다음 archive로 격리했다.

```text
archive/pre-revalidation-2026-09-05/
```

과거 29,952 scenario raw와 집계는 삭제하지 않지만 새 연구의 근거, 결론, 사전 기대값으로 사용하지 않는다.

## 새 연구 1 목적

새 연구 1은 확정적인 보편 규칙을 찾는 연구보다 **유의미한 변수 탐색과 이상치 발굴**을 우선한다.

핵심 질문:

- 어떤 변수가 Crown/Mast 운용의 상대 손익을 크게 움직이는가?
- 어떤 변수는 영향이 작거나 무시 가능한가?
- `Main × Secondary`, `Main × DEF` 등 어떤 상호작용이 중요한가?
- 어떤 캐릭터/조건이 반복적으로 이상치로 나타나는가?
- 어떤 현상을 별도 기전 연구로 넘길 가치가 있는가?

연구 1의 grid 점유율은 실전 확률이나 보편적인 최적화 규칙으로 해석하지 않는다.

## 2026-09-05 재검증 체크포인트

공용 전투/캐릭터 audit에서 확인된 오류를 수정했다.

- generic boss DEF 기본값: 12,000
- SMG baseline: Min Firing Rounds Adjustment ON 기준 24 pulls/s
- Rapi: Red Hood B3 2808% packet의 잘못된 120 normal attack 선행 조건 제거
- Liberalio B3: 1.1초 landing delay 및 Full Burst eligibility 반영
- 표준 reload 입력을 인게임 표시시간 기반 raw body frame으로 정규화
- Mast Hit Rate Down을 검증되지 않은 동일 비율 직접 normal-damage loss로 치환하지 않음

최종 Wave A preflight validation에서 다음을 확인했다.

```text
Wave A focused tests: 8 / 8 passed
full regression: 310 / 310 passed
tracked Python bytecode: 제거 완료
.gitignore: __pycache__ / *.py[cod] / .pytest_cache 차단
active temporary workflow: 없음
```

재장전 세부 교차검증은 `docs/RELOAD_TIMING_AUDIT_2026-09-05.md`, 남은 모델 불확실성과 연구 gate는 `docs/OPEN_MODEL_RISKS_2026-09-05.md`를 기준으로 한다.

## 미해결 항목의 현재 처리

모든 미해결 항목이 연구 전체를 막지는 않는다.

### 전역 비차단 또는 조건부 비차단

- Mast Hit Rate Down: 직접 normal-damage loss 기본값 0 유지. 0~22%/stack 진단에서도 대표 조건의 승패가 뒤집히지 않았으므로 탐색 연구 전체 blocker로 보지 않는다.
- 100% 초과 reload speed: 현재 Crown+Mast 자체 최대 89.47%이며 현재 성장축에도 추가 reload option이 없다. 모든 설계점이 100% 미만인 동안 비차단이다.
- 공용 post-reload 미세지연 / 차지 마지막 탄 recovery overlap: 검증된 표준 캐릭터에는 현행 처리 유지.
- Raid DEF exact 단일값: universal exact를 강제하지 않고 명시적 DEF 민감도 축으로 다루면 탐색 연구 blocker가 아니다.

### 캐릭터별 blocker / 범위 제한

다음 캐릭터는 **첫 verified-core Wave A aggregate에서 제외**한다.

- Scarlet: Black Shadow — 특수 reload timing unresolved
- Raven — RL reload/recovery decomposition unresolved
- Liberalio — 표시 2.0초 reload와 별도 post-delay decomposition unresolved
- Moran (Favorite Item) — current reload source conflict unresolved
- Quency: Escape Queen — hit/spread가 실제 normal/core DPS에 크게 작용하지만 현행 연구 엔진은 weapon spread/body miss를 모델링하지 않음
- Milk: Blooming Bunny — 현행 AUTO-only 구현이며 수동/특수 reload 경로는 범위 밖

이 캐릭터들의 현재 구현은 진단용으로 보존하지만 해당 이슈 해결 전에는 verified aggregate에 포함하지 않는다.

## Wave A verified-core 설계 상태

설계 초안은 `research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md`, 생성기는 `crown_mast_engine/wave_a_study.py`에 구현했다.

현재 후보:

```text
B1 4명
- liter
- anis-star
- little-mermaid
- rapi-red-hood

Main B3 6명
- rapi-red-hood
- cinderella
- cinderella-crystal-wave
- neon-vision-eye
- phantom
- bready

Secondary B3 3명
- epinel
- helm
- snow-white-heavy-arms
```

Rapi B1 + Rapi Main 중복 3 roster를 제외하면 유효 roster는 69개다.

성장 screening은 기존 4×4×4=64 완전교차 대신 16점 pairwise OA를 사용한다. 각 역할 쌍의 4×4 성장 조합은 정확히 한 번씩 포함하며, sign reversal / close-call / 이상치가 나온 roster만 후속 64점 full growth grid로 확대한다.

환경축은 다음 12조건을 완전교차한다.

```text
DEF: 140 / 12,000 / 31,784
core: 0% / 100%
Main advantage: off / on
```

31,784는 현재 DILDORO Solo Raid 설정에서 확인되는 high/Solo-style sensitivity anchor이며 universal exact DEF로 취급하지 않는다.

Wave A1 설계 총량:

```text
69 valid rosters × 16 growth OA × 12 environment = 13,248 scenarios
```

이 수치는 **설계된 case space**일 뿐이며 아직 13,248개 전투 simulation batch는 실행하지 않았다.

## Preflight gate

`wave_a_study.py`와 `tests/test_wave_a_study.py`가 다음을 fail-closed로 검증한다.

- unresolved actor가 verified-core allowlist에 들어오지 않는가
- duplicate actor roster를 생성하지 않는가
- 16점 OA가 B1×Main / B1×Secondary / Main×Secondary의 모든 4×4 조합을 정확히 한 번씩 포함하는가
- DEF/core/advantage label과 `CombatSettings`가 일치하는가
- 현재 allowlist에 Crown/Mast 외 추가 reload-speed skill source가 없는가
- Crown 44.35% + Mast 3 stack 45.12% = 89.47%로 현재 modeled reload ceiling이 100% 미만인가
- roster shard당 192 case와 총 13,248 scenario 산술이 맞는가
- case ID가 유일한가
- study 상태가 draft / explicit approval required로 유지되는가

## 새 연구 진행 원칙

새 연구는 두 단계로 분리한다.

1. **Wave A — verified-core exploratory study**
   - 현재 검증된 캐릭터만 사용
   - B1 / Main / Secondary / 성장 / core / 우월 / DEF 효과 및 상호작용 탐색
   - 변수 효과와 이상치 후보를 먼저 확인
2. **Wave B — unresolved actor re-entry**
   - 각 보류 캐릭터를 해당 timing/hit-model 이슈 해결 후 재진입
   - 재진입 전 결과를 Wave A의 검증 aggregate와 혼합하지 않음

## 신데렐라 anomaly watch

과거 폐기 결과에서 신데렐라가 튀었다는 사실은 새 연구의 증거가 아니다.

다만 재검증에서 놓치지 않기 위한 감시 대상으로만 남긴다.

- 재검증된 엔진에서도 다시 이상치인가
- 여러 DEF 조건에서도 다시 이상치인가
- core / 우월 / 성장 / Secondary 변화에서도 구조적 차이가 반복되는가

엔진 재검증 + DEF 포함 새 연구에서도 독립적으로 다시 이상치가 재현될 때만 버스트 집중도·인접 cycle 상쇄 등을 별도 후속 연구에서 검증한다.

재현되지 않으면 과거 관찰은 archive의 역사자료로 끝낸다.

## 코드 상태

`crown_mast_engine/`과 `tests/`는 Wave A verified-core 범위에서 preflight와 전체 regression을 통과했다. 다만 이것은 모든 캐릭터가 동일한 수준으로 검증 완료됐다는 뜻이 아니다.

기존 `official_study.py`와 관련 연구 생성 로직은 **superseded study scaffolding**이다. 새 Wave A 실행에는 사용하지 않는다.

## 다음 체크포인트

**Wave A 설계를 최종 동결할지 사용자 판단을 받은 뒤, 승인 시에만 새 study ID / provenance / run 저장구조를 동결하고 13,248-scenario Wave A1 batch 실행 단계로 넘어간다.**

사용자 명시 승인 전에는 대규모 batch를 실행하지 않는다.
