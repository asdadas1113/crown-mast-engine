# 1연구 기계용 데이터

이 디렉터리는 1연구 실행이 명시적으로 승인된 뒤 생성되는 기계 판독용 자료만 저장한다.

예정 구조:

```text
machine/
├─ manifest/
│  └─ manifest_template.json
├─ scenarios/
├─ raw/
├─ aggregate/
└─ provenance/
```

현재는 폴더 틀과 manifest 템플릿만 정의하며 실제 연구 데이터는 생성하지 않는다.

## 저장 원칙

- 모든 파일은 1연구 study ID와 연결되어야 한다.
- 각 실제 실행은 별도 run ID를 가진다.
- raw 결과와 집계 결과를 분리한다.
- 실행 시 사용한 branch, commit SHA, 엔진 규칙 revision, skill hook signature를 기록한다.
- 캐릭터 catalog의 source revision과 content SHA-256을 기록한다.
- 스킬 override가 있다면 변경 actor·skill·field·value가 revision에 포함되어야 한다.
- 각 scenario의 실제 roster, build, 전투 조건, timeline을 보존한다.
- 다른 연구의 데이터는 이 디렉터리에 저장하지 않는다.
- 과거 archive run을 복사하거나 새 결과와 혼합하지 않는다.

## manifest 템플릿

`manifest/manifest_template.json`은 실행 전 채워야 할 필드의 최소 형식을 정의한다.

`null` 또는 `TO_BE_*` 값이 남은 manifest로는 정식 연구를 실행하지 않는다. 실제 실행 시에는 템플릿을 덮어쓰지 않고 run별 manifest를 새 파일로 만든다.

사람이 읽는 상세 규칙은 `../human/02_연구_실행_재현성_및_기록_규격.md`를 따른다.
