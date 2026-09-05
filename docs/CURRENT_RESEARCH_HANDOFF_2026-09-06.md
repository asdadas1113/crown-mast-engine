# Crown–Mast 연구 인수인계 — 2026-09-06

## 1. 현재 상태

작업 branch:

```text
research/14-burst-baseline
```

`main`은 수정하거나 병합하지 않는다.

현재 단계는 **1연구 후보군·성장설계 재동결 / 실행 gate 재검증 필요 / 실행 미승인**이다.

공식 또는 대규모 연구 표본은 아직 실행하지 않았다.

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

## 3. 선택 캐릭터 실행 gate

다음 세 캐릭터는 후보군에는 포함하지만 공식 연구 실행 전에 model-specific 재검증이 필요하다.

```text
moran-favorite-item
scarlet-black-shadow
liberalio
```

- Moran FI: current reload source와 pinned timing 정합성
- SBS: 특수 charge/reload/high-speed timing 정합성
- Liberalio: reload body와 post-reload delay 분해 및 policy-sensitive timing 정합성

이 세 gate가 닫히기 전에는 28,188 scenario aggregate를 실행하지 않는다.

## 4. 재현성 / 연구 인프라 보강

보강 semantic commit:

```text
e1dc10a31b2a70caadae5ca10a00644f8ad91b71
```

검증:

- focused hardening: 7/7 통과
- full regression: 317/317 통과
- wheel build 성공
- html2canvas vendor 포함 확인
- catalog content SHA-256 및 skill override revision 기록
- non-finite combat input fail-closed
- overlapping burst cycle fail-closed
- UI reset stale state 문제 수정
- Windows CP949 startup log 문제 수정
- setuptools package discovery 명시

## 5. 후보군 재구성 검증

기존 5 B1 / 6 Main / 3 Secondary 후보군 재구성 focused test는 9/9 통과했다.

이후 성장 설계는 사용자 결정에 따라 16-point pairwise에서 **3-level full27**로 변경했다. 따라서 기존 16,704 산술은 더 이상 current design이 아니다.

이전 전체 regression run `33991715546`의 318개 중 3개 실패는 총딜 20억대에서 약 `0.00005~0.00011` 차이의 기존 numerical baseline/tolerance 문제였다. 후보군 또는 성장 generator invariant 실패는 아니었다. 기대값을 임의 갱신하지 않는다.

## 6. manifest / provenance

규격 문서:

```text
research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
```

템플릿:

```text
research_results/studies/01_exploratory/machine/manifest/manifest_template.json
```

현재 manifest template은 다음으로 정렬됐다.

- study ID 고정
- B1/Main/Secondary 후보 목록 고정
- 87 valid rosters
- `g1-base5-none` 제외
- 3 growth levels / 27 full-cross points
- 12 environments
- 28,188 expected cases
- Moran/SBS/Liberalio execution-gated actors 기록

실제 run ID와 실행 commit SHA 등은 연구 실행 승인 전에는 생성하지 않는다.

## 7. generator 정렬 상태

`crown_mast_engine/wave_a_study.py`는 현재 다음을 반영했다.

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
- Moran/SBS/Liberalio execution gate 명시

## 8. 저장소 정리 상태

불필요 branch 정리는 사용자에 의해 완료됐다.

현재 남아 있는 branch:

```text
main
research/14-burst-baseline
research/64point-secondary-epinel
tmp/distributed-samples
tmp/rapi-b1-added-character-audit
```

마지막 세 branch는 고유 commit이 있어 내용 확인 전까지 보존한다.

과거 연구 문서는 `archive/pre-revalidation-2026-09-05/`에 보존한다.

## 9. 다음 단일 체크포인트

연구 표본을 실행하지 않고 다음 순서로 진행한다.

1. 3-level full27 generator/invariant focused 검증
2. 기존 초미세 numerical baseline 실패 3건 분류
3. Moran/SBS/Liberalio model gate 재검증
4. 필요시 해당 mechanics만 좁게 수정·재검증
5. clean full regression
6. 87/27/12/28,188 preflight 확인
7. manifest 실행값 동결

그 뒤에도 실제 28,188 scenario batch는 사용자 명시 승인 전까지 실행하지 않는다.
