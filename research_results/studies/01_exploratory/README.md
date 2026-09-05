# 1연구 — 광범위 탐색 연구

## 역할

1연구는 Crown/Mast 운용의 보편적 최종 규칙을 확정하는 연구가 아니라, **대표적인 통제 조건에서 광범위한 조합을 탐색하여 우세 경향과 예외를 동시에 찾고 후속 연구 대상을 선별하는 연구**다.

## 현재 canonical 설계

```text
human/03_1연구_실행_설계_확정본.md
```

현재 후보군은 B1 5명 / Main B3 6명 / Secondary B3 3명이며, 라피 B1/Main 중복을 제외해 87 roster를 사용한다.

성장축은 `g1-base5-none`을 제외하고 다음 세 단계만 사용한다.

```text
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

B1/Main/Secondary를 3 × 3 × 3 완전교차하여 27 growth points를 구성한다. 환경축 12개와 결합하면 roster당 324 scenarios, 전체 28,188 scenarios다.

애장품 캐릭터는 SR15 canonical floor를 유지한다.

## 디렉터리

```text
01_exploratory/
├─ human/       사람이 읽는 연구 문서
├─ machine/     승인 후 생성될 실행·원시·집계 데이터
└─ validation/  이 연구에 귀속되는 검증 자료
```

## 현재 상태

- 후보군·성장설계 재동결
- 실행 미승인
- 공식/대규모 batch 미실행
- Moran/SBS/Liberalio 실행 전 model gate 재검증 필요
- 실제 run ID 및 결과 파일 없음

사용자의 별도 명시 승인 전에는 28,188 scenario batch를 실행하지 않는다.
