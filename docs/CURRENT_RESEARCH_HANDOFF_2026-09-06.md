# Crown–Mast 연구 인수인계 — 2026-09-06

## 1. 현재 상태

작업 branch:

```text
research/14-burst-baseline
```

`main`은 수정하거나 병합하지 않는다.

현재 단계는 **1연구 후보군 재동결 / 실행 gate 재검증 필요 / 실행 미승인**이다.

공식 또는 대규모 연구 표본은 아직 실행하지 않았다.

## 2. 1연구 canonical 설계

현재 canonical 문서:

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

표본 산술:

- raw: 5 × 6 × 3 = 90 rosters
- Rapi B1/Main 중복 3개 제외
- **87 valid rosters**
- B1/Main/Secondary growth 16-point pairwise screening
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 192 scenarios
- 전체 **16,704 scenarios**
- Crown/Mast는 OL5 + SR15 대표 build 고정
- 애장품 캐릭터는 SR15 canonical floor

이 연구는 광범위 탐색 및 후속연구 후보 선별용이다. Crown/Mast 상대 성장, hit/spread, 특정 이상치 기전 등은 필요할 경우 후속연구로 분리한다.

## 3. 선택 캐릭터 실행 gate

이번 후보 재구성으로 다음 세 캐릭터가 다시 표본에 들어왔다.

```text
moran-favorite-item
scarlet-black-shadow
liberalio
```

이들은 후보군에는 포함하지만 공식 연구 실행 전에 model-specific 재검증이 필요하다.

- Moran FI: current reload source와 pinned timing 정합성
- SBS: 특수 charge/reload/high-speed timing 정합성
- Liberalio: reload body와 post-reload delay 분해 및 policy-sensitive timing 정합성

이 세 gate가 닫히기 전에는 16,704 scenario aggregate를 실행하지 않는다.

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

상세 기록:

```text
research_results/studies/01_exploratory/validation/01_연구_인프라_보강_검증_2026-09-06.md
```

## 5. manifest / provenance

규격 문서:

```text
research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
```

템플릿:

```text
research_results/studies/01_exploratory/machine/manifest/manifest_template.json
```

실제 run ID와 manifest는 연구 실행 승인 전에는 생성하지 않는다.

## 6. generator 정렬 상태

`crown_mast_engine/wave_a_study.py`는 현재 다음을 반영했다.

- canonical study ID 사용
- 새 B1/Main 후보군 반영
- 87 valid rosters
- 16 growth points
- 12 environments
- 16,704 expected scenarios
- case label의 `study_id` 정렬
- Moran/SBS/Liberalio를 `execution_gated_actors`로 명시
- Raven/Quency/Milk는 현 1연구 후보 밖으로 유지

공식 실행 전에는 이 구조를 focused regression으로 다시 확인한다.

## 7. 저장소 정리 상태

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

과거 연구 문서는:

```text
archive/pre-revalidation-2026-09-05/
```

에 보존한다.

`research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md`는 superseded pointer로 축소했고, 새 canonical 설계는 `studies/01_exploratory/` 아래에 둔다.

## 8. 다음 단일 체크포인트

연구 표본을 실행하지 않고 다음을 수행한다.

1. 새 후보군 기준 focused generator/invariant 테스트
2. Moran/SBS/Liberalio model gate 재검증
3. 필요시 해당 mechanics만 좁게 수정·재검증
4. full regression
5. 87/16/12/16,704 preflight 확인
6. manifest 실행값 동결

그 뒤에도 실제 16,704 scenario batch는 사용자 명시 승인 전까지 실행하지 않는다.
