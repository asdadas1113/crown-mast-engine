from __future__ import annotations

from pathlib import Path
import runpy
import re

ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "scripts/_tmp_character_audit_runner.py"), run_name="__main__")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, value: str) -> None:
    (ROOT / path).write_text(value, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    value = read(path)
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, got {count}: {old!r}")
    write(path, value.replace(old, new, 1))


# Huge deterministic totals should not fail on sub-millidamage floating summation noise.
replace_once(
    "tests/test_analysis.py",
    "        self.assertAlmostEqual(overall.team_f, 2_118_326_068.3537395)\n",
    "        self.assertAlmostEqual(overall.team_f, 2_118_326_068.3537395, delta=1e-3)\n",
)
replace_once(
    "tests/test_analysis.py",
    "            self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643)\n",
    "            self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643, delta=1e-3)\n",
)
replace_once(
    "tests/test_research.py",
    "        self.assertAlmostEqual(overall.team.funnel, 2_118_326_068.3537395)\n",
    "        self.assertAlmostEqual(overall.team.funnel, 2_118_326_068.3537395, delta=1e-3)\n",
)
replace_once(
    "tests/test_scarlet_black_shadow.py",
    "        self.assertAlmostEqual(overall.team_f, 2_094_367_146.9837704)\n",
    "        self.assertAlmostEqual(overall.team_f, 2_094_367_146.9837704, delta=1e-3)\n",
)

# Quency: replace the environment-dependent "ordinary reload must exceed 1s" assertion
# with a direct mechanic boundary test: a >1s but <2s gap must preserve Stage 1 while
# expiring Stage 2/3, after which Stage 2 rebuilds from one stack.
test_path = "tests/test_character_audit.py"
test = read(test_path)
old_import = "from crown_mast_engine import simulate_rotation\nfrom crown_mast_engine.combat import STANDARD_COMBAT_SETTINGS\nfrom crown_mast_engine.models import DamageCategory, EventType, TeamRoster\n"
new_import = "from crown_mast_engine import simulate_rotation\nfrom crown_mast_engine.character_mechanics import QuencyEscapeQueenSkillHook\nfrom crown_mast_engine.characters import STANDARD_CHARACTER_CATALOG\nfrom crown_mast_engine.combat import STANDARD_COMBAT_SETTINGS, WeaponShot\nfrom crown_mast_engine.mechanics import SkillHookContext\nfrom crown_mast_engine.models import DamageCategory, EventType, TeamRoster\n"
if old_import not in test:
    raise RuntimeError("character audit import block not found")
test = test.replace(old_import, new_import, 1)

pattern = re.compile(
    r"    def test_short_stage2_and_stage3_buffs_lapse_during_reload\(self\) -> None:\n.*?(?=\n\nclass CoreStrikeAuditTests)",
    re.S,
)
replacement = '''    def test_stage2_and_stage3_expire_after_one_second_gap_while_stage1_survives(self) -> None:\n        definition = STANDARD_CHARACTER_CATALOG.require(self.actor)\n        context = SkillHookContext(\n            actor=self.actor,\n            definition=definition,\n            roster=TeamRoster(main_b3=self.actor),\n            timeline=(),\n            duration_sec=180.0,\n        )\n        hook = QuencyEscapeQueenSkillHook(context)\n\n        def shot(index: int, time: float) -> WeaponShot:\n            return WeaponShot(\n                time=time,\n                frame=round(time * 60),\n                actor=self.actor,\n                shot_index=index,\n                magazine_index=0,\n                rounds_consumed=1,\n                core_eligible=True,\n            )\n\n        # 10 pulls fill Stage 1, next 10 fill Stage 2, next 5 fill Stage 3.\n        last_time = 0.0\n        for index in range(25):\n            last_time = index * 0.05\n            hook.on_weapon_shot(shot(index, last_time), context)\n\n        # 1.2s is longer than Stage 2 (1s) and Stage 3 (0.5s), but shorter\n        # than Stage 1 (2s). On the next pull Stage 1 must remain maxed while\n        # Stage 2 restarts at one stack and Stage 3 is absent.\n        effects = hook.on_weapon_shot(shot(25, last_time + 1.2), context)\n        windows = [effect for effect in effects if hasattr(effect, "skill")]\n        by_skill = {window.skill: window for window in windows}\n        self.assertIn("skill1_stage1_max", by_skill)\n        self.assertNotIn("skill1_stage2_max", by_skill)\n        self.assertNotIn("skill1_stage3_max", by_skill)\n        self.assertIn("skill2_stage2", by_skill)\n        self.assertAlmostEqual(by_skill["skill2_stage2"].value, 4.9)\n'''
test, count = pattern.subn(replacement, test, count=1)
if count != 1:
    raise RuntimeError(f"Quency audit boundary replacement count={count}")
write(test_path, test)

print("character audit runner2 corrections applied")
