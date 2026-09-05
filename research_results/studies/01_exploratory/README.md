# 1연구 — 광범위 탐색 연구

## 역할

1연구는 Crown/Mast 운용의 보편적 최종 규칙을 확정하는 연구가 아니라, **대표적인 통제 조건에서 광범위한 조합을 탐색하여 우세 경향과 예외를 동시에 찾고 후속 연구 대상을 선별하는 연구**다.

현재 사전 테스트에서는 많은 조합에서 크크메 운용이 우세할 가능성이 확인되었지만, 일부 명확한 엣지케이스에서 단순한 Main 딜 지분만으로 결과를 설명하기 어렵다는 점이 드러났다. 따라서 1연구에서는 딜러 정체성, 성장 격차, 환경 조건 및 딜 구조에 따른 반응 차이를 넓게 기록한다.

## 현재 해석 범위

1연구에서 Crown과 Mast의 성장치는 대표 조건으로 통제한다. 따라서 결과는 다음 범위에서 해석한다.

> 고정된 대표 Crown/Mast 성장 조건에서, 현재 정의한 B1/Main/Secondary 성장 및 환경 조합을 비교했을 때 어떤 운용 경향과 예외가 나타나는가.

Crown/Mast 상대 성장 변화에 대한 일반화는 1연구의 직접 결론으로 확정하지 않는다. 1연구에서 관련 이상치가 발견되면 후속 연구에서 별도 민감도 또는 완전교차 실험으로 검증한다.

## 현재 후보군

```text
B1: 5명
liter
anis-star
moran-favorite-item
little-mermaid
rapi-red-hood

Main B3: 6명
rapi-red-hood
scarlet-black-shadow
cinderella
cinderella-crystal-wave
liberalio
neon-vision-eye

Secondary B3: 3명
epinel
helm
snow-white-heavy-arms
```

표본 구조:

- raw roster 90
- Rapi B1/Main 중복 3개 제외
- 87 valid rosters
- 16-point pairwise growth screening
- 12 environment conditions
- roster당 192 scenarios
- 전체 16,704 scenarios

`moran-favorite-item`, `scarlet-black-shadow`, `liberalio`는 후보에 포함되어 있으나 공식 실행 전에 model-specific gate를 다시 닫아야 한다.

## 디렉터리

```text
01_exploratory/
├─ human/       사람이 읽는 연구 문서
├─ machine/     승인 후 생성될 실행·원시·집계 데이터
└─ validation/  이 연구에 귀속되는 검증 자료
```

## 현재 상태

- 후보군 설계 재동결
- canonical study ID: `crown-mast-study-01-exploratory-v1`
- generator 후보군/식별자 정렬 완료
- 공식/대규모 batch 미실행
- 연구 실행 미승인
- Moran/SBS/Liberalio 재검증 필요

현재 실행 기준 문서는 `human/03_1연구_실행_설계_확정본.md`다.
