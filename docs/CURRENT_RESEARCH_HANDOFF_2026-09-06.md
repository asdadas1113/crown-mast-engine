# Crown–Mast 연구 인수인계 — 2026-09-06

## 1. 현재 상태

작업 branch:

```text
research/14-burst-baseline
```

`main`은 수정하거나 병합하지 않는다.

현재 단계는 **1연구 설계 동결 / actor model gate 종료 / 실행 준비 완료 / 실행 미승인**이다.

런타임 정의:

```text
status = design-frozen-execution-unapproved
execution_ready = true
execution model gates = 0
```

여기서 `execution_ready=true`는 모델·generator·회귀 검증상 실행 준비가 완료됐다는 뜻이다. **공식 연구 실행 승인을 의미하지 않는다.**

공식 28,188 scenario 전투 연구 batch는 아직 실행하지 않았다.

## 2. 1연구 canonical 설계

canonical 문서:

```text
research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

study ID:

```text
crown-mast-study-01-exploratory-v1
```

현재 후보군:

### B1 — 5명

```text
liter
anis-star
moran-favorite-item
little-mermaid
rapi-red-hood
```

### Main B3 — 6명

```text
rapi-red-hood
scarlet-black-shadow
cinderella
cinderella-crystal-wave
liberalio
neon-vision-eye
```

### Secondary B3 — 3명

```text
epinel
helm
snow-white-heavy-arms
```

성장 설계:

```text
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

- `g1-base5-none`은 1연구에서 제외
- B1/Main/Secondary 세 축을 3 × 3 × 3 완전교차
- **27 growth points**
- 애장품 캐릭터 SR15 canonical floor 유지

표본 산술:

- raw: 5 × 6 × 3 = 90 rosters
- Rapi B1/Main 중복 3개 제외
- **87 valid rosters**
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 **324 scenarios**
- 전체 **28,188 scenarios**
- Crown/Mast는 OL5 + SR15 대표 build 고정

## 3. 선택 캐릭터 model gate 종료

공식 실행 전 재검증 대상이던 다음 세 캐릭터의 model gate는 모두 닫혔다.

```text
moran-favorite-item
scarlet-black-shadow
liberalio
```

### Moran Favorite Item

- 현행 Favorite Item reload 기준 1.0초와 모델을 정렬했다.
- raw reload body를 **60f**로 정규화했다.

### Scarlet: Black Shadow

- raw reload body: **120f = 2.0초**
- fixed reload-start delay: **12f = 0.2초**
- 공용 reload 공식 적용 후 120f body는 130f가 되고, fixed 12f를 더한 총 reload는 **142f ≈ 2.3667초**다.
- 일반 공격주기는 `18f charge + 26f recovery = 44f ≈ 0.7333초`로 직접 계측치와 정합한다.
- 대표 재분석에서도 Conventional 우세 방향은 유지됐다.

### Liberalio

- raw reload body: **120f = 2.0초**
- fixed reload-start delay: **12f = 0.2초**
- fixed 12f는 Crown/Mast 등의 reload-speed 효과로 감소하지 않도록 reload body와 분리했다.

actor gate 종료 semantic commit:

```text
6671b49fb8804f96b31c74f95808370cf6c7116b
```

Study 1 상태/테스트 정렬 commit:

```text
21c2529d4fe2078828631a301c064b2b93b0122a
```

## 4. numerical regression 및 stale test 정리

기존 full regression의 초미세 numerical 실패 3건은 Python 3.11과 3.12 사이의 부동소수점 누적 차이로 분류됐다.

- 기대 총딜 값은 변경하지 않았다.
- 절대 총딜 허용오차만 `1e-3`으로 정상화했다.

이후 첫 final preflight run `33998906485`에서 focused 68개는 통과했지만 full suite의 7개 테스트가 실패했다.

7개는 엔진 회귀가 아니라 오래된 테스트 기대값이었다.

