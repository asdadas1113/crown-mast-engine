# Crown–Mast 연구 결과

이 디렉터리는 **공식 연구 결과와 별도로 보존할 가치가 있는 독립 진단 연구 결과를 함께 수집하는 공간**이다.

두 종류는 반드시 구분한다.

```text
공식 연구 결과
-> 최종 동결된 공식 설계에 따라 생성된 공개용 결과

독립 진단 연구 / 케이스 스터디
-> 공식 배치 이전·중간에 발견한 메커니즘, 이상치, 원인 분석 등
-> 정보 소득은 보존하되 공식 결과 수에는 포함하지 않음
```

## 운영 원칙

1. 연구 결과를 생성하기 전 엔진/캐릭터 메커니즘/시간축 검증을 끝낸다.
2. 결과에는 엔진·훅·카탈로그 revision, branch/commit SHA, RAID14 시간축, roster, 성장 프로필, core/우월 조건, 비교 rotation을 기록한다.
3. 기존 체크포인트 숫자를 공식 결과로 승격하지 않는다.
4. 공식 연구 배치는 사용자 명시 승인 후에만 실행한다.
5. 원자료와 요약/해석을 분리한다.
6. 승패 빈도뿐 아니라 **효과크기와 역전 조건의 구조**를 함께 본다.
7. 각 격자점은 확률 표본이 아니라 통제된 결정론적 시나리오다.
8. 독립 진단 연구는 **공식 배치 결과가 아님**을 명시하고 공식 결과 수에 포함하지 않는다.

## 독립 진단 연구 / 케이스 스터디

### 흑련 몰아주기 반응 케이스 스터디 — 2026-09-02

```text
research_results/SCARLET_BLACK_SHADOW_FUNNEL_CASE_STUDY_2026-09-02.md
```

공식 배치 이전에 흑련이 다른 메인 후보보다 유독 낮은 몰아주기 `g`를 보인 원인을 조사한 독립 연구다.

핵심 정보:

- 분배 대미지 버킷 오류 가설: 기각
- 분배딜 메인 전체가 몰아주기에 약하다는 가설: 기각
- 리타 B1 특이성 가설: 기각
- 가장 잘 지지되는 원인: **흑련의 가치 있는 딜이 자기 B3에 충분히 집중되지 않고 다음 사이클에도 크게 남아 있어, 메인 사이클의 메스트 이득이 인접 사이클 M3 손실로 크게 상쇄됨**
- 리타 64점 평균 흑련 메인 `g`: +0.918%
- 리틀 머메이드 64점 평균 흑련 메인 `g`: +1.068%
- 비교군 퀀시: +3.707% / +3.332%
- 대표점 5/6/11/12사이클에서 `+10% -> -21%`, `+10% -> -17%` 형태의 직접적인 상쇄 확인

이 문서는 독립 연구 성과로 보존하며 공식 배치 결과에는 포함하지 않는다.

## 현재 연구 질문

외생변수를 최대한 제거한 동일 조건에서 Crown/Mast B2 운용만 바꿨을 때:

- 관습적인 `강한 메인 딜러 → Mast 몰아주기`가 실제로 얼마나 넓은 조건에서 유효한가?
- 유효한 경우 이득 폭은 얼마나 큰가?
- 유효 조건이 정상적인 실전 파티 구조에서 자주 만들어질 만한가?

정확한 보편 임계값 추정이 주목적은 아니다.

## 공식 v1 표본 공간 — 현재 재검토 중

상세 설계:

```text
research_results/OFFICIAL_STUDY_DESIGN_V1.md
```

연구 ID:

```text
crown-mast-secondary-opportunity-v1
```

B1 표본:

```text
Liter
Anis: Star
Moran (Favorite Item)
Little Mermaid
Rapi: Red Hood — B1 Combat Assist
```

현재 Main B3 표본:

```text
Rapi: Red Hood
Scarlet: Black Shadow
Bready
Cinderella
Cinderella: Crystal Wave
Liberalio
Milk: Blooming Bunny
Phantom (Favorite Item)
Quency: Escape Queen
Raven
```

2026-09-02 첫 공식 배치 전에 후보군을 재검토하면서 **원본 Cinderella를 추가했다.** Quency/Bready 등의 유지 여부와 이미 엔진에 구현된 Neon: Vision Eye의 공식 Main 편입 여부는 차후 논의 대상으로 남겨 두었다. 따라서 Main 후보군은 아직 최종 동결이 아니다.

Secondary B3 기준점:

```text
Epinel                  -> 낮은 기회비용 대조군
Helm                    -> 실전적인 중간 기준점
Snow White: Heavy Arms  -> 높은 기회비용 상단 스트레스 테스트
```

Snow White: Heavy Arms는 일반적인 강한 서브딜러 대표가 아니라, 메인급 딜러를 Secondary 자리에 둬 기회비용의 상단을 확인하는 스트레스 테스트다. 최종 해석은 캐릭터 라벨보다 실제 Secondary 딜 및 지분을 우선한다.

현재 코드 기준 시나리오 수:

```text
원시 로스터:       5 x 10 x 3 = 150
라피 중복 조합:                 - 3
유효 로스터:                    147
로스터당:           64 x 2 x 2 = 256 시나리오
총합:               147 x 256 = 37,632 시나리오
```

**37,632는 현재 후보군 기준 임시 표본 수**다. Main 후보 최종 재검토 후 공식 배치 직전에 다시 canonical count를 확정한다.

환경축:

```text
코어: off=0% / on=100% 적격 코어 적중률
메인 우월속성: off / on, 실제 메인 속성이 우월을 갖는 보스 속성 사용
```

메인 우월속성은 메인에게만 인위적으로 적용하지 않는다. 같은 속성의 팀원도 선택된 보스 속성에 따라 정상적으로 우월 보너스를 받는다.

## 실행/저장 구조

공식 실행은 유효 roster 단위로 분할한다.

```text
roster 1개 shard = 256 시나리오
현재 후보군 기준 = 147 shard
```

공식 실행이 승인되면:

```text
research_results/runs/<run_id>/
  manifest.json
  raw/<roster_id>.jsonl
  tables/scenarios.csv
  tables/rosters.csv
  analysis/
```

원시 JSONL에는 Secondary 기회비용 분석에 필요한 compact 시나리오 기록을 저장한다. 전체 시나리오의 상세 cycle/source report는 기본 저장하지 않고 필요한 사례만 manifest에서 재현한다.

## 현재 구현

```text
crown_mast_engine/official_study.py
tests/test_official_study.py
crown_mast_engine/data/character_cinderella.json
crown_mast_engine/character_mechanics/cinderella.py
tests/test_cinderella.py
```

## 현재 상태

- Secondary 3개 기준점: **유지**
- B1 5명 표본: **유지**
- Main B3 표본: **재검토 중, 현재 10명**
- 원본 신데렐라: **구현 및 현재 Main 후보 추가**
- 현재 코드 기준 표본 수: **37,632**
- 실행/저장 구조: **설계 완료**
- 독립 진단 케이스 스터디: **흑련 몰아주기 반응 1건 보존**
- 공식 연구 배치: **아직 실행하지 않음**
- 공식 결과 파일: **아직 없음**
