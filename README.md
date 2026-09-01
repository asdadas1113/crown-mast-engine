# Crown Mast Research Engine

NIKKE의 Crown + Mast: Romantic Maid 운용을 비교하기 위한 축소형 연구 엔진입니다.

현재 구현 범위:

- 기본 연구용 12 Full Burst 실측 시간축
- 첫 버스트 내부 타이밍 + 일정 버스트 간격으로 임의 개수 시간축을 만드는 생성기(14버스트 확장 준비)
- `Crown, Crown, Mast` 운용
- 지속 몰아주기 운용
- Maid Mast Drunken 1/2/3스택, 스택별 자기 평타 기대 적중 손실
- 3스택 Full Burst 종료 시 reset 및 Hangover 중 사격·무기 상태 정지
- Crown S1/Burst와 recovery trigger용 S2
- Maid Mast S1/S2/Burst 버프
- Boss DEF, DamageUp, Taken, Distributed, projectile 관련 기본 피해 버킷
- 시간별 버프 장부와 전투 이벤트 추적
- 버프 key·대상·스탯 인덱스와 공격 버프 단일 순회 해석
- JSON 기반 캐릭터 기본 스탯·무기·스킬 수치 카탈로그
- caster ATK 비율을 시전자 Static ATK 기준 flat ATK로 변환
- 장비 제외 Progression ATK와 슬롯별 Base-5/OL0/OL5 장비 조합
- 장비 본체와 독립된 11급 OL 공증·우코·장탄 줄 수 입력 및 무상한 극단값 실험
- R0~15·SR0~15 수집품의 flat ATK와 무기별 공격 효과, 애장품 캐릭터의 기본 SR15 적용
- 보스 속성과 캐릭터 속성에 따른 우월 자동 판정 및 OL 우코 적용
- OL 장탄과 스킬 장탄의 소스 그룹별 반올림, 첫 탄창·재장전 반영
- 비차지 및 일반 release형 SR/RL의 60 FPS 발사·장탄·재장전 상태 추적
- nikke-sim 기준 MG 풍업 래더와 재장전 중 풍다운
- 차지 속도의 감산식, 22f release recovery, 기본 차지 배율과 두 종류의 차지 피해 항
- 재장전 완료 시점의 동적 최대 장탄 계산과 버프 종료 후 남은 추가 탄환 보존
- 일반 공격 `DamageEvent`와 캐릭터별 피해 합계
- 고정 180초 전투와 마지막 풀버스트 이후 잔여 구간
- 피해 이벤트별 버스트 번호와 3버스트 단위 매크로 사이클
- 캐릭터별 예약 버프·전투 이벤트·공격 연동 스킬 훅 골격
- Rapi: Red Hood 기본 스탯·MG 일반 공격·풀버스트 자가 ATK 버프
- Rapi: Red Hood 로켓 미터, 부착·저장 폭발, 본인 B3 중 120→60 문턱 변경
- Rapi: Red Hood의 120회 공격 조건과 0.4초 지연 2808% B3 미사일
- Rapi: Red Hood의 작열 기본 상성과 전격 적 대상 추가 우월 및 OL 우코 적용
- Scarlet: Black Shadow 완충 3단계 S1, 분배 대미지, Full Burst 즉시 재장전·자가 버프
- Helm (애장품) 기본 스탯·SR 일반 공격·마지막 탄환 일반 공격 전용 치명타 버프
- Helm (애장품) 완충 회복 이벤트·178.98% 추가타·Full Burst 진입 팀 Attack Damage
- Helm (애장품) 8236.8% B3 피해와 재장전을 가로지르는 다음 10발 차지 배율 버프
- Liter 기본 스탯·SMG 일반 공격과 버스트 횟수별 누적형 팀 버프
- Liter 최대 장탄 +45.17%, 치명타 피해 +12.46%, ATK +14.42% 및 Burst ATK +66%
- Crown 일반 공격 43회 × Relax 20스택 자체 회복과 회복 시 팀 Attack Damage 갱신
- 아니스: 스타의 단독 B1 자가 ATK, Full Burst 팀 버프, 0.25초 Shooting Star,
  완충 추가타와 버스트 중 42f 고정 차지
- 목단 (애장품)의 20초 B1, 시전자 ATK 기준 팀 ATK 버프, 10초 SMG 무기 변경과
  변경 중 5타 추가 피해
- 리틀 머메이드의 상시 적 받는 피해, Full Burst/B1 Attack Damage, 부분 탄약 충전,
  Bubble Wave와 팀 탄약 500발당 Bubble Barrage
- 스노우 화이트: 헤비 암즈의 고정 차지, 상시 적 받는 피해, 풀차지 Auto Fire와
  자신의 B3에서 2발 한정 Fully Active 순차 공격
