# Archive — pre-revalidation snapshot

이 디렉터리는 **2026-09-05 엔진 전면 재검증 및 연구 1 재시작 결정 이전의 자료**를 보존한다.

## 사용 규칙

이 archive의 내용은 다음 용도로만 사용한다.

- provenance 감사
- 과거 구현/설계 이력 확인
- 회귀 비교
- 재현성 확인
- 후속 가설의 역사적 출처 확인

다음 용도로는 사용하지 않는다.

- 새 연구 1의 결론
- 새 연구 1의 목표값 또는 사전 기대값
- 새 연구 1의 파라미터 조정 근거
- 새 결과와의 합산
- 새 엔진이 과거 결과를 재현하도록 맞추는 기준

## 구조

```text
archive/pre-revalidation-2026-09-05/
  docs/
    handoffs/        과거 인계문서
    audits/          과거 감사/검증 문서
    raid14/          RAID14 체크포인트·재계산·패턴 문서
    plans/           과거 결과 계획/기타 상태 문서
  research_results/
    designs/         폐기된 study v1 설계와 Secondary anchor 초안
    diagnostics/     흑련 등 독립 진단 케이스
    runs/            폐기된 공식 결과와 당시 run template
  scripts/           과거 study/benchmark/audit 실행 스크립트
  workflows/         과거 GitHub Actions 배치 정의 — 비활성 보존
  MANIFEST.sha256    이동 전 저장소 manifest 기록
```

## 중요한 예외

`crown_mast_engine/`과 `tests/`는 archive하지 않았다. 새 연구를 위해 재사용한다는 뜻이 아니라 **앞으로 독립 재검증해야 할 현재 코드**이기 때문이다.

`research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md`의 과거 흑련 진단이나 기존 신데렐라 이상치 등은 역사적 가설 생성 자료일 뿐이다. 새 엔진/새 DEF 축에서 같은 현상이 독립적으로 재현된 뒤에만 후속 연구의 근거가 될 수 있다.

현재 상태는 저장소 루트 `README.md`와 `docs/CURRENT_RESEARCH_HANDOFF.md`를 따른다.
