# Crown Mast Research Engine

NIKKE의 Crown + Mast: Romantic Maid 운용을 비교하기 위한 개인 연구용 시뮬레이션 엔진입니다.

## 현재 연구 기준

2026-09-01부터 실전 연구의 기본 시간축은 `RAID14_TIMELINE`입니다.

```text
전투시간                 180.00 s
버스트 횟수              14
B1 -> 다음 B1            12.70 s
B1 -> B2 입력             0.06 s
B2 -> B3 입력             0.06 s
첫 B1                     2.20 s elapsed
c14 B1                  167.30 s elapsed
c14 Full Burst 종료     177.42 s elapsed
이론상 c15 B1           180.00 s elapsed
```

`STANDARD_TIMELINE`의 기존 12버스트 시간축은 삭제하지 않습니다. 과거 v6 연구 수치를 재현하고 엔진 변경의 회귀 여부를 확인하기 위한 **legacy regression reference**로만 유지합니다.

15버스트는 정상 연구 기준에 포함하지 않습니다. 현재 일반 정책은 c14에서 Drunken 2스택 Mast로 마무리하며 c15 요청은 오류로 처리합니다. 15버스트 같은 극단 입력 시나리오는 별도 custom rotation으로 명시해야 합니다.

## 현재 B2 정책

### Conventional / 크크메

```text
C, C, M3 / C, C, M3 / C, C, M3 / C, C, M3 / C, M2
```

### Sustained funnel / 지속 몰아주기

```text
C, C, M3 / C, M2, C / C, C, M3 / C, M2, C / C, M2
```

두 정책은 c13 Crown, c14 M2가 동일합니다. 따라서 마지막 두 사이클은 새로운 직접 B2 차이를 만들기보다 c11/c12에서 전파된 상태가 얼마나 남는지 확인하는 구간으로 기능합니다.

## 첫 B2 Crown vs M1

첫 B2 선택은 별도 변수로 유지합니다.

비교는 첫 Full Burst 10초 종료에서 자르지 않고, **두 오프너의 활성 버프 상태가 다시 같아지는 시점까지** 집계합니다.

RAID14 기준:

```text
c1 B1                         2.20 s
c1 B2                         2.26 s
c1 Full Burst 시작           2.32 s
c1 Full Burst 종료          12.32 s
첫 Crown Burst 종료         17.26 s
오프너 버프 상태 완전 수렴 17.32 s
```

17.26초 이후 0.06초는 Crown S1의 Burst-caster 대상 caster-ATK가 B2가 아니라 Full Burst 진입 시점부터 시작하기 때문에 남습니다.

현재 기본 Liter / Crown / Mast / Rapi: Red Hood / Helm 사례에서는 M1 선진입이 영향구간 총딜 기준 `+1.7108%` 우세합니다. 그러나 이 규칙은 보편적이지 않습니다. Scarlet: Black Shadow를 메인 B3로 둔 현재 엔진 사례에서는 M1 선진입이 `-0.3610%`, 즉 Crown 선진입이 근소하게 우세합니다.

따라서 **Crown 선진입과 M1 선진입을 항상 독립적으로 비교**합니다.

## 현재 RAID14 대표 결과

기본 Liter / Crown / Mast / Rapi: Red Hood / Helm 편성, 현재 기본 엔진 빌드와 보스 조건의 통제 사례:

| 항목 | RAID14 |
|---|---:|
| 크크메 총피해 | 2,793,708,977.32 |
| 지속 몰아주기 총피해 | 2,744,001,195.39 |
| 몰아주기 증감률 | -1.7793% |
| 크크메 기준 Main B3 비중 | 40.0096% |
| local 손익분기 Main share | 66.3750% |
| M1 선진입 영향구간 우위 | +1.7108% |

같은 기본 사례의 legacy 12버스트 손익분기는 70.6844%였습니다. 시간축 변경으로 값이 충분히 움직였으므로 과거 12버스트 손익분기 수치를 새 연구의 기준값으로 사용하지 않습니다.