- 에피넬의 SMG 일반 공격, 마지막 탄환 치명타 버프와 무스택 단일 보스 B3
- 네온: 비전 아이의 무회복 완충 RL, 보스 완충 추가타, 화력 게이지와 초화력 주기
- 탄수 제한 무기 모드의 마지막 발 직후 기본 무기 복귀와 순차 공격 전용 DamageUp 항
- 0~100% 부분 탄약 충전과 캐릭터별 charge release recovery
- 수동 검증·극단값 실험용 캐릭터별 `element_multiplier_by_actor` override
- `CombatSettings`를 통한 Boss DEF·보스 속성·코어 적중률·사거리·우월 배율 설정
- 크크메와 지속 몰아주기의 통제 비교 및 메인 딜러 손익분기 분석
- 단일 계산 전용 크크메·진입 메크메·기본 몰아주기·진입 메스트 몰아주기 4회전 대칭 비교
- c1 B1 발동부터 첫 B2 선택의 활성 버프 상태가 다시 같아질 때까지 팀딜·캐릭터별 손익 진단
- 캐릭터·피해 종류·발생원·3버스트 매크로 사이클별 비교 결과
- 피해 이벤트 1회 순회 인덱스를 통한 비교 결과 집계
- `ResearchScenario` 기반 명시적 파티·장비·OL·보스·시간축 입력과 JSON 왕복
- `ComparisonReport` 기반 총딜·딜 비중·손익분기·사이클·발생원 출력
- 설정 가능한 동률권·미세 우위·명확한 우위 판정과 원시 증감률 분리
- 설치 의존성 없는 로컬 웹 인터페이스와 파티·슬롯별 장비·OL·보스 조건 입력
- 1버스트 육성 3단계와 딜러 장비 격차 4단계를 교차한 12점 배치 비교·산점도·JSON 보고서

## 가변 버스트 시간축

기본 `STANDARD_TIMELINE`은 기존 연구 재현을 위해 12버스트 그대로 유지한다. 실측 후
1버스트 내부 타이밍을 기준으로 이후 버스트를 일정 간격 이동시키는 실험은 다음처럼 만들 수 있다.

```python
from crown_mast_engine import build_uniform_burst_timeline

timeline = build_uniform_burst_timeline(
    cycle_count=14,
    interval_sec=12.0,  # 예시값. 실제 연구에는 실측값을 넣는다.
)
```

`Crown-Crown-Mast`와 지속 몰아주기 정책은 12사이클 뒤에도 같은 패턴을 계속 반복한다.
`CUSTOM_ROTATION`도 12 고정이 아니라 1부터 시작하는 임의 길이의 연속 사이클을 받는다.
다만 현재 웹 UI와 기존 기준점 보고서는 여전히 12버스트 기본 연구를 전제로 하며, 14버스트
실측값이 확정되기 전에는 기본값을 변경하지 않는다.

## 로컬 인터페이스

```powershell
python -m crown_mast_engine.interface --port 8765
```

브라우저에서 `http://127.0.0.1:8765`를 연다. B1·메인/서브 B3, 캐릭터별 장비 4슬롯,
수집품, T11 공증·우코·장탄 줄 수, 보스 방어력·속성·코어 적중률·적정 사거리 보너스를
입력할 수 있다. 단일 계산은 `크크메`, 첫 B2만 Mast로 바꾼 `진입 메크메`, `기본
몰아주기`, 첫 B2만 Mast로 바꾼 `진입 메스트 몰아주기`를 각각 한 번 계산한다. Crown
진입끼리와 Mast 진입끼리의 몰아주기 손익·메인 비중·손익분기를 분리하고, 비몰아주기와
몰아주기 각각의 진입 Mast 총딜 효과, 네 운용의 5인 딜·비중과 4개 매크로 사이클을 함께
제공한다. `기준점 지도 기준 운용` 선택은 단일 계산에 영향을 주지 않는다.
`기준점 지도 12점`은 선택한 편성에
1버스트 육성 3단계와 딜러 장비 격차 4단계를 교차 적용해 X축에 크크메 기준 Main B3
딜비중, Y축에 몰아주기-크크메 총딜 증감률을 표시한다. 종합보고서는 전체 판정, 증감률·
Main 비중·손익분기 범위, 극단값과 최근접점, B1·딜러 조건별 집계, 3×4 교차표, 캐릭터별
평균 비중 범위를 함께 제공한다. 점과 표를 선택하면 해당 사례의 총딜, `g/l`, local slope,
`lambda*`, 캐릭터별 실제 피해와 비중을 확인할 수 있다. 연구 조건·판정 임계값·엔진 규칙과
해석 한계도 결과에 기록되며 단일·배치 결과를 각각 JSON으로 저장할 수 있다. 종합보고서는
`보고서 PNG 저장`으로 그래프와 모든 근거표를 한 장의 긴 이미지로 내보낼 수 있다. PNG
렌더링은 프로젝트에 포함된 `html2canvas 1.4.1`을 사용하므로 외부 접속이 필요 없으며,
라이선스는 `crown_mast_engine/web/vendor/html2canvas.LICENSE.txt`에 보존한다.
웹 API는 별도 피해 계산식을 갖지 않는다. 단일 계산은 네 `SimulationResult`를 한 번씩
만든 뒤 기존 `compare_rotation_results()`와 `ComparisonReport` 집계를 재사용하며, 기준점
지도는 기존 `ResearchScenario`·`run_research_scenario()` 배치 경로를 그대로 사용한다.

단일 계산의 `첫 B2 선택 총영향`은 12버스트 합계와 별도인 보조 진단이다. 동일한 편성·
장비·보스 조건에서 첫 B2만 Crown 또는 Mast로 바꾼 두 결과를 계산하고, c1의 B1 발동
시각부터 두 결과의 활성 버프 상태가 처음 다시 같아지는 경계 직전까지 피해를 집계한다.
표준 시간축에서는 Crown B2의 15초 버프, Mast B2의 10초 버프와 첫 Full Burst Crown S1
대상 차이를 모두 포함해 `3.9 <= t < 20.1`이 된다. 팀 총딜과 5인별 `Mast - Crown`
차이를 제공하며 이 경계 이후의 공통 상태와 후속 운용 차이는 포함하지 않는다.

Rapi: Red Hood 구현 기준:

