# 기계용 결과 자료

공식 run에서 재분석·검증·재현에 사용하는 구조화 자료를 보관한다.

```text
raw/<roster_id>.jsonl
```
- roster 하나당 256개 scenario compact row
- manifest와 함께 canonical 원자료

```text
tables/scenarios.csv
```
- 모든 scenario를 평탄화한 분석용 표

```text
tables/rosters.csv
```
- roster 단위 집계표

전체 cycle/source/damage-event verbose 로그는 기본 저장하지 않는다. 필요한 상세 사례는 manifest의 조건과 commit SHA로 다시 재현한다.
