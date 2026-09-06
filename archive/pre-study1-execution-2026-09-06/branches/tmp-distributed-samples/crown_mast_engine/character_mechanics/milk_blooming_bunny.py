from __future__ import annotations

from ..buffs import BuffWindow
from ..combat import DamageRequest
from ..damage import DamageTraits
from ..mechanics import SkillEffect, SkillHookBase, SkillHookContext
from ..models import BattleEvent, DamageCategory, EventType


class MilkBloomingBunnySkillHook(SkillHookBase):
    """Pinned AUTO-basis implementation for Milk: Blooming Bunny.

    The upstream source deliberately leaves the manual 0.5s held-charge
    Embarrassment cycle unmodeled. This research hook follows that basis.

    In the single-target Crown-Mast study every modeled Milk hit in her own
    burst window is Pierce-tagged by her continuously refreshed Full Charge
    gain-Pierce state. The engine has no standalone Pierce bucket, so the
    pinned +117.64% Pierce Damage line is collapsed to Attack Damage for that
    10s self window. This also follows the pinned nikke-sim behavior where the
    447.7% distributed rider inherits the live Pierce tag.
    """

    def __init__(self, context: SkillHookContext) -> None:
        pass

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

        duration = context.definition.skill_value("burst", "duration_sec")
        interval = context.definition.skill_value(
            "skill2", "overconfident_interval_sec"
        )
        ticks = int(context.definition.skill_value("skill2", "overconfident_ticks"))
        # Include the fifth "every 2 sec" tick at the 10s boundary.
        buff_end = event.time + duration + 1e-6

        effects: list[SkillEffect] = [
            BuffWindow(
                source=context.actor,
                skill="burst_atk",
                stat="atk_pct",
                value=context.definition.skill_value("burst", "atk_pct"),
                target=context.actor,
                start=event.time,
                end=buff_end,
            ),
            BuffWindow(
                source=context.actor,
                skill="burst_pierce_collapsed",
                stat="attack_damage_pct",
                value=context.definition.skill_value("burst", "pierce_damage_pct"),
                target=context.actor,
                start=event.time,
                end=buff_end,
            ),
        ]
        for tick in range(1, ticks + 1):
            effects.append(
                DamageRequest(
                    time=round(event.time + interval * tick, 6),
                    actor=context.actor,
                    source="skill2_overconfident_distributed",
                    category=DamageCategory.SKILL,
                    coefficient_pct=context.definition.skill_value(
                        "skill2", "overconfident_distributed_damage_pct"
                    ),
                    traits=DamageTraits(
                        category=DamageCategory.SKILL,
                        distributed=True,
                        core_eligible=False,
                        range_eligible=False,
                    ),
                )
            )
        return tuple(effects)