- 연구 조합처럼 별도 B1이 존재하는 B3 모드를 구현했다.
- Projectile Attachment +150.72%, Projectile Explosion +100.6%, 본인 B3 Attachment
  +421.2%는 해당 flavor의 `DamageUp` 버킷에만 가산한다.
- 로켓은 120 normal attack마다 발사하며, 본인 B3 사용 후 10초 동안만 문턱을 60으로
  낮춘다. 미터는 구간 경계에서 초기화하지 않는다.
- 부착과 폭발 계수는 pinned nikke-sim의 검증 완료 override에 따라 각각 88.11%를 사용한다.
  별도 계산기의 오래된 시나리오에 남은 폭발 49.71%는 사용하지 않는다.
- 부착 피해는 코어 가능, 저장 폭발과 B3 미사일은 코어 불가능으로 처리한다.
- 풀버스트 밖에서 부착된 로켓은 다음 풀버스트 진입 시 폭발하며, 전투 종료까지 다음
  풀버스트가 없으면 폭발하지 않는다.

Helm (애장품) 구현 기준:

- 일반 SR은 60f 완충 후 발사하며, 각 발사 뒤 22f release recovery를 거친다. 마지막 탄환은
  즉시 재장전에 들어가고 남은 release recovery는 재장전 완료 후 처리한다.
- 기본 차지 배율 250%에 버스트의 multiplier-class +158.4%를 적용하면 다음 10발은
  `2.5 + 2.5 * 1.584 = 6.46` 배율이 된다. 이 탄수 예산은 재장전으로 초기화하지 않는다.
- 마지막 탄환의 치명타 확률 +14.64%는 일반 공격에만 적용하며 스킬 추가타와 B3에는
  적용하지 않는다.
- 완충 공격마다 178.98% 추가타와 전원 회복 이벤트를 발생시켜 Crown S2를 갱신한다.
  회복량과 HP는 계산하지 않는다.
- B3의 8236.8% 피해는 Full Burst 진입 전에 발생하므로 Full Burst +50%를 받지 않는다.
- B3 흡혈 10초는 HP 모델 없이 recovery consumer만 재현하기 위해 1초 간격 10회 회복
  이벤트로 근사한다. Interruption Part +3.08%는 기록하지만 현재 partless 보스에서는
  피해에 적용하지 않는다.

Liter 구현 기준:

- 데이터상 SMG 명목 발사속도는 24발/초지만, pinned nikke-sim 런타임의 프레임 양자화
  기준에 따라 실제 상태기계에서는 3f 간격인 20발/초를 사용한다.
- B1 사용 시 첫 회부터 최대 장탄 +45.17%, 두 번째부터 치명타 피해 +12.46%, 세 번째부터
  ATK +14.42%를 이전 단계와 함께 5초 동안 적용한다.
- 별도의 Burst ATK +66%는 매 B1 사용 시 5초 동안 적용하며 S1의 ATK와 별도 키로 합산한다.
- 최대 장탄 증가는 현재 탄창에 즉시 탄환을 더하지 않는다. 버프가 살아 있는 동안 재장전이
  완료되면 증가한 최대치로 채우고, 이후 버프가 끝나도 이미 채워진 추가 탄환은 제거하지 않는다.
- Full Burst 진입 횟수별 CDR은 고정 시간축을 바꾸지 않는다는 연구 조건에 따라 수치만
  보존하고 스케줄에는 적용하지 않는다.
- S2는 유닛 HP 회복이 아닌 엄폐물 HP 복구이므로 회복 이벤트를 발생시키지 않으며 Crown
  S2를 발동하지 않는다.

신규 B1 구현 기준:

- 아니스: 스타는 단독 B1인 `나만의 별` 조건만 지원한다. Projectile Explosion +92.03%는
  현재 연구 편성의 공격 기여 캐릭터가 아니스보다 낮은 DEF라는 통제 가정으로 전원에게
  적용한다. 향후 동급/상위 DEF 캐릭터를 넣을 때는 DEF 기반 대상 판정이 필요하다.
- Shooting Star는 버스트 시전 즉시 첫 틱이 발생하는 0.25초 간격 40틱으로 처리하며,
  일반 공격식과 Projectile Explosion 버킷을 사용한다.
- 목단 (애장품)은 B1 시전부터 10초 동안 기본 AR을 멈추고 14.7% 계수의 무한 장탄
  SMG로 교체한다. 교체가 끝나면 기본 AR은 완충 상태로 복귀한다.
- 변경 무기는 CDN SMG 명목값인 24발/초를 잠정 기본값으로 사용한다. NIKKE.GG 구 가이드는
  20발/초, 2026년 영상 실측 요약은 10초 약 230발이므로 `weapon_swap_fire_rate`를
  카탈로그 입력값으로 두어 20/23/24발 민감도를 함께 검증한다.
- 변경 무기 일반 공격 5회마다 47.18% 추가 피해를 발생시킨다. 변경 세션마다 카운터를
  초기화하며, 추가 피해는 치명타·Full Burst·속성·Attack Damage 적용 대상이지만 일반
  공격 전용 Core·Range 적용 대상은 아닌 것으로 분류한다.
- Moris 공개판의 `self_state:무기 변경`과 실제 모드명 불일치로 5타 추가 피해가 누락되는
  경로는 사용하지 않는다. 카탈로그의 `weapon_swap_modeled = 1`이 현재 상태를 명시한다.
- 리틀 머메이드의 적 받는 피해 +5.05%는 단일 보스에게 상시 유지되는 것으로 처리한다.
  Bubble Wave는 Full Burst 시작 시점부터 1초 간격 10회, 각 63.36% × 4 순차 피해다.
  Bubble Barrage는 팀 전체 실제 탄약 소비 500발마다 85% × 10 순차 피해로 발생한다.