손익분기는 조합·스펙·시간축에 종속되는 **국소값**입니다. “메인 딜러 비중 X%면 항상 몰아주기” 같은 보편 상수로 해석하지 않습니다.

## 엔진이 추적하는 핵심 상태

- Mast Drunken 1/2/3스택, 3스택 Full Burst 종료 reset, Hangover
- Crown S1/S2/Burst와 동일 Crown Burst 재사용 시 refresh
- Crown과 Mast처럼 서로 다른 source/skill 버프의 동시 적용
- caster ATK, ATK%, Attack Damage, Crit, Reload, Charge, Distributed, projectile 계열
- 무기 발사·장탄·재장전·MG 풍업/풍다운·차지/release 상태
- 캐릭터별 일반 공격·스킬·버스트 `DamageEvent`
- 장비, 수집품, OL 공증/우코/장탄, 보스 DEF·속성·코어·사거리 조건
- 캐릭터별/피해 종류별/발생원별/버스트 사이클별 피해 분해
- 크크메와 몰아주기의 총딜, 실제 Main 비중, local break-even 계산
- Crown/M1 오프너 4회전 대칭 비교

현재 구현된 주요 연구 캐릭터에는 Liter, Crown, Mast: Romantic Maid, Rapi: Red Hood, Helm(애장품), Scarlet: Black Shadow, Anis: Star, Moran(애장품), Little Mermaid, Snow White: Heavy Arms, Epinel, Neon: Vision Eye 등이 포함됩니다.

## 시간축 사용

```python
from crown_mast_engine import RAID14_TIMELINE, build_uniform_burst_timeline

# 현재 실전 연구 기준
timeline = RAID14_TIMELINE

# 시간축 민감도 실험용 예시
custom = build_uniform_burst_timeline(
    cycle_count=14,
    interval_sec=12.80,
)
```

현재 웹 UI와 기존 12점 기준점 지도는 아직 `ResearchScenario`의 legacy 12버스트 기본 시간축을 사용합니다. 따라서 **현재 연구 결론은 RAID14 엔진 계산 결과**, 기존 웹 기준점 지도는 **legacy 보조 도구**로 구분합니다.

## 검증 상태

2026-09-01 전체 회귀검증을 모듈별로 수행했습니다.

```text
테스트 모듈  22
테스트 수    209
통과         209 / 209
compileall   PASS
```

전체 209개를 한 프로세스로 실행하면 이 환경의 실행 제한을 넘기지만, 모듈별 분할 실행에서는 전부 통과했습니다. 검증 중 발견된 유일한 실패는 14사이클 정책으로 바뀐 뒤에도 12사이클 튜플을 기대하던 오래된 테스트 기대값이었으며 현재 정책에 맞게 수정 후 통과했습니다.

개인 연구용이므로 현 단계에서는 실행 속도 최적화보다 계산 규칙의 명시성·재현성·회귀검증을 우선합니다.

## 문서

- `docs/RAID14_BASELINE_2026-09-01.md` — 14버스트 실측 시간축과 c14 M2 규칙
- `docs/RAID14_RECALC_2026-09-01.md` — 12→14버스트 재계산과 손익분기 변화
- `docs/RAID14_OPENER_B3_SPOTCHECK_2026-09-01.md` — 선진입 B3별 반례 조사
- `docs/VALIDATION_2026-09-01.md` — 전체 회귀검증 기록
- `docs/RESEARCH_HANDOFF_V6.md` — 현행 문서 안내
- `docs/RESEARCH_HANDOFF_V6_LEGACY_FULL.md` — 2026-08-29 v6 원문 보존본
- `docs/OVERLOAD_VALIDATION_2026-08-30.md` — OL 관련 검증 기록
- `docs/PROVENANCE.md` — 데이터 출처 기록

## 테스트

```powershell
python -m unittest discover -s tests -v
```

한 번에 실행이 오래 걸리는 환경에서는 테스트 모듈을 나눠 실행해도 됩니다.
