from __future__ import annotations

from ..combat import FPS, WeaponShot
from ..mechanics import RecoveryEffect, SkillEffect, SkillHookBase, SkillHookContext


class CrownSkillHook(SkillHookBase):
    """Collapse Crown's defensive Relax stacks into their DPS-relevant heal event."""

    def __init__(self, context: SkillHookContext) -> None:
        hits_per_stack = int(
            context.definition.skill_value("skill2", "relax_hits_per_stack")
        )
        max_stacks = int(
            context.definition.skill_value("skill2", "max_relax_stacks")
        )
        if hits_per_stack <= 0 or max_stacks <= 0:
            raise ValueError("Crown Relax hit and stack thresholds must be positive")
        self._self_recovery_threshold = hits_per_stack * max_stacks
        self._normal_attacks = 0

    def on_weapon_shot(
        self,
        shot: WeaponShot,
        context: SkillHookContext,
    ) -> tuple[SkillEffect, ...]:
        if shot.actor != context.actor:
            return ()

        self._normal_attacks += 1
        if self._normal_attacks % self._self_recovery_threshold != 0:
            return ()

        # Recovery is resolved after the triggering hit, so that hit cannot
        # retroactively receive the resulting team Attack Damage buff.
        recovery_time = round(shot.time + 1 / FPS, 6)
        return (RecoveryEffect(recovery_time, context.actor),)