- 리틀 머메이드의 33.26% 탄약 충전은 발동 시점의 최대 장탄을 기준으로 더하며 최대치를
  넘지 않는다. CDR과 버스트 게이지 증가는 고정 시간축 연구이므로 스케줄에 반영하지 않는다.

스노우 화이트: 헤비 암즈 구현 기준:

- 단일 보스를 계속 완충 조준하는 연구 조건에서 Lock-On 대상의 받는 피해 +4.2%는 전투
  내내 유지되는 팀 공통 Taken 항으로 처리한다.
- 모든 풀차지에 41.9%와 `105.59% × 5 = 527.95%` 순차 공격을 발생시킨다. 자신의 B3
  Fully Active 2발에는 `105.59% × 10 = 1055.9%` 순차 공격을 추가한다.
- 기본 차지는 72f로 고정해 차지 속도 영향을 받지 않는다. Fully Active는 192f 차지로
  교체하고 2발째 직후 기본 차지 상태로 복귀한다. 10초 전체를 변경 무기로 채우지 않는다.
- Fully Active 2발의 차지 피해 +528%는 기본 250%에 가산해 778%가 된다. 순차 공격 피해
  +158.4%는 별도 최종 곱이 아니라 해당 두 발의 순차 공격에만 DamageUp 가산항으로 넣는다.
- 완충 시 ATK +46.84%는 발사 전에 적용되는 것으로 처리하며 5초 동안 갱신한다. B3 단계
  진입 ATK +73.92%는 다른 B3가 사용된 사이클에도 적용하고, Attack Damage +84.48%는
  자신의 B3 사용 후 10초 동안만 적용한다.
- 현재 partless 단일 보스 범위에서는 DEF +42.24%, 파츠 피해 +62.64%, 관통 다중 타격,
  Lock-On 대상 선택, 파괴 가능한 투사체 41.9% 피해를 계산하지 않는다. Fully Active 두 발은
  기본 SR 상태기계 안에서 같은 탄창과 재장전 상태를 공유하며 실제 탄약을 2발 소비한다.

네온: 비전 아이 구현 기준:

- 기본 RL은 61.3%, 코어 200%, 6발, reload 2초, 60f 완충과 250% 차지 배율이다.
  일반적인 RL과 달리 발사 후 charge release recovery가 없어 0% 차지 속도에서 재장전 전
  발사 간격은 정확히 60f다.
- 단일 stage target 보스를 계속 완충 조준하는 조건에서 매 발마다 437.98% `bonus_damage`를
  발생시킨다. 초화력 상태에서는 같은 발에 262.79% 추가 피해를 한 번 더 발생시킨다.
  두 추가타는 차지 배율·코어·사거리 항을 받지 않으며 치명타·속성·Full Burst·Attack Damage는
  적용받는다.
- 화력 게이지는 전투 시작 시 100이다. 자신의 B3 시전 시 100이면 즉시 모두 소비하여 10초간
  초화력이 되고, 100 미만이면 화력 충전 상태에서 즉시 1, 10초 동안 일반 공격마다 2,
  상태 종료 시 45를 충전한다. 실제 발사 횟수를 사용하며 게이지는 100에서 제한한다.
- 모든 Full Burst 진입 시 ATK +80.04%를 10초 적용하고, 초화력 상태라면 ATK +35.05%를
  추가한다. 자신의 B3는 항상 Attack Damage +110.21%, 초화력일 때 +45.03%를 더 적용한다.
- 표준 12버스트에서 Main B3 배치는 1·7사이클, Secondary B3 배치는 2·8사이클에 초화력이
  발동한다. 피격 기반 무적·해로운 효과 면역·회복량 증가는 피격/HP 모델이 없어 제외하고,
  폭발 범위와 게이지 비례 Burst Gauge 충전 속도는 partless·고정 시간축에서 제외한다.
- 2026-09-01 Moris 계산기 소스의 동일 5인 편성 교차검증에서 Main B3 초화력이
  1·7·13사이클에 발동하여 `초화력 1회 → 충전 2회` 상태 주기가 일치했다. 해당 계산기는
  180초에 14버스트이고 캐릭터별 장비·차지 속도·조작 레이어를 포함하므로 총딜과 발사 수는
  일치 판정에 사용하지 않는다. 단독 실행에서는 모든 완충탄에 `화력 폭발 1`이 1:1로
  발생하는 것도 확인했다.

에피넬 구현 기준:

- 기본 SMG는 10.12%, 코어 250%, 120발, reload 81f이며 현재 공통 SMG 상태기계의
  프레임 양자화에 따라 실효 20발/초로 발사한다.
- 마지막 탄환이 적중한 다음 프레임부터 자신에게 치명타 확률 +5.05%와 치명타 피해
  +6.4%를 5초 동안 적용한다. 발동시킨 마지막 탄환 자체에는 새 버프를 소급하지 않는다.
- 자신의 B3 시전 시 단일 보스에게 457.87% Burst 피해를 1회 발생시킨다. Full Burst 진입
  전에 발생하므로 Full Burst +50%를 받지 않는다.
- 현재 전투는 처치할 수 없는 단일 보스만 존재하므로 `Total Noob` 처치 스택은 0이다.
  따라서 ATK +13.86% × 5와 최대 스택 조건부 457.87% 추가타도 발동하지 않는다. 이는
  저점 극단 비교군을 위한 단일 보스 결과이며, 적이 여럿 등장하는 콘텐츠의 에피넬을
  대표하지 않는다.

