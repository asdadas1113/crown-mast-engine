# Crown–Mast Engine 연구 Handoff — 2026-09-02

이 문서는 새 채팅에서 현재 연구를 이어가기 위한 최신 인계문서다.

## 0. 새 채팅에서 먼저 읽을 것

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-02.md
docs/SOURCE_VALIDATION_POLICY.md
research_results/README.md
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
```

필요할 때만:

```text
docs/CHARACTER_AUDIT_2026-09-02.md
docs/DISTRIBUTED_DAMAGE_BUCKET_AUDIT_2026-09-02.md
docs/RAID14_CHECKPOINT_64POINT_REALISTIC_V3_2026-09-01.md
docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
```

을 본다.

`RAID14_CHECKPOINT_*`의 수치는 개발·검증용 historical checkpoint이며 공식 publication result가 아니다.

---

# 1. 저장소 / 브랜치

```text
repo: asdadas1113/crown-mast-engine
working branch: research/14-burst-baseline
main: 수정/병합 금지 unless explicitly requested
```

현재 branch head를 항상 GitHub에서 다시 확인한다. 이 문서 안의 과거 commit SHA를 최신 HEAD로 간주하지 않는다.

---

# 2. 연구 목적

목표는 NIKKE 전체를 완벽히 재현하는 범용 시뮬레이터가 아니다.

핵심 질문:

> 외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때, 관습적인 `한 딜러가 강하면 Mast를 몰아준다`는 판단이 실제로 얼마나 넓은 범위에서 유효한가?

최종적으로 근거 기반으로 확인하려는 것은:

1. 몰아주기 유효구간이 제한적인가.
2. 유효하더라도 이득 폭이 작은가.
3. 몰아주기 우세 파티가 일반적인 실전 구성에서 잘 발생하지 않는가.

정확한 보편 임계값을 찾는 것이 주목적은 아니다.

외생변수 제거:
- boss jump / movement
- invulnerability
- forced cover
- part exposure
- 기타 패턴 손실

이들은 기본연구에서 제외하고 필요하면 후속연구로 별도 처리한다.

---

# 3. 현행 RAID14 baseline

```text
fight: 180 sec
burst cycles: 14
B1 interval: 12.70 sec
B1 -> B2: 0.06 sec
B2 -> B3: 0.06 sec
first B1: 2.20 sec
c14 B1: 167.30 sec
c14 FB end: 177.42 sec
c15 theoretical B1: 180.00 sec, excluded
```

Conventional with M1 opener:

```text
M1,C,M3 / C,C,M3 / C,C,M3 / C,C,M3 / C,M2
```

Sustained funnel:

```text
M1,C,M3 / C,M2,C / C,C,M3 / C,M2,C / C,M2
```

M1 opener는 첫 macro에서만 가능한 특수조건이다. M3 이후 Hangover 때문에 반복하지 않는다.

---

# 4. 현행 엔진 검증 상태

2026-09-02 audit에서 다음을 교정했다.

- Rapi: Red Hood B1 Combat Assist 지원
- Raven DoT -> 하나의 refreshing stack-scaled DoT, max 10
- Quency: Escape Queen -> dual-SMG 2-hit trigger / sequential route / expiry 교정
- Cinderella: Crystal Wave MG Core Strike -> forced-core
- cast-instant B3 damage -> RAID14의 동일 timestamp 때문에 FB +50%를 잘못 받지 않도록 교정
- Distributed Damage buff -> ordinary Damage Taken과 같은 additive Taken bucket으로 교정

분배 버킷은 Moris calculator + NIKKE.gg 교차검증으로 확정했다.

현재 개념식:

```text
Distributed hit Taken multiplier
= 1 + ordinary Damage Taken + applicable Distributed Damage
```

별도 distributed multiplier와 곱하지 않는다.

관련 문서:

```text
docs/DISTRIBUTED_DAMAGE_BUCKET_AUDIT_2026-09-02.md
```

현재 명시적으로 남아 있던 distributed-bucket blocker는 해소된 상태다.

---

# 5. Rapi: Red Hood B1 역할 규칙

Rapi RH를 B1 Combat Assist로 배정하면 같은 Rapi를 Main/Secondary B3로 동시에 사용할 수 없다.

현재 `TeamRoster` core validation에서 **모든 동일 캐릭터 중복 편성을 거부**한다.

따라서:

```text
B1 Rapi + Main Rapi      -> invalid
B1 Rapi + Secondary Rapi -> invalid
```

정상 Rapi-B1 roster에서는 실제 B3_STAGE_ENTER event가 Rapi에게 생성되지 않는 회귀 테스트도 있다.

공식 후보 조합 생성기를 만들 때는 오류를 낸 뒤 버리는 방식보다 **candidate generation 단계에서 Rapi B1이면 Rapi B3를 미리 제외**한다.

---

# 6. 출처 정책

최상위 규칙:

```text
docs/SOURCE_VALIDATION_POLICY.md
```

핵심:

1. 직접 인게임 검증 / 공식 정보가 있으면 최우선.
2. Moris calculator와 NIKKE.gg를 주요 독립 참조로 사용.
3. 필요하면 Prydwen / 다른 독립 자료 추가.
4. nikke-sim은 datamine provenance / 구조화 데이터 / reference implementation용 보조 source.
5. nikke-sim 단독으로 새로운 mechanic semantic을 확정하지 않는다.
6. timing / trigger / damage bucket처럼 연구 결과를 바꾸는 항목은 교차검증 필수.
7. 근거가 충돌하면 충돌과 채택 이유를 기록한다.
8. 근거가 부족하면 unresolved/out-of-scope로 둔다.

---

# 7. 공식 연구 결과 저장 공간

새 디렉터리:

```text
research_results/
```

현재 파일:

```text
research_results/README.md
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
```

원칙:

- 기존 checkpoint 값과 공식 결과를 분리한다.
- 공식 결과는 현행 검증 엔진으로 새로 수집한다.
- 원자료와 요약/해석을 분리한다.
- 연구 batch는 사용자 명시 승인 전에는 실행하지 않는다.
- 각 결과에 engine revision / commit / timeline / roster / growth / environment를 기록한다.

현재 공식 결과는 **0개**다.

---

# 8. Secondary B3 3-anchor 초안

사용자가 정한 초안:

```text
Epinel                  -> Low secondary anchor
Helm                    -> Mid / practical secondary anchor
Snow White: Heavy Arms  -> High secondary anchor
```

## Epinel

- 실전 추천용이 아님.
- 의도적으로 약한 Secondary.
- low-end stress sample / positive control.
- `Secondary 기회비용이 충분히 낮으면 funnel이 실제로 이길 수 있는가`를 확인.

## Helm

- 실제 활용 가능한 주류 캐릭터.
- 메인 캐리보다 서브딜러 성격이 명확.
- 현실적인 중앙 기준점.

## Snow White: Heavy Arms

- 자체 딜 기여가 매우 높은 상위급 딜러.
- high-contribution Secondary anchor.
- `포기하는 Secondary의 가치가 커지면 funnel 유효영역이 얼마나 축소되는가` 확인.

중요:
- Low/Mid/High는 게임 전체 절대 티어 명칭이 아니다.
- 최종 분석은 이름보다 **conventional 기준 실제 Secondary damage share**를 주 분석변수로 사용한다.

상세:

```text
research_results/SECONDARY_B3_ANCHORS_DRAFT.md
```

---

# 9. 64-point robustness grid

기존 realistic v3 성장축을 사용한다.

```text
B1 growth        4
Main B3 growth   4
Secondary growth 4

