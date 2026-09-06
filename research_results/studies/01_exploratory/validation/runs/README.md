# 1연구 실행별 validation

공식 실행 후 같은 `run_id`의 결과 완전성·재현성 검증을 이 디렉터리에 저장한다.

```text
validation/runs/<run_id>/
```

최소 확인 항목:

- expected/actual case 수 일치
- case ID 중복·누락 없음
- shard별 record 수와 checksum
- manifest와 실행 Git/catalog/hook revision 일치
- 실패·부분 실행 분리 여부
- aggregate가 raw에서 재구성되는지 확인
- close-call/sign flip/이상치 재현 기록

공식 run이 없으므로 현재는 이 인덱스만 존재한다.