아직 구현하지 않은 범위:

- 아니스: 스타 Projectile Explosion 버프의 실제 DEF 비교 대상 판정
- 적 처치 이벤트와 에피넬 `Total Noob` 스택을 포함한 다수전 상태
- Rapi: Red Hood의 무B1 Combat Assist·Stage 1 운용과 Interruption Part 보너스
- CDR과 Burst Gauge에 따른 스케줄 합법성
- Part와 시간에 따라 변하는 Range·Element 노출률
- 보스 패턴 시간 마스크

## 신규 B1 통제 비교

편성은 `B1 / Crown / Mast: Romantic Maid / Rapi: Red Hood / Helm (애장품)`, 몰아주기
대상은 Rapi: Red Hood다. Base-5, Boss DEF 140, Core/Range/Element/Part OFF, 고정 180초
시간축이며 아래 값은 UI 입력기 구축 전의 회귀용 표본이다.

| B1 | 크크메 총딜 | 몰아주기 총딜 | 몰아주기 증감 | 크크메 라피 비중 | 손익분기 라피 비중 |
|---|---:|---:|---:|---:|---:|
| Anis: Star | 2,600,118,188 | 2,561,914,248 | -1.4693% | 38.9125% | 75.3296% |
| Moran (Favorite Item), 24발/초 | 2,175,704,357 | 2,142,757,991 | -1.5143% | 39.7070% | 75.4517% |
| Little Mermaid | 2,417,673,269 | 2,385,302,207 | -1.3389% | 37.4893% | 65.1289% |

Anis: Star의 크크메 캐릭터별 딜 비중은 Anis 26.5162%, Crown 9.0554%, Mast 4.0783%,
Rapi 38.9125%, Helm 21.4376%다. Little Mermaid는 각각 28.4625%, 8.2784%, 3.8065%,
37.4893%, 21.9633%다.

목단 24발/초의 크크메 캐릭터별 딜 비중은 Moran 21.8909%, Crown 9.4341%,
Mast 4.2118%, Rapi 39.7070%, Helm 24.7561%다. 몰아주기는 각각 21.9154%,
9.3390%, 4.3312%, 40.7368%, 23.6776%다. 연사 민감도는 다음과 같다.

| 변경 무기 연사 | 크크메 총딜 | 몰아주기 총딜 | 몰아주기 증감 | 손익분기 라피 비중 |
|---:|---:|---:|---:|---:|
| 20발/초 | 2,101,541,028 | 2,069,605,894 | -1.5196% | 76.0721% |
| 23발/초 | 2,157,742,200 | 2,125,063,408 | -1.5145% | 75.5883% |
| 24발/초 | 2,175,704,357 | 2,142,757,991 | -1.5143% | 75.4517% |

## 운용 비교 분석

`analyze_rotations()`는 같은 편성·스탯·장비·보스 설정·시간축으로 선택 기준 운용과 지속
몰아주기를 각각 계산한다. 기본 기준은 크크메이며 `conventional_policy`에
`OPENING_MAST_CROWN_MAST`를 전달하면 첫 매크로 사이클만 메크메로 계산한다. 메인 딜러
피해를 `R`, 나머지 네 명의 피해를 `O`로 두고
다음 값을 제공한다.

```text
g = R_F / R_C - 1
l = 1 - O_F / O_C
lambda* = -(O_F - O_C) / (R_F - R_C)
s_C* = lambda* R_C / (lambda* R_C + O_C) = l / (g + l)
```

`STANDARD_BREAK_EVEN`은 몰아주기에서 메인 딜러는 이득이고 나머지는 손해인 일반적인
손익분기 사례다. `FUNNEL_DOMINATES`, `CONVENTIONAL_DOMINATES`,
`REVERSE_BREAK_EVEN`, `EQUAL`에서는 부호에 맞는 별도 판정을 사용하며, 우세가 확정된
사례에 억지로 손익분기값을 표시하지 않는다.

```python
from crown_mast_engine import (
    analyze_mast_expected_hit_loss_sensitivity,
    analyze_rotations,
)

comparison = analyze_rotations()
overall = comparison.overall

print(overall.team_c, overall.team_f)
print(overall.g, overall.l)
print(overall.local_slope, overall.local_extreme_upside)
print(overall.comparison_case, overall.break_even_direction)
if overall.has_share_break_even:
    print(overall.require_break_even_main_share_c())
print(comparison.by_character)
print(comparison.macro_cycles)
print(comparison.burst_cycles)
print(comparison.secondary_b3_mast3_burst_omission_cycles)
print(comparison.secondary_b3_mast3_burst_omission_cycle_damage)

for loss, result in analyze_mast_expected_hit_loss_sensitivity().items():
    print(loss, result.overall.team_relative_change)
```

현재 기본 편성 Liter / Crown / Mast: Romantic Maid / Rapi: Red Hood /
Helm (애장품), Base-5 장비, Helm SR15 수집품, Boss DEF 140 기준 결과는 다음과 같다.

```text
크크메 총피해               2,144,196,385.51
지속 몰아주기 총피해       2,118,326,068.35
총피해 증감률               -1.2065%
Rapi 피해 증가율 g          +1.4604%
나머지 피해 손실률 l        3.5213%
local slope g+l              4.9817%
크크메 기준 Rapi 실제 비중  46.4652%
손익분기 메인 비중 s_C*     70.6844%
손익분기 메인 스케일 lambda* 2.7780
Helm c6/c12 3스택 Mast Burst 미사용 구간 피해 차이  37,149,562.66 (18.4686%)

캐릭터                    크크메 비중    몰아주기 비중
Liter                       7.9491%          7.9475%
Crown                      10.1917%         10.0073%
Mast: Romantic Maid         4.5288%          4.6234%
Rapi: Red Hood             46.4652%         47.7195%
Helm (Favorite Item)       30.8652%         29.7023%
```

