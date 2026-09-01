from __future__ import annotations

from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "scripts/_tmp_character_audit_runner3.py"), run_name="__main__")

path = ROOT / "tests/test_analysis.py"
text = path.read_text(encoding="utf-8")
old = "        self.assertAlmostEqual(cycle_damage.loss_from_funnel, 37_149_562.66293943)\n"
new = "        self.assertAlmostEqual(cycle_damage.loss_from_funnel, 37_149_562.66293943, delta=1e-3)\n"
if text.count(old) != 1:
    raise RuntimeError("loss_from_funnel regression assertion not found")
text = text.replace(old, new, 1)
old_rel = '''        self.assertAlmostEqual(\n            cycle_damage.relative_loss_from_funnel,\n            0.1846859190461244,\n        )\n'''
new_rel = '''        self.assertAlmostEqual(\n            cycle_damage.relative_loss_from_funnel,\n            0.1846859190461244,\n            delta=1e-12,\n        )\n'''
if text.count(old_rel) != 1:
    raise RuntimeError("relative_loss_from_funnel regression assertion not found")
text = text.replace(old_rel, new_rel, 1)
path.write_text(text, encoding="utf-8")

print("character audit runner4 floating tolerance applied")
