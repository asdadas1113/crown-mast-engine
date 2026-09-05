# Crown–Mast 공개 모델 리스크와 연구 gate — 2026-09-05

## 목적

엔진 재검증 과정에서 아직 직접 근거가 충분하지 않은 항목을 숨기지 않고, **무엇이 연구 전체를 막는지 / 무엇은 특정 캐릭터 또는 특정 조건만 막는지**를 분리한다.

원칙은 `docs/SOURCE_VALIDATION_POLICY.md`를 따른다.

- 근거가 모호하면 임의 구현하지 않는다.
- 불확실성이 해당 시나리오의 Crown/Mast 상대 손익을 비대칭적으로 바꿀 수 있으면 그 시나리오는 검증 완료로 취급하지 않는다.
- 반대로 영향 범위가 제한적이고 연구 설계에서 해당 범위를 제외할 수 있으면 전역 blocker로 확대하지 않는다.

## 현재 판정 요약

| 항목 | 판정 | 현재 처리 |
|---|---|---|
| Mast: Romantic Maid Hit Rate Down | 전역 비차단 | 기본 직접 딜손실 0 유지 + 민감도 진단 |
| 100% 초과 Reload Speed | 조건부 비차단 | 실제 입력이 100% 미만인 연구만 허용 |
| 공용 post-reload 미세 지연 | 비차단 | 검증된 표준 캐릭터에는 새 공용 지연을 임의 추가하지 않음 |
| 차지 마지막 탄 recovery/reload 겹침 | 비차단 | 현행 직렬 처리 유지 |
| Scarlet: Black Shadow 재장전 | 캐릭터별 blocker | 검증 완료 canonical 표본에서 보류 |
| Raven 재장전 | 캐릭터별 blocker | 검증 완료 canonical 표본에서 보류 |
| Liberalio 재장전 | 캐릭터별 blocker | 검증 완료 canonical 표본에서 보류 |
| Moran (Favorite Item) 재장전 | 캐릭터별 blocker | 검증 완료 canonical 표본에서 보류 |
| Milk: Blooming Bunny 특수 수동 경로 | 범위 밖 / 캐릭터별 보류 | AUTO 진단 전용, 첫 검증 표본에서 제외 |
| Raid DEF exact 단일값 | 전역 비차단 가능 | exact 하나 대신 명시적 DEF 민감도 축 사용 |

## 1. Mast: Romantic Maid Hit Rate Down

### 확인된 사실

Skill 1의 Drunken은 Hit Rate를 스택당 20%, 최대 3스택 감소시킨다.

NIKKE.gg의 현재 해설은 3스택 -60%가 Mast의 실제 명중탄을 곧바로 60% 감소시키는 것으로 해석하지 않는다. 큰 보스/코어 상대로는 코어를 맞히는 능력 자체보다 핀포인트 정확도에 도달하기까지 몇 발이 더 필요한 효과로 설명한다.

따라서 `Hit Rate Down = 동일 비율의 normal damage loss`로 직접 치환하는 것은 근거가 없다.

현재 엔진 기본값은 다음과 같이 유지한다.

```text
expected_normal_damage_loss_per_stack_pct = 0
```

이는 '명중률 감소가 실제로 아무 효과도 없다'는 주장이라기보다, **검증되지 않은 직접 딜손실을 baseline에 발명해 넣지 않는다**는 연구용 처리다.

### 민감도 진단

현행 엔진에는 `analyze_mast_expected_hit_loss_sensitivity()`가 존재한다. 재장전 교정 이후 대표 조건에서 0 / 5 / 10 / 18 / 20 / 22% 직접 normal-damage loss per stack을 가정해 진단했다.

- 기본 standard: 모든 점에서 Conventional 유지
- 기본 RAID14: 모든 점에서 Conventional 유지
- Cinderella Main RAID14: 모든 점에서 Funnel 유지
- Cinderella: Crystal Wave Main RAID14: 모든 점에서 Funnel 유지

0 → 22%/stack이라는 매우 넓은 가정에서도 대표 조건의 승패는 뒤집히지 않았다. 상대 손익 이동은 대략 0.19~0.22 percentage point 범위였다.

### 연구 gate

- **전역 blocker가 아니다.**
- baseline은 0을 유지한다.
- 결과가 정책 경계에 매우 가까운 경우에는 Hit Rate 민감도 확인 없이 확정 판정하지 않는다.
- 실전 산포/거리/보스 hitbox를 연구 질문으로 삼을 때만 별도 명중 모델을 요구한다.

## 2. 100% 초과 Reload Speed

현재 `effective_reload_frames()`는 reload speed가 100% 이상이면 재장전 body를 0으로 clamp하고 고정 tail만 남긴다.

외부 자료에는 약 109~110% 이상에서 추가적인 perfect reload 동작이 보고되어 있으므로, 이 영역의 정확한 식은 미해결이다.

그러나 현재 기본 Crown–Mast 조합의 자체 최대 reload speed는 다음과 같다.

```text
Crown Skill 1       44.35%
Mast Skill 2 x3     45.12%
합계                 89.47%
```

