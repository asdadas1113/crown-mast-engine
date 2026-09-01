from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, got {count}: {old[:80]!r}")
    write(path, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Core primitives found necessary by cross-source audit.
# ---------------------------------------------------------------------------
replace_once(
    "crown_mast_engine/damage.py",
    "    core_eligible: bool = True\n    element_eligible: bool = True\n",
    "    core_eligible: bool = True\n    forced_core: bool = False\n    element_eligible: bool = True\n",
)

replace_once(
    "crown_mast_engine/combat.py",
    "    sequential_damage_pct: float = 0.0\n    sequential_multiplier: float = 1.0\n",
    "    sequential_damage_pct: float = 0.0\n    sequential_multiplier: float = 1.0\n    coefficient_multiplier_stat: str | None = None\n",
)

replace_once(
    "crown_mast_engine/engine.py",
    "        core_bonus_pct = self.combat_settings.core_hit_rate_pct * (\n            definition.weapon.core_attack_pct\n",
    "        core_rate_pct = (\n            100.0 if request.traits.forced_core\n            else self.combat_settings.core_hit_rate_pct\n        )\n        core_bonus_pct = core_rate_pct * (\n            definition.weapon.core_attack_pct\n",
)
replace_once(
    "crown_mast_engine/engine.py",
    "        coefficient_pct = request.coefficient_pct\n        if request.category == DamageCategory.NORMAL:\n",
    "        coefficient_pct = request.coefficient_pct\n        if request.coefficient_multiplier_stat is not None:\n            coefficient_pct *= result.buff_total(\n                request.time,\n                request.actor,\n                request.coefficient_multiplier_stat,\n            )\n        if request.category == DamageCategory.NORMAL:\n",
)
replace_once(
    "crown_mast_engine/engine.py",
    "            coefficient_pct=request.coefficient_pct,\n            traits=request.traits,\n            breakdown=breakdown,\n",
    "            coefficient_pct=coefficient_pct,\n            traits=request.traits,\n            breakdown=breakdown,\n",
)

# ---------------------------------------------------------------------------
# Rapi: Red Hood — add the no-separate-B1 Combat Assist branch.
# CDR is deliberately not fed back into the externally measured RAID14 timeline.
# ---------------------------------------------------------------------------
write(
    "crown_mast_engine/character_mechanics/rapi_red_hood.py",
    '''from __future__ import annotations

from math import inf

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RapiRedHoodSkillHook(SkillHookBase):
    """Formation-branched Rapi: Red Hood implementation.

    Cross-checked against pinned nikke-sim, Moris parsed skills, and NIKKE.gg.
    When Rapi occupies the B1 slot herself, Combat Assist is active: she supplies
    the B1 cast and the team Full-Burst Attack-Damage buff instead of the 95.04%
    self-ATK Full-Burst buff. Her 7.48s team CDR and 20s self B1 CDR are real kit
    lines, but this Crown-Mast study intentionally keeps its externally measured
    RAID14 timestamps fixed, so those two timing effects do not move the timeline.
    """

    COMBAT_ASSIST_TEAM_CDR_SEC = 7.48
    COMBAT_ASSIST_ATTACK_DAMAGE_PCT = 8.02
    B1_SELF_CDR_SEC = 20.0
    B1_CASTER_ATK_PCT = 18.01
    COMBAT_ASSIST_DURATION_SEC = 10.0

    def __init__(self, context: SkillHookContext) -> None:
        self._combat_assist = context.roster.b1 == context.actor
        self._pulls = 0
        self._rocket_meter = 0
        self._stored_rockets = 0
        self._own_stage3_until = 0.0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs = [
            BuffWindow(
                source=context.actor,
                skill="skill2_passive",
                stat="projectile_attachment_pct",
                value=context.definition.skill_value(
                    "skill2", "projectile_attachment_pct"
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
            BuffWindow(
                source=context.actor,
                skill="skill2_passive",
                stat="projectile_explosion_pct",
                value=context.definition.skill_value(
                    "skill2", "projectile_explosion_pct"
                ),
                target=context.actor,
                start=0.0,
                end=inf,
            ),
        ]
        targets = tuple(dict.fromkeys(context.roster.members))
        for event in events:
            if (
                event.event_type == EventType.B1_CAST
                and event.actor == context.actor
                and self._combat_assist
            ):
                for target in targets:
                    buffs.append(
                        BuffWindow(
                            source=context.actor,
                            skill="burst_stage1",
                            stat="caster_atk_pct",
                            value=self.B1_CASTER_ATK_PCT,
                            target=target,
                            start=event.time,
                            end=event.time + self.COMBAT_ASSIST_DURATION_SEC,
                            caster=context.actor,
                            snapshot=True,
                        )
                    )
                continue

            if event.event_type == EventType.FULL_BURST_ENTER:
                if self._combat_assist:
                    for target in targets:
                        buffs.append(
                            BuffWindow(
                                source=context.actor,
                                skill="skill1_combat_assist",
                                stat="attack_damage_pct",
                                value=self.COMBAT_ASSIST_ATTACK_DAMAGE_PCT,
                                target=target,
                                start=event.time,
                                end=event.time + self.COMBAT_ASSIST_DURATION_SEC,
                            )
                        )
                else:
                    buffs.append(
                        BuffWindow(
                            source=context.actor,
                            skill="skill1_full_burst",
                            stat="atk_pct",
                            value=context.definition.skill_value("skill1", "atk_pct"),
                            target=context.actor,
                            start=event.time,
                            end=event.time
                            + context.definition.skill_value("skill1", "duration_sec"),
                        )
                    )
            elif (
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == context.actor
            ):
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_stage3",
                        stat="projectile_attachment_pct",
                        value=context.definition.skill_value(
                            "burst", "projectile_attachment_pct"
                        ),
                        target=context.actor,
                        start=event.time,
                        end=event.time
                        + context.definition.skill_value("burst", "duration_sec"),
                    )
                )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type == EventType.B3_STAGE_ENTER
            and event.actor == context.actor
        ):
            self._own_stage3_until = event.time + context.definition.skill_value(
                "burst", "duration_sec"
            )
            if self._pulls < context.definition.skill_value("burst", "required_pulls"):
                return ()
            return (
                DamageRequest(
                    time=round(
                        event.time
                        + context.definition.skill_value("burst", "delay_sec"),
                        6,
                    ),
                    actor=context.actor,
                    source="burst_stage3_missile",
                    category=DamageCategory.BURST,
                    coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
                    traits=DamageTraits(
                        category=DamageCategory.BURST,
                        core_eligible=False,
                        range_eligible=False,
                    ),
                ),
            )

        if event.event_type != EventType.FULL_BURST_ENTER or self._stored_rockets == 0:
            return ()
        stored = self._stored_rockets
        self._stored_rockets = 0
        return (self._explosion_request(event.time, stored, context),)

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()
        self._pulls += 1
        self._rocket_meter += 1
        threshold = int(
            context.definition.skill_value(
                "skill2",
                (
                    "own_burst_attack_count"
                    if shot.time < self._own_stage3_until
                    else "normal_attack_count"
                ),
            )
        )
        effects: list[SkillEffect] = []
        while self._rocket_meter >= threshold:
            self._rocket_meter -= threshold
            effects.append(
                DamageRequest(
                    time=shot.time,
                    actor=context.actor,
                    source="skill2_rocket_attachment",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2", "attachment_damage_pct"
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.SKILL,
                        projectile_attachment=True,
                        core_eligible=True,
                        range_eligible=False,
                    ),
                    shot_index=shot.shot_index,
                    magazine_index=shot.magazine_index,
                )
            )
            if self._is_full_burst(shot.time, context):
                effects.append(self._explosion_request(shot.time, 1, context))
            else:
                self._stored_rockets += 1
        return tuple(effects)

    @staticmethod
    def _is_full_burst(time: float, context: SkillHookContext) -> bool:
        return any(
            cycle.full_burst_start <= time < cycle.full_burst_end
            for cycle in context.timeline
        )

    @staticmethod
    def _explosion_request(
        time: float,
        rockets: int,
        context: SkillHookContext,
    ) -> DamageRequest:
        return DamageRequest(
            time=time,
            actor=context.actor,
            source="skill2_rocket_explosion",
            category=DamageCategory.SKILL,
            coefficient_pct=(
                context.definition.skill_value("skill2", "explosion_damage_pct")
                * rockets
            ),
            traits=DamageTraits(
                category=DamageCategory.SKILL,
                projectile_explosion=True,
                core_eligible=False,
                range_eligible=False,
            ),
        )
''',
)

# ---------------------------------------------------------------------------
# Raven — one refreshing, stack-scaled DoT state (not independent 5s DoTs).
# ---------------------------------------------------------------------------
write(
    "crown_mast_engine/character_mechanics/raven.py",
    '''from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class RavenSkillHook(SkillHookBase):
    """Single stage-target boss implementation of Raven.

    Shock Wave is one target DoT state: each Full Charge adds one stack up to 10
    and refreshes the whole state's 5s duration. Its 1s tick reads the live stack
    count. This matches Moris' max_stack + scaling=stack_count representation and
    NIKKE.gg's explicit add-stack-and-refresh description.
    """

    _STACK_STAT = "raven_sustained_stack_count"

    def __init__(self, context: SkillHookContext) -> None:
        self._sustained_stacks = 0
        self._sustained_until = 0.0
        self._next_dot_tick: float | None = None
        self._scheduled_ticks: set[float] = set()

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        return tuple(
            BuffWindow(
                source=context.actor,
                skill="skill1_full_burst",
                stat="caster_atk_pct",
                value=context.definition.skill_value(
                    "skill1", "full_burst_caster_atk_pct"
                ),
                target=context.actor,
                start=event.time,
                end=event.time
                + context.definition.skill_value(
                    "skill1", "full_burst_duration_sec"
                ),
                caster=context.actor,
            )
            for event in events
            if event.event_type == EventType.FULL_BURST_ENTER
        )

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if (
            event.event_type != EventType.B3_STAGE_ENTER
            or event.actor != context.actor
        ):
            return ()

        return (
            BuffWindow(
                source=context.actor,
                skill="burst_an_mode",
                stat="sustained_damage_pct",
                value=context.definition.skill_value("burst", "sustained_damage_pct"),
                target=context.actor,
                start=event.time,
                end=event.time + context.definition.skill_value("burst", "duration_sec"),
            ),
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_nuke",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    core_eligible=False,
                    full_burst_eligible=False,
                    range_eligible=False,
                ),
            ),
        )

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor or not shot.charged:
            return ()

        interval = context.definition.skill_value("skill1", "sustained_interval_sec")
        duration = context.definition.skill_value("skill1", "sustained_duration_sec")
        max_stacks = int(context.definition.skill_value("skill1", "sustained_max_stacks"))

        if shot.time > self._sustained_until:
            self._sustained_stacks = 0
            self._next_dot_tick = round(shot.time + interval, 6)

        self._sustained_stacks = min(max_stacks, self._sustained_stacks + 1)
        self._sustained_until = round(shot.time + duration, 6)
        if self._next_dot_tick is None:
            self._next_dot_tick = round(shot.time + interval, 6)

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill1_sustained_stack_state",
                stat=self._STACK_STAT,
                value=float(self._sustained_stacks),
                target=context.actor,
                start=shot.time,
                # Include the terminal 5s tick on the half-open BuffWindow interval.
                end=self._sustained_until + 1e-6,
            )
        ]

        while self._next_dot_tick <= self._sustained_until + 1e-9:
            tick_time = round(self._next_dot_tick, 6)
            if tick_time not in self._scheduled_ticks:
                self._scheduled_ticks.add(tick_time)
                effects.append(
                    DamageRequest(
                        time=tick_time,
                        actor=context.actor,
                        source="skill1_sustained_dot",
                        category=DamageCategory.SKILL,
                        coefficient_pct=context.definition.skill_value(
                            "skill1", "sustained_damage_pct"
                        ),
                        traits=DamageTraits(
                            category=DamageCategory.SKILL,
                            sustained=True,
                            core_eligible=False,
                            range_eligible=False,
                        ),
                        coefficient_multiplier_stat=self._STACK_STAT,
                    )
                )
            self._next_dot_tick = round(self._next_dot_tick + interval, 6)

        return tuple(effects)
''',
)

# ---------------------------------------------------------------------------
# Quency: Escape Queen — dual-SMG hit-count and real stage expiry/rebuild.
# ---------------------------------------------------------------------------
write(
    "crown_mast_engine/character_mechanics/quency_escape_queen.py",
    '''from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import FPS, DamageRequest, WeaponShot
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class QuencyEscapeQueenSkillHook(SkillHookBase):
    """Single-boss implementation of Quency: Escape Queen's Explore Route.

    Quency fires two hits per SMG pull. Her `after 2 normal attacks` data trigger is
    therefore one engine pull. Stage 2 unlocks only after Stage 1 reaches 10, and
    Stage 3 only after Stage 2 reaches 10. The 2s/1s/0.5s stack durations are live:
    Stage 1 survives the normal reload while Stages 2/3 lapse and rebuild.
    """

    def __init__(self, context: SkillHookContext) -> None:
        self._hit_meter = 0
        self._stage1 = 0
        self._stage2 = 0
        self._stage3 = 0
        self._stage1_until = 0.0
        self._stage2_until = 0.0
        self._stage3_until = 0.0

    def scheduled_buffs(
        self,
        events: tuple[BattleEvent, ...],
        context: SkillHookContext,
    ) -> tuple[BuffWindow, ...]:
        buffs: list[BuffWindow] = []
        duration = context.definition.skill_value("burst", "duration_sec")
        for event in events:
            if event.event_type == EventType.B3_STAGE_ENTER and event.actor == context.actor:
                buffs.append(
                    BuffWindow(
                        source=context.actor,
                        skill="burst_reload",
                        stat="reload_speed_pct",
                        value=context.definition.skill_value("burst", "reload_speed_pct"),
                        target=context.actor,
                        start=event.time,
                        end=event.time + duration,
                    )
                )
        return tuple(buffs)

    def on_battle_event(
        self,
        event: BattleEvent,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if event.event_type != EventType.B3_STAGE_ENTER or event.actor != context.actor:
            return ()

        duration = context.definition.skill_value("burst", "duration_sec")
        return (
            BuffWindow(
                source=context.actor,
                skill="burst",
                stat="attack_damage_pct",
                value=context.definition.skill_value("burst", "attack_damage_pct"),
                target=context.actor,
                start=event.time,
                end=event.time + duration,
            ),
            DamageRequest(
                time=event.time,
                actor=context.actor,
                source="burst_distributed",
                category=DamageCategory.BURST,
                coefficient_pct=context.definition.skill_value("burst", "damage_pct"),
                traits=DamageTraits(
                    category=DamageCategory.BURST,
                    distributed=True,
                    core_eligible=False,
                    full_burst_eligible=False,
                    range_eligible=False,
                ),
            ),
        )

    def _expire_route(self, time: float) -> None:
        if self._stage1 and time >= self._stage1_until:
            self._stage1 = self._stage2 = self._stage3 = 0
            self._stage1_until = self._stage2_until = self._stage3_until = 0.0
            return
        if self._stage2 and time >= self._stage2_until:
            self._stage2 = self._stage3 = 0
            self._stage2_until = self._stage3_until = 0.0
            return
        if self._stage3 and time >= self._stage3_until:
            self._stage3 = 0
            self._stage3_until = 0.0

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()

        self._hit_meter += context.definition.weapon.hits_per_shot
        trigger_hits = int(
            context.definition.skill_value("skill2", "normal_attacks_per_trigger")
        )
        if self._hit_meter < trigger_hits:
            return ()
        self._hit_meter -= trigger_hits
        self._expire_route(shot.time)

        stage1_max = int(context.definition.skill_value("skill2", "stage1_max_stacks"))
        stage2_max = int(context.definition.skill_value("skill2", "stage2_max_stacks"))
        stage3_max = int(context.definition.skill_value("skill2", "stage3_max_stacks"))

        if self._stage1 < stage1_max:
            self._stage1 += 1
        elif self._stage2 < stage2_max:
            self._stage2 += 1
        elif self._stage3 < stage3_max:
            self._stage3 += 1

        after_hit = round(shot.time + 1 / FPS, 6)
        self._stage1_until = after_hit + context.definition.skill_value(
            "skill2", "stage1_duration_sec"
        )
        if self._stage2:
            self._stage2_until = after_hit + context.definition.skill_value(
                "skill2", "stage2_duration_sec"
            )
        if self._stage3:
            self._stage3_until = after_hit + context.definition.skill_value(
                "skill2", "stage3_duration_sec"
            )

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="skill2_stage1",
                stat="atk_pct",
                value=context.definition.skill_value(
                    "skill2", "stage1_atk_pct_per_stack"
                ) * self._stage1,
                target=context.actor,
                start=after_hit,
                end=self._stage1_until,
            )
        ]
        if self._stage1 >= stage1_max:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill1_stage1_max",
                    stat="distributed_damage_pct",
                    value=context.definition.skill_value("skill1", "distributed_damage_pct"),
                    target=context.actor,
                    start=after_hit,
                    end=self._stage1_until,
                )
            )

        if self._stage2:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill2_stage2",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "skill2", "stage2_atk_pct_per_stack"
                    ) * self._stage2,
                    target=context.actor,
                    start=after_hit,
                    end=self._stage2_until,
                )
            )
            if self._stage2 >= stage2_max:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_stage2_max",
                        stat="core_damage_pct",
                        value=context.definition.skill_value("skill1", "core_damage_pct"),
                        target=context.actor,
                        start=after_hit,
                        end=self._stage2_until,
                    )
                )

        if self._stage3:
            effects.append(
                BuffWindow(
                    source=context.actor,
                    skill="skill2_stage3",
                    stat="atk_pct",
                    value=context.definition.skill_value(
                        "skill2", "stage3_atk_pct_per_stack"
                    ) * self._stage3,
                    target=context.actor,
                    start=after_hit,
                    end=self._stage3_until,
                )
            )
            if self._stage3 >= stage3_max:
                effects.append(
                    BuffWindow(
                        source=context.actor,
                        skill="skill1_stage3_max",
                        stat="crit_rate_pct",
                        value=context.definition.skill_value("skill1", "crit_rate_pct"),
                        target=context.actor,
                        start=after_hit,
                        end=self._stage3_until,
                    )
                )

        return tuple(effects)
''',
)

# ---------------------------------------------------------------------------
# Cast-instant Burst Skill packets are pre-Full-Burst for the +50% major even
# when RAID14 stores B3_STAGE_ENTER and FULL_BURST_START at the same timestamp.
# Delayed/FB-enter packets remain eligible.
# ---------------------------------------------------------------------------
for path, source in (
    ("crown_mast_engine/character_mechanics/liberalio.py", 'source="burst_nuke"'),
    ("crown_mast_engine/character_mechanics/cinderella_crystal_wave.py", 'source="burst_nuke"'),
    ("crown_mast_engine/character_mechanics/phantom_favorite_item.py", 'source="burst_distributed"'),
    ("crown_mast_engine/character_mechanics/epinel.py", 'source="burst_safe_50_50"'),
    ("crown_mast_engine/character_mechanics/helm.py", 'source="burst_nuke"'),
):
    text = read(path)
    pos = text.find(source)
    if pos < 0:
        raise RuntimeError(f"{path}: source not found: {source}")
    trait_pos = text.find("core_eligible=False,", pos)
    if trait_pos < 0:
        raise RuntimeError(f"{path}: core_eligible marker not found after {source}")
    insert_at = trait_pos + len("core_eligible=False,")
    text = text[:insert_at] + "\n                    full_burst_eligible=False," + text[insert_at:]
    write(path, text)

# CCW's explicit MG core-strike is a forced core hit, independent of the global
# expected normal-attack core-hit rate used by the research boss profile.
replace_once(
    "crown_mast_engine/character_mechanics/cinderella_crystal_wave.py",
    "                            category=DamageCategory.SKILL,\n                            core_eligible=True,\n                            range_eligible=False,\n",
    "                            category=DamageCategory.SKILL,\n                            core_eligible=True,\n                            forced_core=True,\n                            range_eligible=False,\n",
)

# Mechanics signature bump.
replace_once(
    "crown_mast_engine/character_mechanics/__init__.py",
    '    revision="standard-hooks-r11",\n',
    '    revision="standard-hooks-r12-audited",\n',
)

# Ensure the already-existing Rapi suite and the new audit suite run in push CI.
replace_once(
    ".github/workflows/sample-batch-parallel.yml",
    "          tests.test_cinderella_crystal_wave\n          tests.test_phantom_favorite_item\n",
    "          tests.test_cinderella_crystal_wave\n          tests.test_rapi_red_hood\n          tests.test_character_audit\n          tests.test_phantom_favorite_item\n",
)

# Replace Raven's obsolete independent-instance test with stack-refresh tests.
raven_test = read("tests/test_raven.py")
pattern = re.compile(
    r"    def test_full_charge_appends_independent_five_tick_sustained_instances\(self\) -> None:\n.*?(?=    def test_burst_packet_lands_before_full_burst)",
    re.S,
)
replacement = '''    def test_full_charge_builds_one_refreshing_stack_scaled_dot(self) -> None:\n        dots = tuple(\n            event\n            for event in self.result.damage_events_for(\n                actor=self.actor, category=DamageCategory.SKILL\n            )\n            if event.source == "skill1_sustained_dot"\n        )\n        self.assertTrue(dots)\n        self.assertTrue(all(event.traits.sustained for event in dots))\n        self.assertTrue(all(not event.traits.core_eligible for event in dots))\n        self.assertTrue(all(event.traits.full_burst_eligible for event in dots))\n        self.assertLessEqual(max(event.coefficient_pct for event in dots), 684.6 + 1e-9)\n        self.assertTrue(\n            any(abs(event.coefficient_pct - 684.6) < 1e-6 for event in dots),\n            "continuous boss fire should reach Raven's 10-stack 684.6%/s state",\n        )\n\n    def test_sustained_stack_state_never_exceeds_ten(self) -> None:\n        windows = tuple(\n            window for window in self.result.buffs.windows\n            if window.source == self.actor\n            and window.skill == "skill1_sustained_stack_state"\n        )\n        self.assertTrue(windows)\n        self.assertEqual(max(window.value for window in windows), 10.0)\n\n'''
raven_test, n = pattern.subn(replacement, raven_test, count=1)
if n != 1:
    raise RuntimeError(f"tests/test_raven.py: obsolete test replacement count={n}")
write("tests/test_raven.py", raven_test)

# New cross-character audit regression tests.
write(
    "tests/test_character_audit.py",
    '''import unittest
from dataclasses import replace

from crown_mast_engine import simulate_rotation
from crown_mast_engine.combat import STANDARD_COMBAT_SETTINGS
from crown_mast_engine.models import DamageCategory, EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.timeline import RAID14_TIMELINE


class RapiB1AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actor = "rapi-red-hood"
        cls.roster = TeamRoster(
            b1=cls.actor,
            main_b3="scarlet-black-shadow",
            secondary_b3="helm",
        )
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=cls.roster,
            timeline=RAID14_TIMELINE,
        )

    def test_combat_assist_runs_all_fourteen_fixed_cycles(self) -> None:
        casts = tuple(
            event for event in self.result.events
            if event.event_type == EventType.B1_CAST and event.actor == self.actor
        )
        self.assertEqual(len(casts), 14)
        self.assertEqual(tuple(event.time for event in casts), tuple(c.b1_time for c in RAID14_TIMELINE))

    def test_b1_and_full_burst_team_buffs_match_cross_checked_values(self) -> None:
        first = RAID14_TIMELINE[0]
        for target in dict.fromkeys(self.roster.members):
            b1 = [
                b for b in self.result.active_buffs(first.b1_time + 0.01, target)
                if b.source == self.actor and b.skill == "burst_stage1"
                and b.stat == "caster_atk_pct"
            ]
            self.assertEqual([b.value for b in b1], [18.01])
            fb = [
                b for b in self.result.active_buffs(first.full_burst_start + 0.01, target)
                if b.source == self.actor and b.skill == "skill1_combat_assist"
                and b.stat == "attack_damage_pct"
            ]
            self.assertEqual([b.value for b in fb], [8.02])

    def test_combat_assist_does_not_receive_the_dps_branch_95_04_atk(self) -> None:
        self.assertFalse(
            any(
                b.source == self.actor and b.skill == "skill1_full_burst"
                and b.stat == "atk_pct" and b.value == 95.04
                for b in self.result.buffs.windows
            )
        )
        self.assertFalse(
            any(
                e.actor == self.actor and e.source == "burst_stage3_missile"
                for e in self.result.damage_events
            )
        )


class QuencyRouteAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.actor = "quency-escape-queen"
        cls.result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3=cls.actor),
        )

    def test_dual_smg_hit_count_two_means_one_pull_per_route_trigger(self) -> None:
        normals = self.result.damage_events_for(actor=self.actor, category=DamageCategory.NORMAL)
        stage1_max = next(
            w for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage1_max"
        )
        self.assertLessEqual(stage1_max.start, normals[9].time + 1 / 60 + 1e-6)
        self.assertGreater(stage1_max.start, normals[8].time)

    def test_stage2_and_stage3_unlock_sequentially(self) -> None:
        s1 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage1_max"
        )
        s2 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage2_max"
        )
        s3 = min(
            w.start for w in self.result.buffs.windows
            if w.source == self.actor and w.skill == "skill1_stage3_max"
        )
        self.assertLess(s1, s2)
        self.assertLess(s2, s3)

    def test_short_stage2_and_stage3_buffs_lapse_during_reload(self) -> None:
        normals = self.result.damage_events_for(actor=self.actor, category=DamageCategory.NORMAL)
        before = None
        after = None
        for left, right in zip(normals, normals[1:]):
            if right.time - left.time > 1.05:
                before, after = left, right
                break
        self.assertIsNotNone(before)
        self.assertIsNotNone(after)
        probe = after.time - 0.05
        self.assertEqual(self.result.buff_total(probe, self.actor, "core_damage_pct"), 0.0)
        self.assertEqual(self.result.buff_total(probe, self.actor, "crit_rate_pct"), 0.0)
        # Stage 1 has a 2s window and should survive the ordinary SMG reload.
        self.assertEqual(self.result.buff_total(probe, self.actor, "distributed_damage_pct"), 49.58)


class CoreStrikeAuditTests(unittest.TestCase):
    def test_ccw_mg_core_strike_forces_core_bucket_even_with_zero_normal_core_rate(self) -> None:
        actor = "cinderella-crystal-wave"
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3=actor),
        )
        rider = next(
            event for event in result.damage_events_for(actor=actor)
            if event.source == "skill2_mg_full_burst_core_strike"
        )
        self.assertTrue(rider.traits.forced_core)
        # 7.5% expected crit + 50% FB + 100% base core + 26% Pinpoint.
        self.assertAlmostEqual(rider.breakdown.major, 2.835)


class BurstCastTimingAuditTests(unittest.TestCase):
    CASES = (
        ("liberalio", "burst_nuke"),
        ("raven", "burst_nuke"),
        ("cinderella-crystal-wave", "burst_nuke"),
        ("phantom", "burst_distributed"),
        ("quency-escape-queen", "burst_distributed"),
        ("epinel", "burst_safe_50_50"),
        ("helm", "burst_nuke"),
    )

    def test_cast_instant_burst_packets_do_not_take_fb_50_on_raid14(self) -> None:
        zero_fb = replace(STANDARD_COMBAT_SETTINGS, full_burst_bonus_pct=0.0)
        for actor, source in self.CASES:
            with self.subTest(actor=actor):
                roster = TeamRoster(main_b3=actor)
                if actor == "helm":
                    roster = TeamRoster(main_b3="rapi-red-hood", secondary_b3="helm")
                base = simulate_rotation(
                    CROWN_CROWN_MAST,
                    roster=roster,
                    timeline=RAID14_TIMELINE,
                )
                control = simulate_rotation(
                    CROWN_CROWN_MAST,
                    roster=roster,
                    timeline=RAID14_TIMELINE,
                    combat_settings=zero_fb,
                )
                packet = next(
                    e for e in base.damage_events_for(actor=actor)
                    if e.source == source
                )
                control_packet = next(
                    e for e in control.damage_events_for(actor=actor)
                    if e.source == source
                )
                self.assertTrue(packet.full_burst, "RAID14 timestamps overlap FB start")
                self.assertFalse(packet.traits.full_burst_eligible)
                self.assertAlmostEqual(packet.damage, control_packet.damage)

    def test_delayed_rapi_and_ccw_fb_enter_packets_remain_fb_eligible(self) -> None:
        rapi = simulate_rotation(
            CROWN_CROWN_MAST,
            timeline=RAID14_TIMELINE,
        )
        missile = next(
            e for e in rapi.damage_events_for(actor="rapi-red-hood")
            if e.source == "burst_stage3_missile"
        )
        self.assertTrue(missile.traits.full_burst_eligible)
        self.assertTrue(missile.full_burst)

        ccw = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=TeamRoster(main_b3="cinderella-crystal-wave"),
            timeline=RAID14_TIMELINE,
        )
        rider = next(
            e for e in ccw.damage_events_for(actor="cinderella-crystal-wave")
            if e.source == "skill2_mg_full_burst_core_strike"
        )
        self.assertTrue(rider.traits.full_burst_eligible)
        self.assertTrue(rider.full_burst)


if __name__ == "__main__":
    unittest.main()
''',
)

# Audit note: separates confirmed fixes from intentional study-scope omissions.
write(
    "docs/CHARACTER_AUDIT_2026-09-02.md",
    '''# Character audit — 2026-09-02

Scope: Crown–Mast single stage-target, externally fixed RAID14 timeline. No research batch was run.

Cross-check sources:
- `Infernal-Crack-LED/nikke-sim@43308bd02276a476660e44af730785c2ae91eea3`
- `Moris-kr/nikke-calc` `data/parsed_skills.json` and damage/timeline implementation
- NIKKE.gg current character guides; Prydwen used as a tertiary sanity check where useful

Confirmed corrections:
1. Rapi: Red Hood now supports the no-separate-B1 Combat Assist branch: B1 team caster-ATK 18.01%/10s and Full-Burst team Attack Damage 8.02%/10s. Her 20s self B1 CDR and 7.48s team FB CDR are documented but do not alter the externally measured RAID14 timestamps.
2. Raven Shock Wave is one refreshing target state, stacking to 10 and ticking once per second at 68.46% × current stacks. The prior independent-five-tick-per-shot approximation was wrong.
3. Quency: Escape Queen's dual SMG supplies the two-hit trigger every pull. Explore Route now unlocks sequentially and honors 2s/1s/0.5s expiry, so Stage 2/3 lapse and rebuild across reloads.
4. Cinderella: Crystal Wave's MG 833.79% core-strike uses a forced-core path; it is not diluted by the externally configured normal-attack core-hit rate.
5. Burst-cast instant damage is explicitly Full-Burst-major-exempt even where RAID14 stores B3 cast and Full Burst start at the same timestamp. Applied to Liberalio, Raven, CCW, Phantom FI, Quency EQ, Epinel, and Helm. Delayed Rapi B3 and FB-enter CCW riders remain timing-eligible.

Checked with no correction required in this study scope:
- Bready: Recommended Taste route values/conditions agree. Lingering Taste's 349.8 semantics remain source-disputed but are not activated by the Crown–Mast Recommended route.
- Liberalio: single stage-target Raging Current route, 202.5 full-charge rider, 160% FB ATK, 231% Raging Current, 925 burst packet agree. Gentle Current is out of scope.
- Milk: Blooming Bunny: this engine intentionally uses AUTO basis. 447.7% distributed ×5, +220% ATK and +117.64% Pierce Damage are retained. Moris models the manual 0.5s hold/Embarrassment route; it is deliberately not claimed here.
- Phantom FI: Calling Card/Dagger, 250% distributed rider, distributed-amplification stacks, 1457.28% Burst, and Fire-target 18% vulnerability agree for the single-boss favorite-item scope.

Known scope notes:
- CCW remains MG-only by project decision; Snipe state machine is excluded.
- Fixed RAID14 means gauge-generation and CDR effects are not allowed to move burst timestamps.
- Parts/jumps/invulnerability remain outside the base research model.
''',
)

print("character audit patch applied")
