# Crown–Mast Engine 현재 연구 Handoff — 2026-09-01

## 0. 새 채팅에서 가장 먼저 할 것

이 문서는 현재 연구 상태의 **최신 진입점**이다.

새 채팅에서는 우선 다음 세 문서를 읽는다.

```text
docs/CURRENT_RESEARCH_HANDOFF_2026-09-01.md
docs/RAID14_CHECKPOINT_64POINT_REALISTIC_V3_2026-09-01.md
docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
```

필요할 때만 추가로:

```text
docs/RAID14_BASELINE_2026-09-01.md
docs/RAID14_OPENER_B3_SPOTCHECK_2026-09-01.md
docs/VALIDATION_2026-09-01.md
docs/RESEARCH_HANDOFF_V6_LEGACY_FULL.md
```

를 본다.

`RESEARCH_HANDOFF_V6_LEGACY_FULL.md`는 12버스트 시절 역사와 시행착오를 보존한 legacy 문서다. 그 안의 옛 수치나 §25 설계를 현재 최종값으로 복구하지 않는다.

# 0.1. 출처 검증 정책

`docs/SOURCE_VALIDATION_POLICY.md`가 현행 최상위 규칙이다. **Moris 계산기와 NIKKE.gg를 우선 참조하고, 타 사이트/직접 근거와의 교차검증을 필수로 한다.** `nikke-sim`은 pinned datamine/구조화 데이터/참조 구현을 위한 secondary source이며 단독 확정 근거로 사용하지 않는다. timing/trigger/bucket처럼 연구 결과를 바꿀 수 있는 항목은 두 독립 근거 또는 직접 인게임 검증 없이는 새 semantic rule로 확정하지 않는다.

---

# 1. 저장소 / 브랜치

```text
repo: asdadas1113/crown-mast-engine
primary research branch: research/14-burst-baseline
current handoff baseline commit after pattern-doc update:
a4919a0c9dc13ce8b434faa85e7d1bbe2aaf7b3c
```

`main`은 연구 브랜치와 분리해 유지해 왔다.

---

# 2. 연구의 출발점과 철학

목표는 NIKKE 전체를 완벽히 재현하는 범용 시뮬레이터가 아니라:

> **Crown / Mast B2 배치의 상대가치를 동일한 모델오차 아래 비교해 실전에서 쓸 수 있는 기본 운용과 예외 판단기준을 만드는 것.**

우선순위:

```text
1. 비교군 사이 동일한 모델오차
2. Crown/Mast와 직접 연결된 state의 정확성
3. 실전에서 실제로 나타날 법한 성장범위
4. 외생변수는 기본연구에서 제거하고 별도 후속연구로 재도입
```

따라서 기본연구에서는 보스 이동/점프/무적/강제엄폐/부위노출 등 패턴을 제거한다.

---

# 3. 현행 RAID14 baseline

```text
fight length: 180 sec
bursts: 14
B1 → next B1: 12.70 sec
B1 → B2: 0.06 sec
B2 → B3: 0.06 sec
first B1: 2.20 elapsed
c14 B1: 167.30
c14 Full Burst end: 177.42
theoretical c15 B1: 180.00, excluded
```

`0.06`은 수동 입력 근사이며 게임 프레임의 보편상수라고 주장하지 않는다.

현행 conventional RAID14 with M1 opener:

```text
M1,C,M3 / C,C,M3 / C,C,M3 / C,C,M3 / C,M2
```

sustained funnel:

```text
M1,C,M3 / C,M2,C / C,C,M3 / C,M2,C / C,M2
```

첫 M1은 직전 Hangover가 없는 전투 시작의 특수 opener다. M3 이후에는 stun/Hangover 때문에 동일한 방식으로 반복되지 않는다.

---

# 4. 본 연구 — 크크메 vs 지속 몰아주기

## 4.1 핵심 질문

기존 관습처럼 Main B3에 Mast2를 반복적으로 몰아주는 것이 실제로 5인 총피해에서 유리한가, 아니면 conventional Crown-Crown-Mast가 실전적인 기본값인가?

최종 판정은 Main 한 명의 증가율이 아니라 **5인 총피해**로 한다.

## 4.2 break-even 해석

- `g` = sustained funnel에서 Main B3 총피해가 conventional 대비 변한 비율
- `l` = sustained funnel에서 나머지 네 명의 합산 피해가 conventional 대비 잃는 비율