4 x 4 x 4 = 64 growth points
```

이 64점은 임계값을 촘촘하게 추정하기 위한 연속 샘플이 아니다.

목적:
- Main 과투자
- Secondary 과투자
- Main high / Secondary low
- 비슷한 성장도
- 기타 불균형 성장상태

등을 넓게 포함해 결론의 robustness를 본다.

추가 환경축 초안:

```text
Core: off / on                         -> 2
Main elemental advantage: off / on    -> 2
```

따라서 **유효 roster 1개당 64 x 2 x 2 = 256 scenarios**.

각 grid point는 확률표본이 아니라 통제된 deterministic scenario다.

전체 funnel-win 비율을 실제 실전 발생확률로 해석하지 않는다.

---

# 10. 전체 조합 수 주의

대화 중 `33,792 scenarios`라는 provisional arithmetic를 논의했다.

그 숫자는:

```text
5 B1 x 9 Main x 3 Secondary
- Rapi B1/Main duplicate 3 rosters
= 132 valid rosters

132 x 64 growth x 2 core x 2 main advantage
= 33,792
```

라는 **가정된 5 B1 / 9 Main 목록**에 기반한 계산이다.

현재 이 문서에서는 9 Main 후보 목록을 공식 final sample list로 동결하지 않는다.

따라서 다음 채팅에서 전체 scenario 수를 공식화하기 전에:

1. B1 final list 확인
2. Main B3 final list 확인
3. Rapi duplicate exclusion 확인
4. Secondary 3-anchor 확인

후 다시 산정한다.

---

# 11. 분석 중심

이번 연구는 Main 단독보다 **Secondary 기회비용을 중심으로 분석할 가능성이 높다.**

Primary outputs:

1. Secondary anchor별 funnel win/loss 빈도
2. funnel 승리점에서 이득률 분포
3. conventional 승리점에서 funnel 손실률 분포
4. 역전점의 conventional Secondary damage share
5. Main gain vs rest-of-team opportunity loss

Secondary slicing:

- Main character
- B1 character
- growth state
- core on/off
- Main advantage on/off

핵심적으로 확인할 구조:

> Secondary 기여도가 높아질수록 몰아주기 승리영역이 얼마나 축소되는가?

예상 결론을 미리 고정하지 않는다. 실제 결과가 다른 방향이면 그대로 기록한다.

---

# 12. 연구에서 주장하지 않을 것

이 연구의 결과로 다음을 주장하지 않는다.

- 모든 NIKKE / 모든 boss에서 Crown-Crown-Mast가 항상 우월하다.
- grid의 funnel 승리비율이 실전 funnel 승리 확률이다.
- 하나의 보편 Main-share 임계값이 존재한다.
- 패턴 손실이 없는 baseline 결과가 모든 실전 패턴에 그대로 적용된다.

목표는 더 제한적이다.

> **외생변수를 통제한 현실적 표본공간에서 관습적인 Mast 몰아주기의 유효영역과 효과크기를 검증한다.**

---

# 13. 다음 작업 순서

공식 batch를 아직 실행하지 않는다.

다음 순서가 자연스럽다.

```text
1. B1 final sample list 확정
2. Main B3 final sample list 확정
3. 전체 유효 roster / scenario count 재계산
4. research_results raw-result schema 결정
5. batch generator가 Rapi duplicate를 사전 제외하도록 구성
6. 소규모 smoke/verification only
7. 사용자 명시 승인 후 official research batch 실행
8. raw results 저장
9. Secondary-anchor 중심 분석
10. 이후 pattern-loss follow-up
```

연구 결과 수집을 시작하기 전까지 기존 checkpoint를 공식 결과로 승격하지 않는다.
