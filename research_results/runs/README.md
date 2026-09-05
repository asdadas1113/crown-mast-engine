# 전역 runs 영역 — 신규 연구에서는 사용하지 않음

이 디렉터리는 과거 active 구조의 호환성과 기록 추적을 위해 남겨둔다.

앞으로 승인되는 새 연구 실행 결과는 이 전역 `runs/`에 저장하지 않는다.

새 저장 위치:

```text
../studies/<연구>/machine/
```

각 연구의 manifest, scenario 정의, raw 결과, 집계 결과, provenance는 해당 연구 디렉터리 안에서 완전히 분리해 보관한다.

과거 `crown-mast-secondary-opportunity-v1` 결과와 당시 `_template`은 다음 archive에 있다.

```text
../../archive/pre-revalidation-2026-09-05/research_results/runs/
```

현재 공식/대규모 연구 실행은 승인되지 않았다. 사용자 명시 승인 전에는 새 batch를 실행하거나 이 디렉터리에 결과를 생성하지 않는다.
