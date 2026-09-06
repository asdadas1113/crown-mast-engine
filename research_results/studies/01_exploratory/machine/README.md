# 1연구 기계용 데이터

이 디렉터리는 1연구의 기계 판독용 실행 자료를 저장한다.

## 구조

```text
machine/
├─ manifest/
│  └─ manifest_template.json
└─ runs/
   └─ <run_id>/
      ├─ manifest.json
      ├─ scenarios/
      ├─ raw/
      ├─ aggregate/
      └─ provenance/
```

현재 공식 run은 아직 없으므로 템플릿과 구조 설명만 존재한다.

## 저장 원칙

- 모든 실제 실행은 고유한 `run_id`를 가진다.
- 템플릿은 덮어쓰지 않고 `runs/<run_id>/manifest.json`을 새로 만든다.
- raw와 aggregate는 분리한다.
- 실행 branch, commit SHA, engine rule revision, skill hook signature를 기록한다.
- catalog source revision과 content SHA-256을 기록한다.
- 각 scenario의 실제 roster/build/environment/timeline을 보존한다.
- 28,188 scenario를 28,188개의 개별 Git 파일로 저장하지 않는다.
- scenario와 raw는 재현 가능한 shard 단위 JSONL/CSV로 묶고 필요하면 gzip 압축한다.
- 각 shard의 record 수·파일 크기·checksum을 manifest/provenance에 기록한다.
- 실패/부분 shard를 completed 결과와 섞지 않는다.
- 다른 연구나 과거 archive 데이터를 이 디렉터리에 복사하지 않는다.
- 재실행은 기존 run을 덮어쓰지 않는다.

사람이 읽는 결과는 같은 `run_id` 아래의 `../human/reports/<run_id>/`에 저장한다.

상세 규격은 `../human/02_연구_실행_재현성_및_기록_규격.md`를 따른다.
