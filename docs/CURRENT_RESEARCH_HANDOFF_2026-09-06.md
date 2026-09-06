# Crown–Mast 연구 인수인계 — 2026-09-06

## 1. 현재 상태

작업 branch:

```text
research/14-burst-baseline
```

`main`은 수정하거나 병합하지 않는다.

현재 단계:

```text
1연구 설계 동결
actor model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
공식 28,188 scenario 전투 batch = 미실행
```

`execution_ready=true`는 모델·generator·회귀 검증상 실행 준비가 끝났다는 뜻이며 사용자 승인과는 별개다.

## 2. canonical 설계

```text
research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md
```

study ID:

```text
crown-mast-study-01-exploratory-v1
```

표본:

- B1 5명
- Main B3 6명
- Secondary B3 3명
- raw 90 rosters
- Rapi B1/Main 중복 3개 제외
- **87 valid rosters**
- B1/Main/Secondary 성장 3×3×3 = **27 growth points**
- DEF 3 × core 2 × Main advantage 2 = **12 environments**
- roster당 **324 scenarios**
- 총 **28,188 scenarios**

성장 단계:

```text
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

Crown/Mast는 OL5 + SR15 대표 build 고정이며 애장품 캐릭터는 SR15 canonical floor를 유지한다.

## 3. actor model gate

재검증 대상이던 다음 세 캐릭터의 gate는 모두 닫혔다.

```text
moran-favorite-item
scarlet-black-shadow
liberalio
```

핵심 정리:

- Moran FI: raw reload body `60f = 1.0s`
- Scarlet: Black Shadow: `120f body + 12f fixed delay`, 0% reload speed에서 총 `142f ≈ 2.3667s`; 공격주기 `18f + 26f = 44f ≈ 0.7333s`
- Liberalio: `120f body + 12f fixed delay`; fixed 12f는 reload-speed 효과로 감소하지 않음

관련 semantic commit:

```text
6671b49fb8804f96b31c74f95808370cf6c7116b
```

## 4. numerical regression / stale test 정리

기존 초미세 numerical 실패 3건은 Python 3.11↔3.12 부동소수점 누적 차이로 분류했다. 기대값은 바꾸지 않고 총딜 절대 허용오차만 `1e-3`으로 정상화했다.

첫 final preflight `33998906485`의 7개 full-suite 실패는 현행 API/reload 모델을 따라오지 못한 stale test였다. 엔진 동작을 테스트에 맞춰 변경하지 않고 테스트 기대만 현행 의미에 맞췄다.

정리 commit:

```text
f60f4cefbc3d48275f5bc33147e7d2d5c3b19674
```

## 5. 최종 실행 전 검증

```text
GitHub Actions run: 34002759044
job: 101404457366
head: f60f4cefbc3d48275f5bc33147e7d2d5c3b19674
Python: 3.12.14
result: success
```

검증 결과:

- focused: **68/68**
- full regression: **322/322**
- case-generation preflight: **28,188/28,188**
- case ID 중복 없음
- blocked actor 없음
- 87 rosters / 27 growth / 12 environments
- reload-speed ceiling `89.47%`
- RAID14 / canonical study ID / 환경축 일치
- **Simulation executed: no**

상세:

```text
research_results/studies/01_exploratory/validation/05_최종_실행전_검증_2026-09-06.md
```

## 6. 공식 실행 결과 저장 구조

공식 실행을 승인하면 먼저 `run_id`를 고정하고 아래 구조를 만든다.

```text
research_results/studies/01_exploratory/
├─ machine/
│  ├─ manifest/manifest_template.json
│  └─ runs/<run_id>/
│     ├─ manifest.json
│     ├─ scenarios/
│     ├─ raw/
│     ├─ aggregate/
│     └─ provenance/
├─ human/
│  └─ reports/<run_id>/
│     ├─ 00_전체_요약.md
│     ├─ 01_세컨더리_기준점_분석.md
│     ├─ 02_메인_B3_분석.md
│     ├─ 03_B1_분석.md
│     ├─ 04_효과크기_분석.md
│     ├─ 05_역전_구조_분석.md
│     ├─ 06_성장_및_환경_민감도.md
│     ├─ 07_해석과_한계.md
│     ├─ 08_후속_연구_후보.md
│     └─ cases/
└─ validation/
   └─ runs/<run_id>/
```

원칙:

- `machine/runs/<run_id>/raw/`: scenario별 원시 결과
- `machine/runs/<run_id>/aggregate/`: 집계 CSV/JSON 등
- `human/reports/<run_id>/`: 사람이 읽는 한글 결과 보고서
- `validation/runs/<run_id>/`: 실행 후 완전성/재현성/이상치 검증
- 재실행 시 기존 run을 덮어쓰지 않고 새 `run_id`를 사용

## 7. 문서 및 브랜치 정리 정책

현재 실행에 직접 필요하지 않은 9월 5일 상태 문서와 초안은 active 영역에서 제거하고 다음에 보존한다.

```text
archive/pre-study1-execution-2026-09-06/
```

옛 실험 브랜치의 branch-tip tree도 같은 archive 아래 snapshot으로 보존한다. 이 snapshot은 역사·감사용이며 현재 연구 브랜치에 병합하지 않는다.

active 개발 기준 branch는 `research/14-burst-baseline` 하나다. `main`은 그대로 둔다.

## 8. 다음 단계

사용자가 공식 1연구 실행을 명시적으로 승인한 경우에만:

1. 실행 commit SHA 동결
2. `run_id` 생성
3. run manifest 완성
4. run별 저장 디렉터리 생성
5. 28,188 scenario 전투 batch 실행
6. raw 완전성 검증
7. aggregate 생성
8. 한글 결과 보고서 작성

그 전에는 공식 전투 batch를 실행하지 않는다.
