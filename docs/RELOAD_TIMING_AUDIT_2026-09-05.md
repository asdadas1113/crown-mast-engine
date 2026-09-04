# 재장전 시간축 교차검증 — 2026-09-05

## 목적

Crown–Mast 연구 엔진에서 `reload_frames`와 런타임 재장전 보정이 같은 숨은 시간을 두 번 포함할 가능성을 점검했다. 이 문서는 공식 연구 재실행 전 확정된 수정과 보류한 항목을 분리한다.

## 확정한 공용 규칙

`WeaponProfile.reload_frames`는 **인게임에 표시되는 기본 재장전시간을 60 FPS 프레임으로 환산한 raw body**로 정의한다. 런타임은 여기에 기존 `effective_reload_frames()`의 `×0.975`와 고정 `+13f`를 적용한다. 따라서 nikke-sim에서 합성된 `81/111/141/171f`를 그대로 넣고 다시 `+13f`를 적용하던 혼합 정의는 사용하지 않는다.

직접 계측 근거는 Ore-game의 reload-limit 분석(`https://ore-game.com/nikke/post/reload-limit/`)이며, 현행 Moris/Jgaram 계산기는 캐릭터 데이터의 표시 `reload_time`을 재장전 본체 입력으로 사용한다. Prydwen의 최신 캐릭터 페이지에서도 이번에 정규화한 캐릭터들의 표시 재장전시간을 교차확인했다. NIKKE.gg의 Crown/Mast 및 관련 캐릭터 분석은 고속 재장전의 실제 영향과 특수 재장전 사례를 추가 확인하는 용도로 사용했다.

0% 재장전속도에서 현재 식의 기준점은 다음과 같다.

- 표시 1.0초 (`60f`) → `72f`
- 표시 1.5초 (`90f`) → `101f`
- 표시 2.0초 (`120f`) → `130f`
- 표시 2.5초 (`150f`) → `159f`

## 이번에 정규화한 캐릭터

- Liter: 1.5초 → 90f
- Crown: 2.5초 → 150f
- Mast: Romantic Maid: 2.5초 → 150f
- Rapi: Red Hood: 2.5초 → 150f
- Helm: 2.0초 → 120f
- Anis: Star: 2.0초 → 120f
- Little Mermaid: 1.0초 → 60f
- Snow White: Heavy Arms: 2.0초 → 120f
- Epinel: 1.0초 → 60f
- Neon: Vision Eye: 2.0초 → 120f
- Cinderella: 2.0초 → 120f
- Cinderella: Crystal Wave: 일반 MG 재장전 2.5초 → 150f
- Phantom (Favorite Item): 2.0초 → 120f
- Bready: 2.0초 → 120f
- Quency: Escape Queen: 1.0초 → 60f

CCW는 MG-only 연구 범위다. NIKKE.gg/Prydwen이 구분하는 두 번째 모드전환용 3.0초 고정 재장전은 현재 연구 모델에 들어오지 않으므로 일반 2.5초 재장전만 정규화했다.

## 확인 후 변경하지 않은 항목

### Scarlet: Black Shadow
표시 재장전 2.0초와 별개로 실제 자동발사·재장전 동작이 특수하다. 기존 152f를 단순 120f로 바꾸기에는 직접 계측과 데이터 정의가 완전히 합치하지 않아 유지했다.

### Raven
표시값과 실제 RL 동작 간 특수 지연을 분해할 독립 근거가 부족하므로 유지했다.

### Liberalio
표시 2.0초는 확인되지만 Moris에 별도 post-reload 0.5초 예외가 존재한다. 어느 부분이 기본 재장전이고 어느 부분이 캐릭터 고유 복귀시간인지 독립적으로 확정되지 않아 유지했다.

### Moran (Favorite Item)
최신 Prydwen 표기와 기존 datamine의 재장전시간이 충돌한다. 수정하지 않았다.

### Milk: Blooming Bunny
현재 Crown 연구는 AUTO 기준이며 특수 수동/강제 재장전 경로를 모델링하지 않는다. 이번 공용 수정에서 제외했다.

### 100% 초과 재장전속도
Ore-game/Prydwen은 약 109~110%까지 추가 단축·perfect reload 동작을 보고하지만 현행 Moris와 Crown은 100%에서 body를 0으로 clamp한다. 구현 간 해석이 갈리므로 **이번에는 런타임 식을 수정하지 않았다.**

### 공용 post-reload 11f 및 차지 마지막 탄 겹침
Prydwen의 last-shot→first-shot 계측과 Ore-game의 세분화는 추가 공격불가시간이 있음을 시사하지만, Moris는 SG 외 무기군에 이를 공용값으로 일반화하지 않는다. 따라서 새 공용 post-reload delay를 추가하지 않았다. 또한 Helm 기준 6발+재장전 약 10.4초 실측은 현재의 차지 회복+재장전 직렬 총시간과 잘 맞으므로 마지막 탄 회복을 재장전과 겹치게 바꾸지 않았다.

## 영향

대표 legacy 비교에서 break-even main share가 약 0.7206에서 0.6733으로 이동했다. RAID14의 Mast opener 상대 이득은 약 2.43%에서 2.52%로 이동했다. 이는 공통 스케일만 바뀐 것이 아니라 재장전속도 버프와 캐릭터별 탄창 주기가 정책 간 상대값에 들어가기 때문이다.

공식 29,952-scenario 연구 배치는 이 수정 검증 과정에서 실행하지 않았다.
