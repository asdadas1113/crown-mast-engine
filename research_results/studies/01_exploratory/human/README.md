# 1연구 사람용 문서

이 디렉터리는 1연구를 사람이 읽고 검토하기 위한 문서만 저장한다.

현재 문서 순서는 다음과 같다.

```text
01_연구_설계_초안.md
02_연구_실행_재현성_및_기록_규격.md
03_1연구_실행_설계_확정본.md
04_결과_요약.md              # 실행 후 작성
05_해석과_한계.md            # 실행 후 작성
06_후속_연구_후보.md         # 실행 후 작성
```

현재 canonical 실행 설계는 `03_1연구_실행_설계_확정본.md`다.

## 현재 설계 요약

```text
B1 5명
Main B3 6명
Secondary B3 3명
87 valid rosters
```

성장축은 `g1-base5-none`을 1연구에서 제외하고 다음 세 단계만 사용한다.

```text
g2-ol0-sr5
g3-ol0-sr15-e3-a3
g4-ol5-sr15-e4-a4-ammo3
```

B1/Main/Secondary를 `3 × 3 × 3` 완전교차하여 **27 growth points**를 사용한다.

환경축은:

```text
DEF 3 × core 2 × Main advantage 2 = 12
```

따라서 현재 예상 표본은:

```text
324 scenarios / roster
28,188 scenarios total
```

이다.

애장품 캐릭터는 SR15 canonical floor를 유지한다.

설계는 재동결됐지만 실제 연구 실행은 아직 승인되지 않았다. 또한 Moran Favorite Item / Scarlet: Black Shadow / Liberalio model gate와 clean full regression이 남아 있다.

결과 문서는 실제 연구 실행 전에는 만들지 않으며 빈 결과를 기입하지 않는다.

## 문서 작성 원칙

- 제목과 본문은 한글을 기본으로 한다.
- 관측된 결과와 해석을 분리한다.
- 1연구의 통제 범위를 넘어선 일반화를 피한다.
- 사전 예상이나 과거 archive 결과를 새 결과처럼 기재하지 않는다.
- 특이 결과는 후속 연구 후보로 기록하되, 기전은 별도 검증 전 확정하지 않는다.
- 과거 검증 문서의 superseded 표본 수를 현재 설계값처럼 재사용하지 않는다.
- 정식 실행 결과에는 해당 run의 manifest와 validation 기록을 반드시 연결한다.

사용자의 별도 명시 승인 전에는 28,188 scenario aggregate를 실행하지 않는다.
