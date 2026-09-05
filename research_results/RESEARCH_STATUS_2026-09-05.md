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

재장전 정규화 이후 집중 회귀와 전체 회귀를 갱신했고, 저장소의 추적 Python bytecode도 제거했다.

```text
full regression: 302 tests passed
bytecode: source tree에서 제거, .gitignore로 재발 방지
```

재장전 세부 교차검증은 `docs/RELOAD_TIMING_AUDIT_2026-09-05.md`, 남은 모델 불확실성과 연구 gate는 `docs/OPEN_MODEL_RISKS_2026-09-05.md`를 기준으로 한다.

## 미해결 항목의 현재 처리

모든 미해결 항목이 연구 전체를 막지는 않는다.

### 전역 비차단 또는 조건부 비차단

- Mast Hit Rate Down: 직접 normal-damage loss 기본값 0 유지. 0~22%/stack 진단에서도 대표 조건의 승패가 뒤집히지 않았으므로 탐색 연구 전체 blocker로 보지 않는다.
- 100% 초과 reload speed: 현재 Crown+Mast 자체 최대 89.47%이며 현재 성장축에도 추가 reload option이 없다. 모든 설계점이 100% 미만인 동안 비차단이다.
- 공용 post-reload 미세지연 / 차지 마지막 탄 recovery overlap: 검증된 표준 캐릭터에는 현행 처리 유지.
- Raid DEF exact 단일값: universal exact를 강제하지 않고 명시적 DEF 민감도 축으로 다루면 탐색 연구 blocker가 아니다.

### 캐릭터별 blocker

다음 캐릭터는 reload/recovery 특수 동작의 독립 근거가 부족하므로 **첫 verified-core 연구 표본에서 제외**한다.

- Scarlet: Black Shadow
- Raven
- Liberalio
- Moran (Favorite Item)

Milk: Blooming Bunny는 현행 AUTO-only 모델이므로 첫 verified-core 표본 범위 밖으로 둔다.

이 캐릭터들의 현재 구현은 진단용으로 보존하지만, timing 이슈 해결 전에는 verified aggregate에 포함하지 않는다.

## 새 연구 진행 원칙

새 연구는 두 단계로 분리한다.

1. **Wave A — verified-core exploratory study**
   - 현재 검증된 캐릭터만 사용
   - B1 / Main / Secondary / 성장 / core / 우월 / DEF 효과 및 상호작용 탐색
   - 변수 효과와 이상치 후보를 먼저 확인
2. **Wave B — unresolved actor re-entry**
   - SBS / Raven / Liberalio / Moran FI를 각각 추가 검증 후 재진입
   - 재진입 전 결과를 Wave A의 검증 aggregate와 혼합하지 않음

새 대규모 batch는 설계 동결과 사용자 명시 승인 전에는 실행하지 않는다.

## 재시작 순서

1. Crown–Mast 엔진 및 캐릭터 메커니즘 독립 재검증
2. damage formula와 방어력 처리 재검증
3. 검증된 범위 안에서 DEF 민감도 설계
4. verified-core B1 / Main / Secondary / 성장 / core / 우월 / DEF 변수 재동결
5. 새 study ID / 새 engine revision / 새 raw로 실행
6. 변수 효과·상호작용·이상치 탐색
7. unresolved actor를 검증 후 단계적으로 재진입
8. 재현성 있는 현상만 별도 후속 기전 연구로 분리

## 신데렐라 anomaly watch

과거 폐기 결과에서 신데렐라가 튀었다는 사실은 새 연구의 증거가 아니다.

다만 재검증에서 놓치지 않기 위한 감시 대상으로만 남긴다.

- 재검증된 엔진에서도 다시 이상치인가
- 여러 DEF 조건에서도 다시 이상치인가
- core / 우월 / 성장 / Secondary 변화에서도 구조적 차이가 반복되는가

엔진 재검증 + DEF 포함 새 연구에서도 독립적으로 다시 이상치가 재현될 때만 버스트 집중도·인접 cycle 상쇄 등을 별도 후속 연구에서 검증한다.

재현되지 않으면 과거 관찰은 archive의 역사자료로 끝낸다.

## 코드 상태

`crown_mast_engine/`과 `tests/`는 재검증이 상당 부분 진행됐지만, 모든 캐릭터가 동일한 수준으로 검증 완료된 것은 아니다.

기존 `official_study.py`와 관련 연구 생성 로직은 **superseded study scaffolding**이다. 새 설계 동결 전에는 공식 batch에 사용하지 않는다.

## 다음 체크포인트

**verified-core Wave A의 후보군과 DEF/core/우월/성장 축을 새 연구 목적에 맞게 재설계하고, unresolved actor가 포함되지 않는지 preflight gate를 고정한다.**

그 뒤 scenario 수와 새 study ID를 확정하고 사용자 승인 단계로 넘어간다.
