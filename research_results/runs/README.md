# 공식 연구 실행 결과 폴더

이 디렉터리는 공식 연구 배치가 승인된 뒤 생성되는 run별 결과를 보관한다.

각 실행은 다음 구조를 따른다.

```text
research_results/runs/<run_id>/
  manifest.json
  machine/
    raw/
      <roster_id>.jsonl
    tables/
      scenarios.csv
      rosters.csv
  human/
    00_전체_요약.md
    01_세컨더리_기준점_분석.md
    02_메인_B3_분석.md
    03_B1_분석.md
    04_효과크기_분석.md
    05_역전_구조_분석.md
    06_성장_및_환경_민감도.md
    cases/
      몰아주기_승리_대표사례.md
      기존운용_승리_대표사례.md
      경계_사례.md
      이상치_사례.md
```

`manifest.json`은 사람/기계 양쪽이 공유하는 provenance 원본이다.

`machine/`은 재분석·검증·재현을 위한 구조화 원자료를 보관한다. 전체 verbose 전투 로그는 기본 저장하지 않고, compact scenario row와 roster 집계만 canonical raw로 남긴다.

`human/`은 사람이 읽는 해석 자료다. 원자료 전체를 복사하지 않고 요약·효과크기·역전 조건·대표 사례 중심으로 구성한다.

공식 연구 배치는 사용자 명시 승인 전에는 실행하지 않는다.