Mast의 Hit Rate 감소는 범용 탄착 시뮬레이션이 아니라 pinned NIKKE Sim의 표본 검증
근사와 동일하게 `normal_attack_pct = -20% × live Drunken stack`으로 처리한다. 따라서
Mast 자신의 일반 공격 기대피해에만 적용되며 공통 `core_hit_rate_pct`를 변경하지 않는다.

기본 민감도 sweep 결과:

```text
기대손실/stack   몰아주기 증감률   break-even Main B3 share
0%               -1.4000%          71.7239%
18%              -1.2266%          70.7992%
20%              -1.2065%          70.6844%
22%              -1.1863%          70.5669%
```

Secondary B3를 Scarlet: Black Shadow로 교체한 첫 provisional 표본:

```text
크크메 총피해                    2,101,149,975.23
지속 몰아주기 총피해            2,094,367,146.98
몰아주기 증감률                 -0.3228%
Rapi 비중                        38.6009%
Scarlet: Black Shadow 비중       43.7389%
손익분기 Main B3 비중            49.0744%
c6/c12 3스택 Mast Burst 미사용 구간 피해 차이  16,684,686.29 (5.8093%)

캐릭터                    크크메 비중    몰아주기 비중
Liter                       6.1720%          6.1227%
Crown                       7.9430%          7.7294%
Mast: Romantic Maid         3.5452%          3.5795%
Rapi: Red Hood             38.6009%         39.3338%
Scarlet: Black Shadow      43.7389%         43.2347%
```

흑련의 S1은 pinned NIKKE Sim과 동일하게 일반 구간에서는 완충 3회마다, 본인 B3 후
10초에는 완충 1회마다 세 단계가 순환하는 모델이다. 정확한 버스트 중 proc cadence와
분배 추가타의 치명타·Full Burst·속성 적용은 원본에서도 미확정이므로 이 결과는 규칙
민감도 검증 전까지 provisional로 취급한다.

Helm이 없는 이 표본에서는 Crown이 일반 공격 860회마다 자체 회복하고 S2를 갱신한다.
현재 180초 시간축에서는 크크메와 몰아주기 양쪽 모두 동일한 시각에 8회 발동한다.

`lambda*`는 다른 모든 피해 이벤트를 고정한 채 현재 메인 딜러 피해 성분만 배율 조정하는
국소 민감도 지표다. 실제 장비·스킬 수치를 2.7476배로 만들라는 뜻은 아니다. 캐릭터가
바뀌면 공격 횟수, 버프 수혜, 스킬 발동과 피해 구성도 함께 달라지므로 새 캐릭터 구현으로
다시 시뮬레이션해야 한다.

`ComparisonReport` schema v3는 이 전제를 `break_even_methodology`에도 기록한다.
내부 `ResearchScenario` schema v2는 `baseline_rotation`을 저장하며, 기존 schema v1 입력은
`crown_crown_mast`로 마이그레이션한다.
`local_main_damage_scaling`은 C/F의 메인 딜러 피해만 같은 `lambda`로 조정하고, 비메인 피해,
이벤트 시각, 버프 창과 스킬 발동은 고정한다. 보고되는 비중은 그 국소 손익분기점에서의
크크메 총딜 대비 메인 딜러 비중이다.

전체 손익분기는 12버스트 합계로 계산한다. `macro_cycles`는 세 번의 버스트씩 나눈 네
구간의 차이를 보여주는 진단값이며, 구간별 손익분기값을 단순 평균해 전체 손익분기로
사용하지 않는다.

`break_even_main_share_c`는 `STANDARD_BREAK_EVEN` 또는 `REVERSE_BREAK_EVEN`이면서
메인·비메인 기준 피해가 모두 유효할 때만 제공한다. 지배우위·동률 또는 0 기준값 사례에서는
`has_share_break_even`이 `False`이며, `require_break_even_main_share_c()`는 판정 유형을
포함한 `ValueError`를 발생시킨다. 결과 출력기는 임의로 `None`을 백분율로 변환하지 않고
`comparison_case`와 `break_even_direction`을 먼저 확인해야 한다.

각 `SimulationResult`는 `engine_rule_revision`, skill-hook revision, 등록된 hook factory
목록으로 구성된 `mechanics_signature`를 저장한다. `compare_rotation_results()`는 이 값이
다른 두 결과를 통제된 C/F 쌍으로 비교하지 않고 거부한다. 엔진 공통 규칙을 변경하면
`ENGINE_RULE_REVISION`을, 표준 캐릭터 hook 구성을 변경하면 `standard-hooks-rN`을 함께
갱신한다. 별도 `SkillHookRegistry`를 재사용할 때는 의미 있는 `revision`을 지정한다.

`BuffBook`은 같은 key가 같은 시각에 refresh되면 기존 window를 0초로 닫아 남기지 않고
새 window로 교체한다. 직접 입력된 `start == end` window는 기록하지 않으며,
`end < start` window는 잘못된 입력으로 거부한다.

### 결과 보고 규약

덱 계산이나 비교 테스트 결과를 기록할 때는 최소한 다음을 함께 명시한다.

```text
편성: B1 / Crown / Mast / Main B3 / Secondary B3
몰아주기 대상: main_actor
캐릭터별 딜 비중: 크크메 비중 / 몰아주기 비중
```

