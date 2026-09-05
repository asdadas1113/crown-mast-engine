# 1연구 기계용 데이터

이 디렉터리는 1연구 실행이 명시적으로 승인된 뒤 생성되는 기계 판독용 자료만 저장한다.

예정 구조:

```text
machine/
├─ manifest/
├─ scenarios/
├─ raw/
├─ aggregate/
└─ provenance/
```

현재는 폴더 틀만 정의하며 실제 데이터는 생성하지 않는다.

## 저장 원칙

- 모든 파일은 1연구 study ID와 연결되어야 한다.
- raw 결과와 집계 결과를 분리한다.
- 실행 시 사용한 branch, commit SHA, 설정, 후보군, scenario 수를 provenance에 기록한다.
- 실행 재현에 필요한 manifest를 함께 보존한다.
- 다른 연구의 데이터는 이 디렉터리에 저장하지 않는다.
- 과거 archive run을 복사하거나 새 결과와 혼합하지 않는다.
