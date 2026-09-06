# 1연구 — 광범위 탐색 연구

## 역할

1연구는 Crown/Mast 운용의 보편적 최종 규칙을 확정하는 연구가 아니라, **대표적인 통제 조건에서 광범위한 조합을 탐색하여 우세 경향과 예외를 동시에 찾고 후속 연구 대상을 선별하는 연구**다.

## canonical 설계

```text
human/03_1연구_실행_설계_확정본.md
```

study ID:

```text
crown-mast-study-01-exploratory-v1
```

현재 표본:

- B1 5명 / Main B3 6명 / Secondary B3 3명
- Rapi B1/Main 중복 제외 후 **87 valid rosters**
- 성장 `g2/g3/g4`를 B1/Main/Secondary에 완전교차: **27 growth points**
- 환경축: DEF 3 × core 2 × Main advantage 2 = **12 environments**
- roster당 **324 scenarios**
- 총 **28,188 scenarios**
- 애장품 캐릭터 SR15 canonical floor

## 현재 상태

```text
execution model gates = 0
execution_ready = true
status = design-frozen-execution-unapproved
```

최종 preflight `34002759044`에서 focused 68/68, full regression 322/322, case-generation 28,188/28,188이 통과했다. 이 과정에서 공식 전투 시뮬레이션은 실행하지 않았다.

## 디렉터리

```text
01_exploratory/
├─ human/
│  ├─ 02_연구_실행_재현성_및_기록_규격.md
│  ├─ 03_1연구_실행_설계_확정본.md
│  └─ reports/<run_id>/       실행 후 한글 보고서
├─ machine/
│  ├─ manifest/               실행 전 템플릿
│  └─ runs/<run_id>/          실행별 기계 데이터
└─ validation/
   ├─ 실행 전 검증 기록
   └─ runs/<run_id>/          실행 후 검증
```

공식 run에서는 scenario/raw 데이터를 수만 개의 작은 Git 파일로 쪼개지 않고 **shard 단위 JSONL/CSV 또는 압축 파일**로 저장한다. aggregate와 보고서는 별도 파일로 유지한다.

사용자의 별도 명시 승인 전에는 28,188 scenario 공식 전투 batch를 실행하지 않는다.
