# 1연구 실행별 기계 데이터

공식 실행이 승인되면 이 디렉터리 아래에 고유한 `run_id` 폴더를 만든다.

```text
runs/<run_id>/
├─ manifest.json
├─ scenarios/
├─ raw/
├─ aggregate/
└─ provenance/
```

`scenarios/`와 `raw/`는 수만 개의 개별 파일 대신 shard 단위 JSONL/CSV를 사용하며 필요하면 gzip 압축한다. 각 shard의 record 수와 checksum은 manifest/provenance에 기록한다.

기존 run은 덮어쓰지 않는다.