현재 성장 모델의 OL 옵션도 ATK / Element / Max Ammo만 다루며 reload speed 축은 없다.

### 연구 gate

- **시나리오 전체가 100% 미만임을 보장하면 비차단이다.**
- Cube, Anchor, 추가 reload buffer 등으로 어느 actor/time에서든 100%를 넘길 수 있는 설계를 넣을 경우 그 설계는 미해결 blocker로 재분류한다.
- 새 연구 생성기에는 가능하면 `max modeled reload speed < 100%` 사전 검사를 두는 것이 바람직하다.

## 3. 공용 reload 후 지연과 차지 마지막 탄

Prydwen의 last-shot→first-shot 계측과 Ore-game의 재장전 세분화는 표시 reload 외 공격불가시간이 존재함을 시사한다. 그러나 Moris는 이를 모든 무기군에 동일한 공용 `post_reload_delay`로 일반화하지 않는다.

따라서 검증된 표준 캐릭터에 임의의 공용 11f 등을 추가하지 않는다.

또한 Helm 계열 직접 시간 대조에서는 현재의 `charge release recovery -> reload` 직렬 처리가 전체 magazine 시간과 잘 맞았다. 마지막 탄 recovery를 reload와 겹치도록 바꾸지 않는다.

### 연구 gate

- 검증된 표준 캐릭터에는 **비차단**.
- 독자적인 특수 reload/recovery를 가진 캐릭터는 아래 캐릭터별 gate를 적용한다.

## 4. 캐릭터별 unresolved timing

### Scarlet: Black Shadow

표시 reload 2.0초와 별개로 특수 자동발사/재장전 동작이 있다. 현재 152f를 단순 120f로 교체할 독립 근거가 부족하다.

**판정: 캐릭터별 blocker.**

### Raven

표시 reload와 RL 특수 동작/복귀 지연을 독립적으로 분해할 근거가 부족하다.

**판정: 캐릭터별 blocker.**

### Liberalio

표시 reload 2.0초는 확인되지만 Moris에 별도 `post_reload_delay=0.5s`가 있다. 현재 엔진의 141f가 이 둘을 합친 값에 가까워도, 그 전체가 reload-speed buff에 의해 줄어드는 것으로 처리되므로 Crown/Mast 정책 차이에 비대칭 오차가 생길 수 있다.

**판정: 캐릭터별 blocker 중 우선순위 높음.**

### Moran (Favorite Item)

현재 Prydwen 표기와 기존 pinned data의 기본 reload 값이 충돌한다. 독립 current source 또는 직접 실측 전에는 변경하지 않는다.

**판정: 캐릭터별 blocker.**

### Milk: Blooming Bunny

현행 연구 구현은 AUTO 기준이고 수동 Embarrassment/특수 강제 reload 경로를 모델링하지 않는다.

**판정: 첫 verified-core 표본 범위 밖.** 진단용으로는 사용할 수 있으나 보편 결과에 합치지 않는다.

## 5. DEF exact value

NIKKE의 적 DEF는 모드/보스/레벨에 따라 달라지므로 하나의 universal exact 값을 찾는 것이 연구 1의 필수조건은 아니다.

현재 generic baseline은 12,000을 사용한다. 새 연구 1은 변수 탐색이 목적이므로 DEF를 low / representative / high 등의 **명시적 민감도 축**으로 두면 exact 단일값의 불확실성을 연구 설계 내부에 포함시킬 수 있다.

### 연구 gate

- 특정 실전 Solo Raid 보스의 절대 피해량을 재현한다고 주장할 때는 exact DEF 근거가 필요하다.
- Crown/Mast 상대 손익의 변수 탐색에서는 여러 DEF 조건을 명시적으로 교차하면 전역 blocker가 아니다.
- 결과 문서에는 각 DEF 점을 실제 발생확률로 해석하지 않는다고 명시한다.

## 6. 다음 연구의 권장 구조

### Wave A — verified-core exploratory study

메커니즘과 cadence가 현재 검증된 캐릭터만 사용한다.

목적:

- B1 / Main / Secondary / 성장 / core / 우월 / DEF의 큰 효과 확인
- 상호작용과 이상치 후보 탐색
- 결과가 특정 보류 캐릭터의 미확정 timing에 의존하지 않도록 기반 확보

### Wave B — unresolved actor re-entry

SBS / Raven / Liberalio / Moran FI는 각 timing 이슈가 해결된 뒤 하나씩 Wave A 설계에 재진입시킨다.

재진입 전에는 해당 캐릭터를 포함한 결과를 verified aggregate에 합치지 않는다.

## 7. 해석 원칙

이 gate는 불확실성을 없앴다는 선언이 아니다.

목적은 다음 두 오류를 동시에 피하는 것이다.

1. 모든 미해결 항목 때문에 검증된 범위의 연구까지 무기한 정지하는 것
2. 미해결 캐릭터를 검증 완료 표본에 섞어 전체 결론의 신뢰도를 떨어뜨리는 것

따라서 현재 가장 안전한 진행 방식은 **검증된 core roster로 탐색을 먼저 진행하고, unresolved actor는 명시적으로 보류한 채 후속 재진입시키는 것**이다.
