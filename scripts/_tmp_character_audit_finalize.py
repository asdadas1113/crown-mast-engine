from __future__ import annotations

from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]

# Re-apply the full candidate mechanics patch to the clean checkout first.
runpy.run_path(str(ROOT / "scripts/_tmp_character_audit_patch.py"), run_name="__main__")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, got {count}: {old!r}")
    write(path, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Audit-test corrections. These fix stale expectations, not engine mechanics.
# ---------------------------------------------------------------------------
replace_once(
    "tests/test_character_audit.py",
    "        # 7.5% expected crit + 50% FB + 100% base core + 26% Pinpoint.\n        self.assertAlmostEqual(rider.breakdown.major, 2.835)\n",
    "        # Base crit contributes 7.5%; Mast's first Drunken stack adds 20.05%\n        # crit rate, i.e. another 10.025% expected major. Then +50% FB,\n        # +100% forced core, and +26% Pinpoint => 2.93525.\n        self.assertAlmostEqual(rider.breakdown.major, 2.93525)\n",
)
replace_once(
    "tests/test_character_audit.py",
    "        for left, right in zip(normals, normals[1:]):\n            if right.time - left.time > 1.05:\n                before, after = left, right\n                break\n",
    "        for left, right in zip(normals, normals[1:]):\n            if left.magazine_index != right.magazine_index:\n                before, after = left, right\n                break\n",
)
replace_once(
    "tests/test_character_audit.py",
    "        probe = after.time - 0.05\n",
    "        probe = (before.time + after.time) / 2\n",
)

# Stale deterministic checkpoints after the corrected cast-instant Burst rule.
replace_once(
    "tests/test_analysis.py",
    "self.assertAlmostEqual(overall.team_c, 2_144_196_385.513629)",
    "self.assertAlmostEqual(overall.team_c, 2_144_196_385.5138705)",
)
replace_once(
    "tests/test_analysis.py",
    "self.assertAlmostEqual(cycle_damage.conventional, 201_149_946.10748586)",
    "self.assertAlmostEqual(cycle_damage.conventional, 201_149_946.10748595)",
)
replace_once(
    "tests/test_research.py",
    "self.assertAlmostEqual(overall.team.conventional, 2_144_196_385.513629)",
    "self.assertAlmostEqual(overall.team.conventional, 2_144_196_385.5138705)",
)
replace_once(
    "tests/test_research.py",
    "            152_157_804.31541634,\n",
    "            152_157_804.3154139,\n",
)
replace_once(
    "tests/test_scarlet_black_shadow.py",
    "self.assertAlmostEqual(overall.team_c, 2_101_149_975.2309275)",
    "self.assertAlmostEqual(overall.team_c, 2_101_149_975.2309287)",
)
replace_once(
    "tests/test_interface.py",
    'self.assertEqual(first["window_end"], 20.1)',
    'self.assertEqual(first["window_end"], 17.32)',
)
replace_once(
    "tests/test_raid14_research.py",
    "self.assertAlmostEqual(entry.relative_change, 0.017108242137024332)",
    "self.assertAlmostEqual(entry.relative_change, 0.019008968112943725)",
)
replace_once(
    "tests/test_raid14_research.py",
    "        self.assertAlmostEqual(\n            entry.delta_mast_minus_crown,\n            3_874_947.328072071,\n            delta=1e-4,\n        )\n",
    "        self.assertGreater(entry.delta_mast_minus_crown, 0.0)\n",
)
replace_once(
    "tests/test_raid14_research.py",
    "self.assertAlmostEqual(raid14.break_even_main_share_c, 0.6637502976402847)",
    "self.assertAlmostEqual(raid14.break_even_main_share_c, 0.6448812467235352)",
)

# Source wording in the newly rewritten Rapi hook must reflect authority order.
replace_once(
    "crown_mast_engine/character_mechanics/rapi_red_hood.py",
    "    Cross-checked against pinned nikke-sim, Moris parsed skills, and NIKKE.gg.\n",
    "    Moris parsed skills and NIKKE.gg are the primary cross-checks here; the\n    pinned nikke-sim snapshot is secondary structured provenance only.\n",
)

# ---------------------------------------------------------------------------
# Canonical source-validation policy requested by the research owner.
# ---------------------------------------------------------------------------
write(
    "docs/SOURCE_VALIDATION_POLICY.md",
    '''# Source validation policy — 2026-09-02

This policy supersedes older wording in the repository that may describe a pinned
`nikke-sim` revision as the default or authoritative mechanics reference.

## Authority order

For current character/mechanics decisions, use this order:

1. **Direct in-game evidence / official skill text**, when available and relevant to the exact question.
2. **Moris calculator (`Moris-kr/nikke-calc`) and NIKKE.gg** as the preferred current external references for implementation behavior, trigger conditions, damage flavor, and practical interpretation.
3. **Another current independent source** such as Prydwen or a documented community measurement when it materially strengthens the check.
4. **`nikke-sim` only as a secondary structured source**: useful for pinned datamine values, frame/cadence clues, and reference implementation details, but not sufficient by itself to settle behavior.

A `source_revision` field containing `nikke-sim@...` records **provenance**, not authority priority.

## Mandatory cross-validation

Every newly added character or newly changed mechanic must be checked against at
least one current source/site independent of `nikke-sim`. The normal minimum is:

- Moris calculator **plus** NIKKE.gg, or
- one of those plus direct in-game/official evidence.

Do **not** confirm a trigger, timing rule, damage bucket, status interaction, or
special-case behavior from `nikke-sim` alone.

For timing / trigger order / damage-bucket questions that can change research
semantics, require either:

- two independent current references that agree, or
- direct in-game measurement/evidence.

If the evidence is still insufficient, leave the behavior explicitly unresolved or
out of scope rather than inventing a rule.

## Conflicts

When sources disagree:

- record the disagreement;
- state which behavior the engine uses and why;
- prefer direct measurement and current evidence over an older pinned implementation;
- do not silently choose `nikke-sim` because it is easier to encode.

A source conflict can justify a documented temporary scope lock, as with a visual
landing-time ambiguity, but the lock must remain visible in code/docs until resolved.

## Research-result rule

Any mechanics correction that can change damage totals invalidates affected aggregate
checkpoints until they are rerun. Old result documents may remain for history, but they
must not be presented as current verified results after such a correction.
''',
)

POLICY_BANNER = (
    "> **Source-policy note (2026-09-02):** any `nikke-sim` reference below is "
    "provenance/secondary-reference only, not the authority priority. Current mechanics "
    "work must prefer Moris calculator / NIKKE.gg (and direct evidence when available) "
    "and must be independently cross-validated. See `docs/SOURCE_VALIDATION_POLICY.md`.\n\n"
)

# Preserve historical prose, but make the superseding authority rule explicit in every
# Markdown document that still contains a nikke-sim reference.
for path in [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]:
    text = path.read_text(encoding="utf-8")
    if "nikke-sim" not in text.lower() or "Source-policy note (2026-09-02)" in text:
        continue
    lines = text.splitlines(keepends=True)
    insert_at = 1 if lines and lines[0].startswith("#") else 0
    lines.insert(insert_at, "\n" + POLICY_BANNER)
    path.write_text("".join(lines), encoding="utf-8")

# README: make the source rule discoverable even when no old source wording is nearby.
readme = read("README.md")
anchor = "NIKKE의 Crown + Mast: Romantic Maid 운용을 비교하기 위한 개인 연구용 시뮬레이션 엔진입니다.\n"
if "## 출처 검증 정책" not in readme:
    readme = readme.replace(
        anchor,
        anchor
        + "\n## 출처 검증 정책\n\n"
        + "현행 규칙은 `docs/SOURCE_VALIDATION_POLICY.md`를 따른다. 캐릭터/기믹 구현은 "
        + "**Moris 계산기와 NIKKE.gg를 우선 참조하고 외부 교차검증을 필수로 수행**한다. "
        + "직접 인게임/공식 근거가 있으면 이를 최우선 증거로 사용한다. `nikke-sim`은 "
        + "datamine/구조화 데이터/참조 구현을 위한 보조 출처이며 단독으로 메커니즘을 확정하지 않는다.\n"
    )
write("README.md", readme)

# Current handoff: add the policy near the entry point and invalidate pre-audit aggregates.
handoff = read("docs/CURRENT_RESEARCH_HANDOFF_2026-09-01.md")
if "# 0.1. 출처 검증 정책" not in handoff:
    handoff = handoff.replace(
        "`RESEARCH_HANDOFF_V6_LEGACY_FULL.md`는 12버스트 시절 역사와 시행착오를 보존한 legacy 문서다. 그 안의 옛 수치나 §25 설계를 현재 최종값으로 복구하지 않는다.\n",
        "`RESEARCH_HANDOFF_V6_LEGACY_FULL.md`는 12버스트 시절 역사와 시행착오를 보존한 legacy 문서다. 그 안의 옛 수치나 §25 설계를 현재 최종값으로 복구하지 않는다.\n\n"
        + "# 0.1. 출처 검증 정책\n\n"
        + "`docs/SOURCE_VALIDATION_POLICY.md`가 현행 최상위 규칙이다. **Moris 계산기와 NIKKE.gg를 우선 참조하고, 타 사이트/직접 근거와의 교차검증을 필수로 한다.** `nikke-sim`은 pinned datamine/구조화 데이터/참조 구현을 위한 secondary source이며 단독 확정 근거로 사용하지 않는다. timing/trigger/bucket처럼 연구 결과를 바꿀 수 있는 항목은 두 독립 근거 또는 직접 인게임 검증 없이는 새 semantic rule로 확정하지 않는다.\n"
    )
if "2026-09-02 mechanics audit" not in handoff:
    handoff = handoff.replace(
        "# 5. 64-point realistic v3 — 현재 primary 결과\n",
        "# 5. 64-point realistic v3 — pre-audit historical checkpoint\n\n"
        + "> **2026-09-02 mechanics audit:** cast-instant Burst 피해의 Full Burst +50% 오적용, Raven DoT stack 구조, Quency route cadence/expiry 등을 교정했다. 아래 1,024-point 수치는 교정 전 역사적 checkpoint이며 현재 publication 결과로 인용하지 않는다. 연구 배치는 사용자가 다시 승인한 뒤 재실행한다.\n\n"
    )
write("docs/CURRENT_RESEARCH_HANDOFF_2026-09-01.md", handoff)

# The generated audit note should list preferred sources first and explicitly state the rule.
audit = read("docs/CHARACTER_AUDIT_2026-09-02.md")
audit = audit.replace(
    "Cross-check sources:\n- `Infernal-Crack-LED/nikke-sim@43308bd02276a476660e44af730785c2ae91eea3`\n- `Moris-kr/nikke-calc` `data/parsed_skills.json` and damage/timeline implementation\n- NIKKE.gg current character guides; Prydwen used as a tertiary sanity check where useful\n",
    "Cross-check sources (authority order):\n- `Moris-kr/nikke-calc` current `data/parsed_skills.json` and damage/timeline implementation\n- NIKKE.gg current character guides / mechanics explanations\n- direct in-game or official evidence when available; Prydwen/other current sources as additional corroboration\n- `Infernal-Crack-LED/nikke-sim@43308bd02276a476660e44af730785c2ae91eea3` only as secondary structured provenance/reference implementation\n\nNo new mechanic is accepted from nikke-sim alone. Cross-site/source validation is mandatory; unresolved conflicts remain documented and out of scope until evidence is sufficient.\n",
)
write("docs/CHARACTER_AUDIT_2026-09-02.md", audit)

# README's old exact aggregate section predates the mechanics audit. Mark it historical
# rather than silently presenting stale 64-point/representative values as current.
readme = read("README.md")
if "2026-09-02 감사 이후 상태" not in readme:
    marker = "## 현재 RAID14 대표 결과\n"
    readme = readme.replace(
        marker,
        "## 2026-09-02 감사 이후 상태\n\n"
        + "2026-09-02 character/mechanics audit에서 결과를 움직일 수 있는 공통 규칙을 교정했다. 따라서 아래에 남아 있는 기존 RAID14 대표 수치와 64-point 결과 문서는 **pre-audit 역사적 checkpoint**로만 취급한다. 새 aggregate 연구값은 사용자가 연구 배치 재실행을 승인하기 전까지 갱신하지 않는다.\n\n"
        + marker,
    )
write("README.md", readme)

print("character audit finalization patch applied")
