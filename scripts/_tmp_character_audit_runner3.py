from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runner2 = ROOT / "scripts/_tmp_character_audit_runner2.py"
text = runner2.read_text(encoding="utf-8")

old = '''    "            self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643)\\n",\n    "            self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643, delta=1e-3)\\n",\n'''
new = '''    "        self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643)\\n",\n    "        self.assertAlmostEqual(cycle_damage.funnel, 164_000_383.44454643, delta=1e-3)\\n",\n'''
if old not in text:
    raise RuntimeError("runner2 cycle-damage indentation block not found")
text = text.replace(old, new, 1)

namespace = {"__file__": str(runner2), "__name__": "__main__"}
exec(compile(text, str(runner2), "exec"), namespace)
print("character audit runner3 indentation correction applied")
