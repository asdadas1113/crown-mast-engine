# AI 연구 인계 프로토콜

이 문서는 저장소에 대한 사전 대화가 없는 AI가 Crown–Mast 연구를 인계받을 때 따르는 고정 절차다. 현재 수치와 진행 상태는 `CURRENT_RESEARCH_HANDOFF.md`에서 확인하고, 이 문서에서는 상태가 바뀌어도 유지할 운영 원칙을 정의한다.

## 1. 인계 시작 순서

새 AI는 어떤 코드 수정이나 연구 실행보다 먼저 다음 순서로 읽는다.

1. 루트 `AGENTS.md`
2. `docs/CURRENT_RESEARCH_HANDOFF.md`
3. 위 문서가 지정한 dated canonical handoff
4. `research_results/studies/01_exploratory/human/03_1연구_실행_설계_확정본.md`
5. `research_results/studies/01_exploratory/human/02_연구_실행_재현성_및_기록_규격.md`

서로 충돌하는 내용이 있으면 다음 우선순위를 적용한다.

```text
AGENTS.md > CURRENT_RESEARCH_HANDOFF.md가 가리키는 최신 문서 > 현재 Study 1 확정본 > 과거 문서
```

`archive/`는 역사·감사용이며 활성 연구의 코드, 수치, 실행 절차를 가져오는 곳이 아니다.

## 2. 인계 직후 읽기 전용 확인

새 AI는 다음 사실을 먼저 확인하고 사용자에게 기준을 보고한다.

```text
branch = research/14-burst-baseline
study_id = crown-mast-study-01-exploratory-v1
timeline = RAID14_TIMELINE
expected = 87 rosters × 324 = 28,188 scenarios
official batch = not executed; a completed status requires manifest and validation evidence
```

함께 확인할 항목:

- `git status --short --branch`
- `git rev-parse HEAD`
- manifest가 존재한다면 manifest의 branch와 commit SHA
- `machine/runs/<run_id>/`와 `validation/runs/<run_id>/`의 존재 및 상태
- 사용자에게 현재 대화에서 공식 실행 승인이 있었는지 여부

이 확인만으로 실행 승인이 생기지는 않는다. 이전 대화의 승인, 문서에 기록된 승인, 다른 AI의 추정은 현재 사용자의 명시적 승인으로 간주하지 않는다.

## 3. 단계별 권한 경계

### 검수·준비 단계

허용:

- 문서와 코드를 읽고 상태를 확인
- 테스트, compile, case generation처럼 전투 결과를 만들지 않는 검증
- manifest 템플릿과 실행 계획 점검

금지:

- 공식 28,188 scenario 전투 계산
- 공식 `run_id`를 임의로 확정
- 공식 결과처럼 보이는 raw/aggregate/report 생성

### 공식 실행 단계

사용자가 현재 대화에서 공식 1연구 실행을 명시적으로 승인한 경우에만 진입한다. 실행 전에 branch, clean working tree, commit SHA, `run_id`, manifest를 먼저 고정한다. 하나라도 고정되지 않으면 실행하지 않는다.

### 분석·보고 단계

완료된 raw와 validation을 근거로만 aggregate와 보고서를 만든다. 부분 shard나 실패 shard를 완료 결과에 섞지 않는다.

## 4. 실행 중 코드 불변성

한 run은 manifest에 기록된 정확한 commit SHA와 catalog digest에 귀속된다.

- 실행 시작 후 해당 run의 엔진, 캐릭터 데이터, 연구 정의를 수정하지 않는다.
- 재개 시 현재 checkout의 SHA·catalog·schema가 manifest와 다르면 즉시 중단한다.
- 코드가 바뀐 상태에서 기존 `run_id`를 이어서 사용하지 않는다.
- 원래 run을 재개해야 하면 manifest의 commit을 별도 clean worktree에 checkout한다.
- 변경된 코드로 다시 계산해야 하면 새 `run_id`를 만든다.
- 기존 scenario/raw/aggregate/manifest를 덮어쓰지 않는다.

이 원칙 때문에 1차 연구 이후 엔진을 수정해도 완료된 1차 연구의 재현성과 provenance는 유지된다.

## 5. 1차 연구 후 새 가설과 코드 변경

1차 연구 결과를 보기 전에는 후속 가설이나 코드 변경안을 미리 확정하지 않는다. 결과에서 새 가설이 생긴 뒤 다음 절차를 따른다.

1. 1차 연구의 run directory, manifest, validation, 보고서를 불변 자료로 보존한다.
2. 가설을 먼저 문서화하고 어떤 결과가 가설을 만들었는지 case ID와 run ID를 연결한다.
3. 새 작업 브랜치를 만든다. 예: `research/post-study1-<topic>`.
4. 엔진 변경과 연구 설계 변경을 구분한다.
5. 변경 후 전체 회귀와 해당 가설의 focused validation을 수행한다.
6. 변경된 코드로 계산하면 반드시 새 `run_id`를 사용한다.
7. 표본·환경축·핵심 질문이 달라지면 새 study ID와 별도 연구 디렉터리를 사용한다.

단순 문서 보완은 기존 연구 결과의 의미를 바꾸지 않는다. 반면 계산식, 캐릭터 데이터, timeline, 성장점, 환경축, 후보군 변경은 결과 호환성에 영향을 주므로 기존 raw와 직접 합치지 않는다.

## 6. 사후 오류 발견 처리

1차 연구 후 엔진 오류가 발견돼도 과거 결과를 조용히 수정하거나 삭제하지 않는다.

- 원본 manifest는 보존하고 같은 run의 validation 상태를 `invalid` 또는 `superseded`로 표시한다.
- 오류 원인과 영향 범위를 validation 문서에 기록한다.
- 수정 commit과 새 run ID를 사용해 재실행한다.
- 새 보고서에서 이전 run과 새 run의 관계를 명시한다.

오류가 결과에 영향을 주지 않는다고 판단한 경우에도 근거가 되는 focused regression을 남긴다.

## 7. 새 AI의 첫 보고 형식

새 AI는 작업 전 사용자에게 최소 다음을 보고한다.

```text
확인 branch / HEAD SHA
현재 study_id와 예상 case 수
RAID14 사용 여부
공식 run 존재 여부
현재 요청이 검수·준비·실행·분석 중 어느 단계인지
실행 승인이 필요한지 여부
발견한 불일치 또는 blocker
```

확인하지 못한 항목을 추정으로 채우지 않는다.
