# Secondary B3 experimental anchors — draft

Status: **초안 / 공식 결과 아님**

## 1. 연구 목적과 Secondary 축

본 연구는 보스 패턴·이동·무적·강제 엄폐 등 외생변수를 최대한 제거하고, 동일 조건에서 Crown/Mast B2 운용 차이만 비교한다.

주요 검증 대상은 관습적으로 사용되는 다음 판단이다.

> `메인 딜러가 강하면 Mast를 반복적으로 몰아주는 편이 유리하다.`

연구의 목표는 정확한 보편 손익분기점을 찾는 것이 아니다. 대신 다음을 근거 기반으로 확인한다.

1. 몰아주기가 유효한 조건이 실제로 얼마나 제한적인가.
2. 유효하더라도 이득 폭이 얼마나 작은가.
3. 몰아주기가 이기는 파티 구조가 일반적인 실전 편성에서 쉽게 발생하는가.

이 목적에서 **Secondary B3의 기회비용**을 핵심 분석축으로 둔다.

---

## 2. Secondary B3 3개 기준

### 2.1 Epinel — Low opportunity-cost / positive-control anchor

역할:
- 실전 추천 캐릭터를 대표하기 위한 표본이 아님.
- 의도적으로 자체 피해 기여도가 낮은 Secondary를 넣는 **low-end stress sample / positive control**.

확인하려는 것:
- Secondary의 기회비용을 충분히 낮추면 sustained funnel이 실제로 이길 수 있는가.
- 몰아주기 유효구간이 존재한다면 어느 정도까지 넓어지는가.

해석 주의:
- Epinel에서 몰아주기가 이긴다고 해서 Epinel 편성을 추천하지 않는다.
- 이 표본의 목적은 `몰아주기 자체가 구조적으로 불가능한 전략은 아니다`를 확인하고, 낮은 Secondary 기여도의 영향을 관찰하는 것이다.

### 2.2 Helm — practical middle anchor

역할:
- 실제로 활용 가능한 주류 캐릭터이면서, 메인 캐리보다 **서브딜러 성격이 뚜렷한 실전 기준점**.
- Low와 upper-bound 사이의 practical middle anchor.

확인하려는 것:
- 실전적인 Secondary 기여도를 가진 편성에서도 몰아주기 역전이 자주 발생하는가.
- 발생하더라도 이득 폭이 실전적으로 의미 있는 수준인가.

이 표본은 세 기준 중 **현실적인 중앙 기준**으로 우선 해석한다.

### 2.3 Snow White: Heavy Arms — High opportunity-cost / upper-bound stress-test anchor

역할:
- 자체 피해 기여도가 매우 높은 메인급 딜러를 Secondary B3 자리에 둔 **high opportunity-cost upper-bound stress test**.
- 일반적인 `강한 서브딜러 대표`를 뜻하지 않는다.

확인하려는 것:
- 포기하는 Secondary의 가치가 극단적으로 커질수록 sustained funnel의 기회비용이 얼마나 증가하는가.
- 메인에게 유리한 성장/코어/우월코드 조건을 주더라도 몰아주기 유효영역이 남는가.

해석 주의:
- Snow White: Heavy Arms는 조건에 따라 메인 캐리급 기여를 할 수 있으므로 실전 Secondary의 중앙값이나 일반적인 상위 서브딜러를 대표한다고 주장하지 않는다.
- 이 표본은 **Secondary 기회비용 축의 상단 경계값**을 만드는 것이 목적이다.
- 최종 결론에서 이 표본 때문에 conventional 승리 비율이 높아진 것을 실전 편성 전체에 그대로 일반화하지 않는다.

---

## 3. 분석의 중심

초기 내부 분류는 다음처럼만 사용한다.

```text
Epinel                  -> Low opportunity-cost / positive control
Helm                    -> Practical middle
Snow White: Heavy Arms  -> High opportunity-cost / upper-bound stress test
```