정상 tradeoff에서 conventional 기준 Main share의 break-even:

\[
s^*=\frac{l}{g+l}
\]

보편적인 `Main share 60%` 같은 상수는 없다. `g,l`은 캐릭터와 buff environment에 따라 달라진다.

---

# 5. 64-point realistic v3 — pre-audit historical checkpoint

> **2026-09-02 mechanics audit:** cast-instant Burst 피해의 Full Burst +50% 오적용, Raven DoT stack 구조, Quency route cadence/expiry 등을 교정했다. 아래 1,024-point 수치는 교정 전 역사적 checkpoint이며 현재 publication 결과로 인용하지 않는다. 연구 배치는 사용자가 다시 승인한 뒤 재실행한다.


각 B1 / Main B3 / Secondary B3 성장축에 네 현실적 성장상태를 사용한다.

```text
g1-base5-none
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

따라서 roster/boss condition당:

```text
4 × 4 × 4 = 64 growth points
```

이것은 OL 한 줄의 인과효과를 분해하는 설계가 아니라 **실제 계정 성장범위에서 결론이 안정적인지 보는 robustness grid**다.

현재 primary roster:

```text
B1: Liter, Anis: Star
Main B3: Rapi: Red Hood, Scarlet: Black Shadow, Snow White: Heavy Arms, Epinel
Secondary B3: Helm
Boss: neutral / Main natural elemental advantage
```

총 controlled comparisons:

```text
2 B1 × 4 Main × 2 boss × 64 = 1,024
```

결과:

```text
sustained funnel wins: 0 / 1,024
clear conventional: 978
marginal conventional: 46
tie: 0
mean relative change: about -1.9619% for funnel
```

46개 marginal conventional은 모두 Rapi: Red Hood Main-advantage 조건.

가장 funnel에 가까운 점도:

```text
Liter / Rapi RH / Wind boss
B1 g4 / Main g3 / Secondary g4
funnel relative change: -0.3624%
```

으로 conventional 쪽에 남았다.

현재 실전적 표현:

> **실제로 사용되는 정상적인 딜러 조합 범위에서는 크크메가 안정적인 기본값이다. 지속 몰아주기는 실사용 범위를 벗어날 정도로 Secondary 기여가 낮거나 다른 특수조건에서만 역전할 수 있다.**

`몰아주기는 절대로 이길 수 없다`고 일반화하지 않는다.

---

# 6. Epinel Secondary positive-control 결과

별도 temporary branch에서 Secondary를 극단적으로 낮은 Epinel로 바꾼 stress test를 수행했다.

```text
branch: research/64point-secondary-epinel
PR #3: closed without merge
primary branch에는 결과 코드/문서를 merge하지 않음
```

Main Epinel은 duplicate를 피하기 위해 제외.

```text
2 B1 × 3 Main × 2 boss × 64 = 768
```

결과:

```text
funnel: 413 / 768
conventional: 296 / 768
tie-band: 59 / 768
```

이 결과의 의미:

- 엔진이 구조적으로 funnel 승리를 막고 있지 않음.
- Secondary 기여도가 충분히 낮아지면 실제로 funnel-favorable regime이 발생함.
- Epinel Secondary는 practical recommendation이 아니라 positive-control/stress test.

Helm에서 `l`이 대략 3~4% 수준이던 것이 Epinel에서는 대략 1.1~1.3%로 크게 줄어든 것이 핵심 메커니즘이다.

---

# 7. Scarlet: Black Shadow / distributed damage 해석

SBS는 Mast와 강하게 시너지가 나는 distributed dealer인데도 sustained funnel의 `g`가 매우 작거나 일부에서 음수가 나왔다.

현재 결론은 버그라기보다 **측정정의와 메커니즘의 결과**다.

Mast S2는 Drunken stack이 있는 상태에서 B3 진입 시:

```text
Distributed Damage +15.03% × stack
Reload Speed +15.04% × stack
10 sec
```

을 주며, 이 효과는 B2가 Crown이어도 발동한다.

따라서 conventional Crown cycle에서도 SBS는 Mast의 핵심 distributed synergy를 이미 받는다.

sustained funnel에서 추가로 얻는 것은 Mast Burst의:

```text
Crit Damage
Attack Damage
caster ATK
```

이고, 대신 Crown Burst 15초 Attack Damage를 포기한다.

즉:

> `SBS가 Mast와 잘 맞는다`와 `SBS 때문에 Mast B2를 더 자주 써야 한다`는 같은 명제가 아니다.

다른 distributed dealer에서도 같은 패턴이 반복되는지 확인하면 class-level 해석을 강화할 수 있다.

---

# 8. Damage Taken + Distributed 공식 주의

현재 `damage.py`는 ordinary Damage Taken과 Distributed Damage modifier가 함께 있을 때 두 항을 곱하는 구조다.

NIKKE.gg의 현재 표기 기준으로는:

```text
Damage Taken = 1 + ordinary Damage Taken + Distributed Damage
```

처럼 같은 additive bracket으로 처리되는 것으로 확인했다.

현재 primary Crown/Mast 64-point 연구는 ordinary target Damage Taken을 사실상 사용하지 않으므로 이 문제는 현재 결론을 설명하거나 무효화하지 않는다.

하지만 **ordinary Damage Taken과 distributed buff가 동시에 있는 새 캐릭터를 넣기 전에는 수정/검증해야 한다.**

특히 Bready를 구현한다면 이 부분을 먼저 또는 동시에 처리하는 것이 안전하다.

---

# 9. 첫 버스트 Crown vs M1 후속연구

본 연구의 1,024-point grid에 opener까지 교차해 2,048점으로 불필요하게 키우지 않는다.

첫 버스트 문제는 별도 소규모 후속연구다.

현재 spot-check:

```text
Liter / Rapi / Helm: audited M1 opener about +1.90%
SBS case: M1 about -0.36%, Crown opener slightly better
```

즉 opener는 캐릭터별 예외가 실제로 존재할 가능성이 높다.

연구 질문:

> M1 first burst가 일반적으로 유리한가, 아니면 B3 mechanics에 따라 Crown-first 예외가 의미 있게 존재하는가?

현재 우선순위는 sample character expansion보다 뒤다.

---

# 10. 패턴손실 후속연구 — 설계 완료, 구현은 아직

현행 설계 문서:

```text
docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
```

핵심 질문:

```text
기본: C,C,M3
대응: C,M2,C
```

M3 예정 Full Burst에 예측 가능한 피해손실이 있을 때 해당 한 주기만 M2를 앞당길 threshold `L*`를 구한다.

## 10.1 180초 전체를 primary 판정에 사용하지 않음

패턴 대응은 한 M3 주기의 국소 선택이다.

primary 판정:

```text
3-FB local cycle
```

실전 중요도:

```text
한 번의 local delta를 기존 T180에 얹은 180s normalized delta
```

## 10.2 burst-position averaging

RAID14의 반복 가능한 normal blocks:

```text
A = c4~c6
B = c7~c9
C = c10~c12
```

각 block의 **실제 시작상태를 보존**하고 같은 상태에서 두 정책을 fork한다.

상태 자체를 평균하지 않는다.

각 run을:

```text
D1 = 1번째 burst-cycle
D2 = 2번째 burst-cycle
D3 = 3번째 burst-cycle
Tail = 세 번째 FB 뒤 직접 잔여 공격효과
```

로 나눈 뒤 같은 위치의 피해끼리 평균한다.

```text
평균 D1 + 평균 D2 + 평균 D3 + 평균 Tail
→ 대표 3버스트 사이클
```

세 번째 Full Burst 10초 loss-window 피해도 block별로 뽑은 뒤 평균한다.

**block별 L*을 먼저 구한 뒤 단순평균하지 않는다.**
피해 구성요소를 먼저 평균한 뒤 대표 L*를 한 번 계산한다.

\[
L^*=\frac{C_0-P_0}{C_w-P_w}
\]

위치별 결과는 primary estimator가 아니라 robustness diagnostic으로 보존한다.

## 10.3 패턴 연구 구현 순서

```text
1. c4/c7/c10 실제 시작state snapshot
2. 동일 snapshot에서 C,C,M3 / C,M2,C fork
3. D1/D2/D3/Tail 분할
4. 3rd FB loss-window 집계
5. burst-position average
6. 대표 3-FB cycle 조립
7. L* + no-crossing 판정
8. T180 normalized delta
9. 대표 표본 실제 time-mask 검증
```

**현재는 이 기능 구현보다 표본용 캐릭터 추가가 먼저다.**

---

# 11. 현재 검증 상태

최근 전체 검증 상태:

```text
2026-09-02 audited full discovery: 279 tests / 279 pass
compileall PASS
```

multiprocessing batch runner도 serial과 exact identical을 확인했고 36-point benchmark에서 대략 2.35× speedup을 확인했다.

엔진 신뢰도 해석:

```text
internal consistency: strong
relative-comparison confidence: high
exact game absolute fidelity: not fully established
```

이상한 결과가 나오면 먼저:

```text
bug
measurement definition
real mechanic
```

세 종류로 분류해서 본다.

---

# 12. 다음 작업 — 표본용 캐릭터 추가

## 현재 최우선 작업

> **64-point practical study와 구조적 일반화를 강화하기 위한 표본 캐릭터 추가.**

패턴손실 local module이나 opener full study로 넘어가기 전에 이 작업을 진행한다.

추가 캐릭터의 목적은 캐릭터 수 자체를 늘리는 것이 아니라 **현재 결론이 서로 다른 메커니즘에서도 반복되는지 확인하는 것**이다.

우선 선정 기준:

```text
1. 실제 Crown + Mast 조합에서 채용할 이유가 있는 캐릭터
2. 현재 Main/Secondary 표본과 다른 damage structure
3. Mast S2/Burst와의 반응구조가 다른 캐릭터
4. 구현비용 대비 연구정보량이 높은 캐릭터
5. 너무 극단적인 비실전 저DPS는 practical sample이 아니라 stress test로 분리
```

### 이미 논의된 유력 후보: Bready

Bready는 distributed dealer 검증에 유용하다.

구조적 이유:

```text
SBS = 반복/phase형 distributed proc
Bready = Full Charge 연계 conditional distributed damage
```

서로 다른 구조의 distributed dealer가 둘 다 conventional 쪽 패턴을 보이면:

> distributed dealer는 Mast와 잘 맞지만, Mast S2의 핵심 distributed buff는 Crown B2에서도 이미 발동하므로 sustained funnel이 자동으로 정당화되지는 않는다.

라는 class-level 해석이 강해진다.

단 Bready의 상태경로를 단순히 한 hit에 `distributed=True`만 붙이는 식으로 구현하지 않는다.

필요한 확인:

```text
Recommended Taste / Lingering Taste 상태경로
Full Charge trigger
Distributed hit
Damage Taken 경로
관련 지속피해
```

그리고 §8의 Damage Taken + Distributed bracket을 먼저/동시에 수정·검증한다.

Bready가 최종 첫 추가캐릭터로 확정된 것은 아니다. 새 채팅에서 실제 후보를 검토한 뒤 implementation order를 정한다.

---

# 13. 새 채팅에서 바로 이어갈 작업 절차

새 채팅의 첫 요청은 다음 취지로 시작하면 된다.

```text
GitHub의
- docs/CURRENT_RESEARCH_HANDOFF_2026-09-01.md
- docs/RAID14_CHECKPOINT_64POINT_REALISTIC_V3_2026-09-01.md
- docs/RAID14_PATTERN_LOSS_FOLLOWUP_2026-09-01.md
를 읽고 연구를 이어간다.