캐릭터 이름만 나열하지 않고 각 Burst 역할을 표시한다. 기본 편성이라도 생략하지 않으며,
5인 전원의 딜 비중을 생략하지 않는다. 우월·Boss DEF·전투시간처럼 기본값과 다른 공통
조건이 있으면 같은 결과 블록에 기록한다.

## 후속 연구: 2스택 메스트

2스택 메스트는 반복 운용이나 180초 총딜 최적화가 아니라, 3스택 메스트를 사용할 예정인
풀버스트에 보스 패턴으로 인한 딜로스가 예상될 때 사용하는 국소적인 대응으로 연구한다.

기본 비교 단위는 동일한 세 번의 버스트다.

```text
기준 운용: Crown -> Crown -> 3스택 Mast (크크메)
대안 운용: Crown -> 2스택 Mast -> Crown (크메크)
```

- 두 운용은 반드시 같은 사이클 시작 상태에서 분기한다.
- 딜로스는 세 번째 풀버스트 구간에 적용한다.
- 2스택 Mast가 Drunken을 초기화하지 않는다는 종료 상태는 기록하되, 기본 손익분기에는
  이후 180초 피해를 합산하지 않는다.
- 버프가 풀버스트 종료 후에도 남을 수 있으므로 사이클 경계와 잔여 버프 처리 규칙을
  양쪽 운용에 동일하게 적용한다.

현재 피해 이벤트의 사이클 귀속은 첫 B1 이전을 1번, 각 B1부터 다음 B1 직전까지를 해당
버스트 번호, 12번 B1 이후 180초 종료까지를 12번으로 기록한다. 후속 손익분기 분석에서는
이 기록을 이용하되, 비교 목적에 맞는 시작·종료 경계와 잔여 버프 포함 범위를 별도로
고정해야 한다.

12버스트는 세 번씩 네 개의 매크로 사이클로 나눈다. 실제 타임라인 계산에서는 잔여 버프,
탄창과 재장전 상태, MG 풍업, 공격 간격, 지연 피해, 첫 전투 진입과 종료 경계 때문에 같은
운용도 매크로 사이클별 피해가 달라질 수 있다. 따라서 각 매크로 사이클 시작 상태 `S_i`를
보존하고, 그 상태에서 두 운용을 각각 계산한다.

```text
S_i -> CCM
S_i -> CMC
```

각 사이클의 로스율 `L`에 대한 피해 차이는 다음과 같이 둔다.

```text
delta_i(L) = D_CMC_i(L) - D_CCM_i(L)
```

대표 손익분기율은 사이클별 손익분기율을 단순 평균하지 않는다. 네 사이클의 피해량 또는
`delta_i(L)`를 먼저 합산/평균한 뒤, 평균 피해 차이가 0이 되는 `L`을 구한다. 사이클별
손익분기율과 최솟값·최댓값은 결과의 변동 폭을 보여주는 보조 통계로 제공한다.

이 분석 기능은 기본 계산기와 캐릭터별 공격·스킬 이벤트 구현 이후 추가한다. 재작업을
피하기 위해 모든 피해 이벤트에는 발생 시각, 버스트 번호, 공격 주체와 피해 종류를
추적할 수 있어야 한다.

일반 공격 피해 계산:

```python
from crown_mast_engine import CROWN_CROWN_MAST, CombatSettings, simulate_rotation

result = simulate_rotation(
    CROWN_CROWN_MAST,
    combat_settings=CombatSettings(
        boss_def=140,
        core_hit_rate_pct=0,
        duration_sec=180,
    ),
)

print(result.damage_by_character)
```

연구 시나리오와 비교 보고서:

```python
from crown_mast_engine import ResearchScenario, run_research_scenario

scenario = ResearchScenario.standard()
scenario_json = scenario.to_json()
restored = ResearchScenario.from_json(scenario_json)

report = run_research_scenario(restored)
print(report.overall.team.to_dict())
print(report.overall.outcome_band.value)
print(report.to_json())
```

`ResearchScenario`는 파티원 전원의 장비 본체와 OL 옵션을 명시하도록 강제하고, 엔진·skill
hook·카탈로그 revision이 실행 환경과 다르면 계산을 거부한다. `ComparisonReport`의 판정은
원시 총딜과 증감률을 변경하지 않는 별도 해석 계층이다. 기본값은 `±0.1%`를 동률권,
`±0.5%` 이상을 명확한 우위로 분류하며 시나리오별로 변경할 수 있다.

표본 실행 자동화:

```python
from crown_mast_engine import SampleCase, run_sample_batch

batch = run_sample_batch((SampleCase("rapi-baseline", scenario),))
print(batch.results[0].summary_row())
```

`SampleBatchResult`는 각 사례의 전체 `ComparisonReport`와 함께 총딜, 증감률, `s`, `s*`,
`margin`, `lambda*`, `g/l`, 5인 딜 비중을 요약 행으로 제공한다. 격자 축과 표본 선정은
엔진에 고정하지 않으며, 현재 표본 수집 중단 기간에는 진단 실행에만 사용한다.

테스트 실행:

```powershell
python -m unittest discover -s tests -v
```

현재 전체 회귀 테스트는 196개이며, 주요 검증 항목은 다음과 같다.