다만 최종 분석에서는 캐릭터 이름이나 선험적 Low/Mid/High 분류에 의존하지 않는다.

각 scenario에서 conventional rotation 기준으로 실제 계산된:

- Secondary 총피해
- Secondary의 5인 총피해 지분
- Main 총피해 및 지분
- sustained funnel 전환 시 Main gain
- 나머지 파티의 opportunity loss
- 최종 5인 총피해 변화율

을 함께 기록한다.

따라서 최종적으로는 다음 형태의 구조적 해석을 목표로 한다.

> Secondary 기여도가 증가할수록 몰아주기 승리영역이 어떻게 축소되는가?

이는 단순한 `어떤 캐릭터가 좋다/나쁘다` 비교가 아니라, **포기하는 Secondary B3의 기회비용이 Mast 몰아주기의 유효성을 어떻게 제한하는가**를 확인하기 위한 것이다.

---

## 4. 현재 robustness grid

성장축은 기존 realistic v3 구조를 유지한다.

```text
B1 growth       : 4 checkpoints
Main B3 growth  : 4 checkpoints
Secondary growth: 4 checkpoints

4 x 4 x 4 = 64 growth points per roster/environment
```

64점의 목적은 성장 임계값을 정밀 추정하는 것이 아니다.

- Main만 과투자된 상태
- Secondary가 더 잘 성장한 상태
- Main 고성장 / Secondary 저성장
- 세 역할이 비슷하게 성장한 상태

등의 불균형한 현실 가능 범위까지 포함해 결론의 robustness를 확인한다.

추가 환경축:

```text
Core: off / on
Main elemental advantage: off / on
```

즉 각 유효 roster당:

```text
64 growth x 2 core x 2 main advantage = 256 scenarios
```

Rapi: Red Hood를 B1 Combat Assist로 사용하는 경우 같은 Rapi를 Main/Secondary B3에 중복 편성할 수 없다. 현재 `TeamRoster` core validation에서도 동일 캐릭터 중복을 차단한다.

공식 v1 표본은 132 valid rosters, 총 **33,792 scenarios**로 동결되어 있다. 사용자 명시 승인 전에는 공식 batch를 실행하지 않는다.

---

## 5. 최종 결과에서 우선 볼 지표

### Primary

1. Secondary anchor별 sustained funnel 승리/패배 빈도
2. sustained funnel 승리점에서의 이득률 분포
3. conventional 승리점에서 funnel 선택의 손실률 분포
4. 역전점의 실제 Secondary damage share 분포

### Secondary

- Main별
- B1별
- 성장 조합별
- core on/off별
- Main elemental advantage on/off별

분석은 `전체 승률 하나`보다 **어떤 조건에서 역전이 발생하며, 그 역전의 효과크기가 얼마인지**를 우선한다.

---

## 6. 연구에서 주장하지 않을 것

이 grid의 각 점은 동일 확률로 발생하는 실전 관측치가 아니다.

따라서 예를 들어 funnel win이 전체의 5%라고 나와도:

> `실전에서 몰아주기가 유효할 확률은 5%다.`

라고 해석하지 않는다.

허용되는 표현은 다음과 같다.

> `본 연구가 정의한 현실적 통제 표본 공간에서 몰아주기 우세 조건은 제한적으로 나타났다.`

또한 본 연구는 보스 패턴·다중 파츠·무적·강제 엄폐 등 외생변수를 기본적으로 제외하므로, 해당 변수가 강한 실전에서는 별도 후속연구가 필요하다.

---

## 7. 현재 상태

- Secondary 3-anchor 역할 정의: **동결**
- 공식 v1 표본: **132 rosters / 33,792 scenarios 동결**
- 분배딜 Main 사전검증: `docs/DISTRIBUTED_MAIN_PRETEST_2026-09-02.md`
- 공식 research batch: **아직 실행하지 않음**
- 공식 결과 파일: **아직 없음**
