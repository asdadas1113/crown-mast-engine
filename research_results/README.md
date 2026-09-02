# Crown–Mast Research Results

이 디렉터리는 **공식 연구 결과를 수집·보존하는 전용 공간**이다.

## 목적

기존 `docs/RAID14_CHECKPOINT_*` 문서와 개발 중 실험값은 엔진 검증·탐색·회귀 확인을 위한 역사적 checkpoint다. 이 디렉터리의 자료와 섞지 않는다.

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
- 공식 research batch: **아직 실행하지 않음**
- 공식 결과 파일: **아직 없음**