테스트 프로세스에서는 완전히 동일한 기본 크크메·몰아주기 C/F 결과만
`tests/simulation_fixtures.py`에서 공유한다. 공유 결과는 읽기 전용으로 취급한다.
짧은 시간축, 다른 캐릭터·장비·보스 설정·카탈로그·skill hook을 사용하는 테스트는
상태 격리와 입력 검증을 위해 각각 독립 실행한다. 2026-08-31 기준 기본 fixture 최적화
직후 137개 suite는 공유 전 154.438초에서 공유 후 81.238초로 단축되었다. 현재
`ResearchScenario`와 `ComparisonReport`, 스노우 화이트: 헤비 암즈·에피넬 검증을 포함한
196개 suite로 네온: 비전 아이의 Secondary B3 초화력 주기, 수집품 효과와 웹 입력·배치
기준점 변환·종합 집계·PNG 내보내기, 네 회전 진입 비교와 첫 버스트 진단을 함께 고정한다.

- `크크메`와 지속 몰아주기 양쪽에서 Rapi의 일반 공격·로켓·미사일 이벤트 수 보존
- 진입 메크메의 B2 순서 `M-C-M / C-C-M / C-C-M / C-C-M`, 첫 Mast 1스택과 c3 reset
- 진입 메스트 몰아주기가 기본 몰아주기의 첫 B2만 Mast로 바꾸고 진입 메크메와 c1~c4를 공유
- 비몰아주기·몰아주기의 공통 진입 Mast 절대피해 변화 보존과 동일 진입끼리의 손익분기 분리
- 기존 scenario v1의 크크메 마이그레이션과 선택 회전의 JSON·단일·배치 입력 보존
- c1 B1 이상·첫 진입 버프 상태 수렴 미만 창의 Crown/Mast 팀딜과 캐릭터별 합계 보존
- 지속 몰아주기 c5/c11의 2스택 Mast 패키지와 이전 Crown 버프 잔여 시간 차이
- 팀 총피해와 캐릭터별·피해 종류별·4개 매크로 사이클별 합계 일치
- Rapi 로켓의 풀버스트 시작 전 저장, 풀버스트 중 즉시 폭발, 종료 경계 이후 재저장
- Rapi 본인 B3 사용 후 10초 동안만 로켓 문턱 120→60 적용
- 마지막 풀버스트 이후 저장된 로켓이 다음 폭발 없이 180초에 종료되는 보존 관계
- Helm SR의 완충·22f recovery·재장전 경계와 차지 속도 감산식
- R/SR 수집품의 flat ATK, 무기별 효과와 Helm·목단 애장품 기본 SR15 선택
- Helm 완충 1회당 178.98% 추가타 1회 및 회복 이벤트 발생
- Helm B3가 Full Burst +50%를 받지 않고 8236.8%로 발생하는 순서
- Helm B3의 158.4% multiplier-class가 재장전을 넘어 정확히 다음 10발에만 적용되는 관계
- 마지막 탄환 +14.64% 치명타가 일반 공격에만 적용되고 스킬·버스트에는 미적용되는 범위
- Liter SMG의 20발/초 프레임 경계와 최대 장탄 버프 중 재장전·종료 후 추가 탄환 보존
- Liter 1·2·3회 B1 사용 시 누적되는 최대 장탄·치명타 피해·ATK 단계와 정확한 5초 종료 경계
- Liter 엄폐물 복구가 Crown의 회복 발동 조건으로 전달되지 않는 관계
- 스노우 화이트: 헤비 암즈의 풀차지별 두 기본 라이더, 자신의 B3 2발 한정 추가 라이더,
  두 번째 발 직후 1.2초 차지 복귀, 기본 탄창·재장전 공유, 순차 공격 전용 DamageUp 적용 범위
- 에피넬의 120발 마지막 탄환 다음 프레임 치명타 창, 본인 B3 457.87% 단발,
  단일 불사 보스에서 처치 스택과 조건부 추가타가 0으로 유지되는 관계
- 라피: 레드 후드가 작열 기본 상성과 별개로 전격 적에게 우월 판정을 받아 OL 우코를
  적용받고, 같은 전격 적에게 철갑 아군도 기본 우월을 함께 받는 관계
- 목단 무기 변경의 24발/초·버스트당 240발, 세션별 48회 5타 추가 피해
- 목단 변경 무기 20/23/24발 민감도와 변경 종료 시 기본 AR 완충 복귀
- 손익분기 네 가지 부호 사례와 완전 동률 판정
- mechanics signature가 다른 C/F 결과의 비교 거부
- 같은 시각 buff refresh 병합과 0초·음수 duration window 처리
- 운용 비교의 캐릭터별·피해 종류별·발생원별 합계 보존
- 4개 매크로 사이클 합계 보존과 구간별 손익분기 변동
- 첫 B2 정책 분기 전 크크메·몰아주기 DamageEvent 완전 동일
- DamageEvent의 기록된 피해 요소 재곱과 최종 피해 일치
- 1버스트 육성 3단계 × 딜러 장비 격차 4단계의 12개 고유 배치 입력과 결과 집계
- 배치 증감률·비중 범위, 조건별 평균, 극단·손익분기 최근접 사례와 캐릭터 비중 집계
- 공통 피해 scalar 적용 시 절대피해만 비례하고 상대 분석값은 불변
- 173초 계산과 180초 계산의 173초 이전 DamageEvent prefix 동일

고정 기준 자료:

```text
nikke-sim commit 43308bd02276a476660e44af730785c2ae91eea3
```

인게임 수치와 메커니즘을 확정할 때는 고정 NIKKE Sim 구현, 최신 NIKKE.GG 자료,
Moris NIKKE 계산기 데이터·구현을 함께 확인한다. 세 자료가 충돌하면 임의로 하나를
정답으로 선택하지 않고 차이와 현재 연구에 미치는 영향을 먼저 기록한다.