다음 작업은 표본용 캐릭터 추가다.
현재 구현된 캐릭터와 연구표본의 빈 영역을 확인하고,
추가 후보를 실전성 / 메커니즘 다양성 / 구현비용 기준으로 선정한 뒤 구현한다.
Bready는 distributed 구조 검증 후보로 우선 검토하되 자동 확정하지 않는다.
```

후보 선정 전에는 새 캐릭터를 무작정 많이 구현하지 않는다.
먼저 **어떤 가설공간을 채우는 표본인지**를 정의하고 추가한다.

---

# 14. 하지 말아야 할 것

```text
legacy 12-burst threshold를 현재 결과로 복구
60% 같은 universal Main-share rule을 다시 도입
Epinel stress test를 practical recommendation으로 해석
Helm 0/1024만으로 모든 조합에 universal impossibility 주장
SBS의 작은 g를 Mast synergy 부재라고 해석
패턴손실 연구에서 180초 전체 intervention을 모든 표본에 강제
패턴 연구에서 block별 L*를 단순평균
state 자체를 평균해 가상 local cycle 생성
새 캐릭터를 연구질문 없이 대량 구현
```

현재 연구 방향은 **넓은 실전표본으로 기본규칙을 먼저 확보하고, 상세한 연속 임계점이나 인과분해는 마지막에 별도 parameter study로 넘기는 것**이다.
