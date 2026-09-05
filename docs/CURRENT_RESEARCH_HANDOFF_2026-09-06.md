# Crown–Mast 연구 인수인계 — 2026-09-06

## 1. 현재 상태

작업 branch:

```text
research/14-burst-baseline
```

`main`은 수정하거나 병합하지 않는다.

현재 단계는 **1연구 설계 동결 / 실행 미승인**이다.

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

동결된 A1 설계:

- verified-core B1 4명
- Main B3 6명
- Secondary B3 3명
- 중복 제외 69 rosters
- B1/Main/Secondary growth 16-point pairwise screening
- DEF 3 × core 2 × Main advantage 2 = 12 environments
- roster당 192 scenarios
- 전체 13,248 scenarios
- Crown/Mast는 OL5 + SR15 대표 build 고정
- 애장품 캐릭터는 SR15 canonical floor

이 연구는 광범위 탐색 및 후속연구 후보 선별용이다. Crown/Mast 상대 성장, hit/spread, 특정 이상치 기전 등은 필요할 경우 후속연구로 분리한다.

## 3. 재현성 / 연구 인프라 보강

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

## 4. manifest / provenance

규격 문서:

```text
research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md
```

템플릿:

```text
research_results/studies/01_exploratory/machine/manifest/manifest_template.json
```

실제 run ID와 manifest는 연구 실행 승인 전에는 생성하지 않는다.

## 5. 아직 남은 실행 전 작업

현재 `crown_mast_engine/wave_a_study.py`의 generator는 과거 식별자:

```text
wave-a-verified-core-draft-v1
```

을 사용한다.

실제 연구 실행 전에는 이를 동결 study ID와 정렬하고 다음 invariant를 다시 확인해야 한다.

- 69 valid rosters
- 16 growth points
- 12 environment conditions
- 13,248 unique case IDs
- blocked actor 미포함
- reload-speed ceiling gate 유지
- RAID14 timeline
- runtime/catalog/hook revision 일치

이 정렬은 실행 승인과 별개로 기능 검증 단계에서 진행할 수 있으나, 실제 13,248 scenario 계산은 사용자 명시 승인 전 실행하지 않는다.

## 6. 저장소 정리 점검

상세 문서:

```text
research_results/studies/01_exploratory/validation/02_저장소_정리_점검_2026-09-06.md
```

현재 삭제 후보 branch:

```text
noop-placeholder
research/64point-realistic-grid
verify/sample-batch-parallel
```

- `research/64point-realistic-grid`: 현재 branch의 완전한 조상
- `verify/sample-batch-parallel`: 현재 branch의 완전한 조상
- `noop-placeholder`: 정리 점검 중 실수로 생성된 ref, 고유 commit 0개

현재 연결 도구에는 branch ref 삭제 기능이 없어 자동 삭제하지 못했다.

고유 commit이 있어 즉시 삭제하지 않는 branch:

```text
research/64point-secondary-epinel   # 2 unique commits
tmp/distributed-samples             # 3 unique commits
tmp/rapi-b1-added-character-audit   # 22 unique commits
```

앞의 두 branch의 unique commit은 각각 temporary Epinel runner/matrix, distributed/Phantom diagnostic 계열이다. 마지막 branch는 character audit와 임시 검증 이력이 다수 남아 있어 archive 대체 여부를 확인하기 전 보존한다.

## 7. 문서 정리 상태

`docs/`는 현재 active 문서만 남아 있어 추가 대청소가 필요하지 않다.

과거 연구 문서는:

```text
archive/pre-revalidation-2026-09-05/
```

에 보존한다.

과거 `research_results/WAVE_A_VERIFIED_CORE_DESIGN_DRAFT.md`는 superseded pointer로 축소했고, 새 canonical 설계는 `studies/01_exploratory/` 아래에만 둔다.

전역 `research_results/runs/`는 deprecated migration pointer로만 유지하며, 새 연구 데이터는 각 연구의 `machine/`에 저장한다.

## 8. 다음 단일 체크포인트

연구 표본을 실행하지 않고 다음 기능 정렬을 수행한다.

1. `wave_a_study.py`의 draft study ID를 canonical study ID와 정렬
2. case labels/definition status를 `design frozen / approval required` 상태로 갱신
3. 기존 69/16/12/13,248 invariant tests를 새 study ID 기준으로 갱신
4. focused + full regression 검증
5. 검증 성공 후 실행-ready 문서만 갱신

그 뒤에도 실제 1연구 batch는 사용자 명시 승인 전까지 실행하지 않는다.
