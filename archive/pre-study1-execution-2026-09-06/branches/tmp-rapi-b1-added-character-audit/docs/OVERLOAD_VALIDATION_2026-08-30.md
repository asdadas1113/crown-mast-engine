# 크라운-메스트 연구: 오버로드 계산식 교차검증

> **Source-policy note (2026-09-02):** any `nikke-sim` reference below is provenance/secondary-reference only, not the authority priority. Current mechanics work must prefer Moris calculator / NIKKE.gg (and direct evidence when available) and must be independently cross-validated. See `docs/SOURCE_VALIDATION_POLICY.md`.

작성일: 2026-08-30

## 1. 검증 범위와 자료

이번 검증은 전체 오버로드 시스템이 아니라 연구 엔진에 넣을 세 옵션만 다룬다.

- 공격력 증가
- 우월코드 대미지 증가
- 최대 장탄 수 증가

확인한 자료:

- [NIKKE Sim](https://github.com/Infernal-Crack-LED/nikke-sim/tree/43308bd02276a476660e44af730785c2ae91eea3) `43308bd` (2026-08-25)
- [Jgaram 원본 계산기](https://github.com/Jgaram/nikke-calc/tree/35d8c204540d55ac41607d61554f5d463fc04295) `35d8c20` (2026-08-29)
- [Moris 실서비스 포크](https://github.com/Moris-kr/nikke-calc/tree/2584f4d2b402a0da24468c0c981bd339525bd29a) `2584f4d` (2026-08-30)
- [NIKKE.gg Damage Formula](https://nikke.gg/damage-formula/) (2026-08-07 갱신본)

Moris 사이트는 Jgaram 엔진의 포크를 브라우저에서 실행한다. 이번 검증 시점의 Moris 포크에서
아래 세 옵션의 핵심 계산 경로는 Jgaram 원본과 같았다.

### 1.1 근거 우선순위

NIKKE Sim은 `damage-calculation.md`, `nikke-damage-formula.md`, `game-mechanics.md`,
`override-guide.md` 사이에 시전자 공격력 기준 설명이 완전히 일치하지 않는다. 따라서 이번 검증은
문서 문구를 단순 다수결하지 않고 다음 순서로 판정했다.

1. 직접 인게임 관측값이 붙은 규칙
2. 현재 실행 코드가 실제로 수행하는 계산
3. 최신 피해 공식 문서
4. 구현 가이드와 설명용 문서

이 원칙에 따라 시전자 ATK는 두 엔진의 실행 코드가 공통으로 사용하는 Static ATK 기준을,
장탄은 실제 관측값 536발과 937발을 설명하는 Jgaram/Moris 규칙을 채택했다.

---

## 2. 결론표

| 항목 | NIKKE Sim | Jgaram / Moris | NIKKE.gg | 연구 엔진 결정 |
|---|---|---|---|---|
| OL 11급 수치 | 데이터는 1~15급 범위를 사용 | 11급 표에 공 11.81 / 우 23.56 / 장 68.93 | 옵션의 역할만 확인 가능 | 세 값 확정 |
| OL 공증 계층 | 자신의 `atkPct`에 가산 | 자신의 `atk_pct`에 가산 | 일반 ATK%와 같은 Base Damage 내부 | `Static ATK x (1 + ATK%)`에 가산 |
| 시전자 ATK 버프 | 시전자 `staticAtk` 기준 flat | 시전자 `base_stats.atk` 기준 flat | `% Caster's ATK`는 flat 항이나 기준 스냅샷은 불명확 | Static ATK 기준 유지, OL 공증으로 재증폭하지 않음 |
| 우코 | 우월 시 `1.10 + 추가%` | 우월 시 `1.10 + 추가%` | `Base 1.1 + Other Elemental Damage Sources` | 합의된 식 채택 |
| 장탄 반올림 | 모든 % 합산 후 1회 `Math.round` | 소스 그룹별 반올림 후 합산 | 상세 규칙 없음 | 인게임 실측 근거가 있는 Jgaram/Moris 규칙 채택 |

---

## 3. 공격력 증가

### 3.1 합의된 부분

OL 공격력은 캐릭터 자신의 일반 공격력 증가 버킷에 들어간다.

```text
Effective ATK
= Static ATK x (1 + 자신의 ATK%)
+ 시전자 공격력 기준 flat ATK
+ 기타 flat ATK
```

따라서 대상 캐릭터의 OL 공증이 이미 환산된 `시전자 공격력 기준 flat ATK`를 다시 곱하지 않는다.

### 3.2 시전자 기준 공격력

NIKKE Sim은 버프 적용 시 `owner.staticAtk x 버프%`를 flat 값으로 변환한다. Jgaram과 Moris도
`base_stats.atk x 버프%`를 수령자의 `atk_flat`에 넣는다. 양쪽 모두 시전자의 현재 `ATK%`나
OL 공증을 기준값에 포함하지 않는다.

NIKKE.gg의 최신 공식은 `% Caster's ATK`를 Base Damage 안의 flat 항으로 분류하지만, 그 값이
시전자의 Static ATK인지 버프 포함 최종 ATK인지까지는 명시하지 않는다. 따라서 사이트 설명만으로
두 코드 구현을 뒤집을 근거는 없다.

연구 엔진에서는 다음을 채택한다.

```text
Caster ATK flat = 시전자 Static ATK x 스킬 비율
```

이는 현재 엔진 규칙과도 일치한다. 추후 직접 실측이 나오면 `engine_rule_revision`을 올리고 이 규칙만
교체한다. 특히 고자체딜 B1에 OL 공증을 줄 때 팀 버프까지 함께 커지는 것으로 계산하지 않는다.

판정: **구현 가능, 신뢰도 중간.** 서로 독립된 NIKKE Sim과 Jgaram 계열 코드가 일치하지만 NIKKE.gg 문구만으로는 스냅샷 기준을
직접 증명할 수 없다.

---

## 4. 우월코드 대미지

세 자료의 방향이 일치한다.

```text
비우월 = 1.00
우월   = 1.10 + OL 우코% / 100 + 같은 우월 버킷의 추가 효과% / 100
```

예를 들어 OL 우코 70%가 활성화되면 `1.10 x 1.70`이 아니라 `1.80`이다. OL 우코는 캐릭터가
해당 보스 속성에 우월할 때만 활성화한다. 같은 코드 아군도 각자 우코 옵션을 보유했다면 함께 받는다.

판정: **확정 구현.** 현재 수동 속성 배율 경로는 디버그 override로 남기고, 보스 속성과 캐릭터
코드에 의한 자동 판정을 기본 경로로 둔다.

---

## 5. 최대 장탄 수

### 5.1 확인된 충돌

NIKKE Sim은 장탄 관련 모든 퍼센트를 더한 뒤 기본 장탄에 곱하고 한 번 반올림한다.

```text
NIKKE Sim
= round(Base Ammo x (1 + total ammo%)) + flat
```

Jgaram과 Moris는 소스 그룹별 증가량을 각각 반올림한 뒤 기본 장탄에 더한다.

```text
Jgaram / Moris
= Base Ammo
+ sum(round_half_up(Base Ammo x group%))
+ flat
```

그룹 규칙:

- 같은 종류와 같은 단계의 OL 장탄 옵션은 부위가 달라도 한 그룹
- 단계가 다른 OL 장탄 옵션은 서로 다른 그룹
- 소장품, 큐브, 각 스킬 버프는 OL과 별도 그룹
- flat 장탄은 퍼센트 그룹 계산 뒤 마지막에 더함
- 0.5는 올림
- 최종 최대 장탄 하한은 1발

### 5.2 채택 근거

Jgaram/Moris 문서에는 실제 계정 관측값이 남아 있다.

```text
MG 기본 300발
OL 장탄 68.93% + 소장품 9.5%

300 + round_half_up(206.79) + round_half_up(28.5)
= 300 + 207 + 29
= 536발
```

합산 후 한 번 반올림하면 535발이 되어 관측값 536발과 어긋난다. 따라서 이 항목은 계산기 간
다수결이 아니라 **실측 근거의 유무**로 결정하여 Jgaram/Moris 규칙을 채택한다.

연구 프리셋의 OL 장탄은 모두 11급이므로 `68.93% x N줄`을 하나의 OL 그룹으로 처리한다.
다만 소장품이나 스킬 장탄 버프가 겹치므로 엔진 내부에서는 합계 하나만 저장하지 않고 출처 그룹을
보존해야 한다.

판정: **소스 그룹 방식으로 구현.** NIKKE Sim과의 장탄 수 차이는 의도된 규칙 차이이며,
`mechanics_signature`에 장탄 규칙 revision을 포함한다.

---

## 6. OL 수치

Jgaram/Moris의 1~15급 옵션 표와 별도 OL 옵션 표를 대조했다. 연구에서 사용할 11급 값은 다음과 같다.

| 옵션 | 11급 1줄 |
|---|---:|
| 공격력 증가 | 11.81% |
| 우월코드 대미지 증가 | 23.56% |
| 최대 장탄 수 증가 | 68.93% |

따라서 `4우4공3장`은 다음 입력이다.

```text
우코 94.24%
공증 47.24%
장탄 206.79% (동일 11급 OL 그룹 1개)
```

`우공합 약 140%`는 우코와 공증의 단순 표기 합인 141.48%를 뜻하며, 피해식에서 두 값을 같은
버킷으로 합한다는 의미가 아니다.

---

## 7. 구현 상태

교차검증 결과에 따라 세 옵션의 핵심 경로를 구현했다.

1. `OverloadProfile`과 깡오버/고육성 프리셋 구현 완료
2. 공증을 자기 `ATK%`에 연결 완료
3. 보스 속성 자동 판정과 우코 연결 완료
4. 장탄 소스 그룹 자료구조와 소스별 반올림 완료
5. 첫 탄창과 재장전 완료 시점 회귀 테스트 완료
6. `mechanics_signature`를 `2026-08-30-r4-ol-t11-grouped-ammo`로 갱신

장비 본체 상태와 OL 옵션은 독립적으로 지정한다. 줄 수는 `0 이상의 정수`이며 엔진 상한을
두지 않는다. `4우4공3장` 같은 배열은 현실적 대표 프리셋이고, 그 이상의 값은 연구용
극단값으로 명시해 사용할 수 있다.

전체 회귀 테스트 149건을 통과했다. 표본 수집은 별도 엔진 완성 기준을 확정할 때까지 계속 중단한다.