- `RotationWinner.EQUAL` → 현행 `RotationWinner.TIE`
- 폐기된 `NO_SCALING_BREAK_EVEN`, `SCALING_BREAK_EVEN_ONLY` 기대값 → 현행 dominance/reverse-break-even 분류
- dominance case의 break-even accessor 기대 동작 정렬
- SBS 단일 reload `152f` 기대 → 현행 `120f body + 12f fixed delay` 분해 모델

stale regression expectation 정리 commit:

```text
f60f4cefbc3d48275f5bc33147e7d2d5c3b19674
```

엔진 동작이나 연구 기대값을 이 테스트 정리를 위해 변경하지 않았다.

## 5. 최종 실행 전 검증

최종 preflight:

```text
GitHub Actions run: 34002759044
job: 101404457366
head: f60f4cefbc3d48275f5bc33147e7d2d5c3b19674
Python: 3.12.14
result: success
```

검증 결과:

- focused Study 1 / repaired actor tests: **68/68 통과**
- full regression suite: **322/322 통과**
- Study 1 case-generation preflight: **28,188/28,188 통과**
- valid rosters: **87**
- growth points: **27**
- environments: **12**
- scenarios/roster: **324**
- execution model gates: **0**
- `execution_ready=true`
- case ID 중복: 없음
- blocked actor 포함: 없음
- study ID: `crown-mast-study-01-exploratory-v1`
- growth label: `full27-three-level`
- timeline: RAID14
- DEF/core environment 값: canonical 정의와 일치
- reload-speed ceiling: **89.47%**
- **Simulation executed: no**

즉 28,188개의 case 객체와 식별자/조건을 전수 생성·검사했을 뿐, 28,188개의 전투 시뮬레이션은 실행하지 않았다.

상세 기록:

```text
research_results/studies/01_exploratory/validation/05_최종_실행전_검증_2026-09-06.md
```

## 6. manifest / provenance

규격 문서:

```text
research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
```

템플릿:

```text
research_results/studies/01_exploratory/machine/manifest/manifest_template.json
```

manifest template은 현재 다음 설계값과 정렬한다.

- status: `design-frozen-execution-unapproved`
- study ID 고정
- B1/Main/Secondary 후보 목록 고정
- execution-gated actors: 빈 목록
- 87 valid rosters
- `g1-base5-none` 제외
- 3 growth levels / 27 full-cross points
- 12 environments
- 324 scenarios/roster
- 28,188 expected cases

실제 공식 run ID, 실행 commit SHA, 생성시각, 결과 provenance는 연구 실행 승인 전에는 채우지 않는다.

## 7. generator 정렬 상태

`crown_mast_engine/wave_a_study.py`는 현재 다음을 반영한다.

- canonical study ID 사용
- 현재 B1/Main/Secondary 후보군
- Study 1 전용 `WAVE_A_GROWTH_PROFILES = REALISTIC_GROWTH_PROFILES[1:]`
- 전역 4단계 profile 정의는 보존
- 3단계 27-point full Cartesian growth grid
- 87 valid rosters
- 12 environments
- 324 scenarios/roster
- 28,188 expected scenarios
- case label `growth_design = full27-three-level`
- execution-gated actors 없음
- `execution_ready=true`
- 공식 실행은 explicit user approval 필요

## 8. 저장소 정리 상태

과거 연구 문서는 `archive/pre-revalidation-2026-09-05/`에 보존한다.

최종 검증에 사용한 임시 workflow는 검증 결과 기록 후 제거한다. 공식 연구용 workflow로 전용하지 않는다.

`main`은 그대로 유지한다.

## 9. 다음 단일 체크포인트

엔진·generator 측 실행 전 gate는 모두 닫혔다.

다음 단계는 **사용자의 공식 1연구 실행 승인 여부 결정**이다.

승인 전에는 다음을 하지 않는다.

- 28,188 scenario 전투 시뮬레이션 실행
- 공식 run ID 생성
- 실제 manifest의 실행 commit/provenance 확정
- raw/aggregate 연구 결과 생성

사용자가 명시적으로 승인하면 그 시점의 branch HEAD와 canonical 문서를 다시 확인하고, manifest 실행값을 확정한 뒤 공식 batch를 시작한다.
