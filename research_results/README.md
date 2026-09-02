# Crown–Mast Research Results

이 디렉터리는 **공식 연구 결과와 별도로 보존할 가치가 있는 독립 진단 연구 결과를 함께 수집하는 공간**이다.

두 종류는 반드시 구분한다.

```text
Official study results
-> frozen official design에 따라 생성된 publication-facing 결과

Independent diagnostic / case studies
-> 공식 batch 이전·중간에 발견한 메커니즘, 이상치, 원인분석 등
-> 정보 소득은 보존하되 official result count에는 포함하지 않음
```

## 목적

기존 `docs/RAID14_CHECKPOINT_*` 문서와 개발 중 실험값은 엔진 검증·탐색·회귀 확인을 위한 역사적 checkpoint다. 단순 checkpoint 숫자를 공식 결과로 승격하지 않는다.

다만 검증 과정에서 **독립적으로 해석 가치가 있는 발견**이 생기면, 재현 조건·가설검증·원인분석이 충분한 경우 `research_results/` 아래에 별도 case study로 보존할 수 있다. 이러한 문서는 공식 v1 batch와 명확히 분리한다.

공식 연구 결과는 연구 설계가 확정된 뒤 현행 검증 엔진으로 새로 수집한다.

## 운영 원칙

1. 연구 결과를 생성하기 전 엔진/캐릭터 메커니즘/시간축 검증을 끝낸다.
2. 결과 파일에는 최소한 다음을 기록한다.
   - engine rule revision
   - skill-hook revision
   - branch / commit SHA
   - RAID14 timeline revision
   - roster
   - 성장 프로필
   - core 조건
   - main elemental-advantage 조건
   - 비교 rotation
3. 기존 checkpoint 숫자를 공식 결과로 복사하지 않는다.
4. 연구 batch는 사용자 명시 승인 후에만 실행한다.
5. 원자료와 요약/해석을 분리한다.
6. 승패 빈도만 보지 않고 **효과크기와 역전 조건의 구조**를 함께 기록한다.
7. 각 grid point는 확률 표본이 아니라 통제된 결정론적 scenario다. 승리 비율을 실전 발생확률로 해석하지 않는다.
8. 독립 diagnostic/case study는 제목과 본문에 **not official batch result** 상태를 명시하고 official result count에 포함하지 않는다.

## Independent diagnostic / case studies

### Scarlet: Black Shadow Funnel Response Case Study — 2026-09-02

```text
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

공식 batch 이전에 흑련이 다른 Main 후보보다 유독 낮은 Funnel `g`를 보인 원인을 조사한 독립 연구다.

핵심 정보:

- distributed damage 버킷 오류 가설: 기각
- distributed Main 전체가 Funnel에 약하다는 가설: 기각
- Liter B1 특이성 가설: 기각
- 가장 잘 지지되는 원인: **흑련의 가치 있는 딜이 자기 B3에 충분히 집중되지 않고 다음 cycle에도 크게 남아 있어, Main cycle의 Mast 이득이 adjacent-cycle M3 손실로 크게 상쇄됨**
- Liter 64점 평균 SBS Main `g`: +0.918%
- Little Mermaid 64점 평균 SBS Main `g`: +1.068%
- 비교군 Quency: +3.707% / +3.332%
- 대표점 cycle 5/6/11/12에서 `+10% -> -21%`, `+10% -> -17%` 형태의 직접적인 cancellation 확인

이 문서는 **독립 연구 성과**로 보존하지만 공식 33,792-scenario 결과에는 포함하지 않는다.

## 현재 연구 질문

외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때:

- 관습적인 `강한 메인 딜러 → Mast 몰아주기`가 실제로 얼마나 넓은 조건에서 유효한가?
- 유효한 경우 이득 폭은 얼마나 큰가?
- 유효 조건이 정상적인 실전 파티 구조에서 자주 만들어질 만한가?

정확한 보편 임계값을 추정하는 것이 주목적은 아니다.

## 공식 v1 sample space

상세 설계:

```text
research_results/OFFICIAL_STUDY_DESIGN_V1.md
```

Study id:

```text
crown-mast-secondary-opportunity-v1
```

Final B1 sample:

```text
Liter
Anis: Star
Moran (Favorite Item)
Little Mermaid
Rapi: Red Hood — B1 Combat Assist
```

Final Main B3 sample:

```text
Rapi: Red Hood
Scarlet: Black Shadow
Bready
Cinderella: Crystal Wave
Liberalio
Milk: Blooming Bunny
Phantom (Favorite Item)
Quency: Escape Queen
Raven
```

Secondary B3 anchors:

```text
Epinel                  -> low-end positive control
Helm                    -> practical middle anchor
Snow White: Heavy Arms  -> high-contribution anchor
```

The Main list deliberately excludes the three Secondary anchors so Main/Secondary axes remain independent.

Rapi RH is the only character shared by the B1 and Main candidate lists. `Rapi B1 + Rapi Main` is excluded during candidate generation before `TeamRoster` construction.

Canonical v1 count:

```text
raw rosters:     5 x 9 x 3 = 135
Rapi duplicates:             - 3
valid rosters:                132
per roster:      64 x 2 x 2 = 256 scenarios
total:           132 x 256 = 33,792 scenarios
```

Environment axes:

```text
Core: off=0% / on=100% eligible core-hit rate
Main advantage: off / on using the real boss element naturally beaten by Main
```

Main advantage is not isolated to the Main actor; same-element teammates receive normal advantage under the selected boss element.

## 실행/저장 구조

Official execution is sharded by valid roster:

```text
1 roster shard = 256 scenarios
132 roster shards total
```

When the official run is authorized, use:

```text
research_results/runs/<run_id>/
  manifest.json
  raw/<roster_id>.jsonl
  tables/scenarios.csv
  tables/rosters.csv
  analysis/
```

Raw JSONL should store compact scenario-level records needed for Secondary opportunity-cost analysis. Do not store every verbose cycle/source report for all 33,792 points by default; selected full reports can be deterministically reproduced from the manifest.

## 현재 구현

```text
crown_mast_engine/official_study.py
tests/test_official_study.py
```

The generator freezes the candidate lists, pre-excludes duplicate actors, reports the canonical arithmetic, and builds one 256-scenario roster shard without executing research simulations.

## 현재 상태

- Secondary 3-anchor 선정: **v1 확정**
- B1 5명 / Main B3 9명 표본: **v1 확정**
- canonical scenario count: **33,792**
- 실행/저장 구조: **v1 설계 완료**
- independent diagnostic case study: **SBS Funnel response 1건 보존**
- 공식 research batch: **아직 실행하지 않음**
- 공식 결과 파일: **아직 없음**
