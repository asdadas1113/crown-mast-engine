from __future__ import annotations

import argparse
import json
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from .characters import STANDARD_CHARACTER_CATALOG
from .combat import CombatSettings
from .equipment import (
    GEAR_SLOTS,
    BuildProfile,
    CollectionProfile,
    EquipmentLoadout,
    GearState,
    OverloadProfile,
    SR15_COLLECTION,
)
from .mechanics import ENGINE_RULE_REVISION
from .models import TeamRoster
from .research import (
    ComparisonReport,
    FirstBurstEntryDamageReport,
    ResearchScenario,
    analyze_entry_variants,
    run_research_scenario,
)
from .rotations import BASELINE_ROTATIONS, CROWN_CROWN_MAST
from .samples import SampleCase, run_sample_batch


WEB_ROOT = Path(__file__).with_name("web")
MAX_REQUEST_BYTES = 1_000_000
FIXED_ACTORS = ("crown", "mast-romantic-maid")
BASELINE_ROTATION_DEFINITIONS = (
    {
        "id": CROWN_CROWN_MAST.name,
        "label": "크크메",
        "sequence": "Crown-Crown-Mast × 4",
    },
    {
        "id": "opening_mast_crown_mast",
        "label": "진입 메크메",
        "sequence": "Mast-Crown-Mast → Crown-Crown-Mast × 3",
    },
)

B1_CHECKPOINTS = (
    {
        "id": "b1-low",
        "label": "B1 Low",
        "gear": GearState.BASE5,
        "overload": OverloadProfile(),
        "collection": "low",
    },
    {
        "id": "b1-standard",
        "label": "B1 Standard",
        "gear": GearState.OL5,
        "overload": OverloadProfile(),
        "collection": "SR15",
    },
    {
        "id": "b1-high",
        "label": "B1 High",
        "gear": GearState.OL5,
        "overload": OverloadProfile(atk_lines=4, element_lines=4, ammo_lines=3),
        "collection": "SR15",
    },
)

DEALER_CHECKPOINTS = (
    {
        "id": "equal-o5",
        "label": "Main O5 bare / Secondary O5 bare",
        "main": (GearState.OL5, OverloadProfile()),
        "secondary": (GearState.OL5, OverloadProfile()),
    },
    {
        "id": "gap-o5-o0",
        "label": "Main O5 bare / Secondary O0 bare",
        "main": (GearState.OL5, OverloadProfile()),
        "secondary": (GearState.OL0, OverloadProfile()),
    },
    {
        "id": "atk3-vs-b5",
        "label": "Main O5 ATK3 / Secondary B5",
        "main": (GearState.OL5, OverloadProfile(atk_lines=3)),
        "secondary": (GearState.BASE5, OverloadProfile()),
    },
    {
        "id": "ammo2-vs-o5",
        "label": "Main O5 Ammo2 / Secondary O5 bare",
        "main": (GearState.OL5, OverloadProfile(ammo_lines=2)),
        "secondary": (GearState.OL5, OverloadProfile()),
    },
)

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


def interface_metadata() -> dict[str, Any]:
    definitions = STANDARD_CHARACTER_CATALOG.definitions
    characters = [
        {
            "slug": definition.slug,
            "name": definition.name,
            "burst_stage": definition.burst_stage,
            "unit_class": definition.unit_class,
            "element": definition.element,
            "weapon_type": definition.weapon.weapon_type,
        }
        for definition in definitions
    ]
    return {
        "characters": characters,
        "b1_options": [item for item in characters if item["burst_stage"] == "I"],
        "b3_options": [item for item in characters if item["burst_stage"] == "III"],
        "fixed_actors": list(FIXED_ACTORS),
        "baseline_rotations": list(BASELINE_ROTATION_DEFINITIONS),
        "gear_states": [state.value for state in GearState],
        "collection_stages": (
            ["none"]
            + [f"R{level}" for level in range(16)]
            + [f"SR{level}" for level in range(16)]
        ),
        "boss_elements": ["Fire", "Water", "Wind", "Electric", "Iron"],
        "defaults": {
            "roster": {
                "b1": "liter",
                "main_b3": "rapi-red-hood",
                "secondary_b3": "helm",
            },
            "gear_state": GearState.BASE5.value,
            "baseline_rotation": CROWN_CROWN_MAST.name,
            "collection_by_actor": {
                definition.slug: (
                    "SR15"
                    if definition.slug in {"helm", "moran-favorite-item"}
                    else "none"
                )
                for definition in definitions
            },
            "combat": {
                "boss_def": 140.0,
                "boss_element": None,
                "core_hit_rate_pct": 0.0,
                "range_bonus_pct": 0.0,
            },
        },
        "revisions": {
            "engine_rule": ENGINE_RULE_REVISION,
            "skill_hooks": (
                ResearchScenario.standard().expected_skill_hook_revision
            ),
            "catalog_source": STANDARD_CHARACTER_CATALOG.scope.source_revision,
        },
    }


def calculate_interface_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    payload = _mapping(payload, "request")
    _required_optional_keys(
        payload,
        {"roster", "builds", "combat"},
        {"baseline_rotation"},
        "request",
    )

    roster = _parse_roster(payload["roster"])

    builds_payload = _mapping(payload["builds"], "builds")
    expected_actors = set(roster.members)
    _exact_keys(builds_payload, expected_actors, "builds")
    builds = {
        actor: _build_profile(_mapping(builds_payload[actor], f"builds.{actor}"), actor)
        for actor in roster.members
    }

    combat_settings = _parse_combat(payload["combat"])
    scenario = ResearchScenario(
        roster=roster,
        builds=builds,
        combat_settings=combat_settings,
        main_actor=roster.main_b3,
        baseline_rotation=CROWN_CROWN_MAST.name,
    )
    variants = analyze_entry_variants(scenario)
    crown_report = ComparisonReport.from_comparison(
        scenario,
        variants.crown_entry,
    )
    mast_scenario = replace(
        scenario,
        baseline_rotation="opening_mast_crown_mast",
    )
    mast_report = ComparisonReport.from_comparison(
        mast_scenario,
        variants.mast_entry,
    )
    return {
        "schema_version": 1,
        "scenario": scenario.to_dict(),
        "mechanics_signature": crown_report.to_dict()["mechanics_signature"],
        "display_names": _display_names(roster),
        "comparisons": {
            "crown_entry": crown_report.to_dict(),
            "mast_entry": mast_report.to_dict(),
        },
        "entry_effects": {
            "conventional": _entry_effect_payload(
                variants.crown_entry,
                variants.mast_entry,
                mode="conventional",
            ),
            "funnel": _entry_effect_payload(
                variants.crown_entry,
                variants.mast_entry,
                mode="funnel",
            ),
        },
        "first_burst_entry_comparison": variants.first_burst.to_dict(),
    }


def _entry_effect_payload(
    crown_entry: Any,
    mast_entry: Any,
    *,
    mode: str,
) -> dict[str, Any]:
    if mode not in {"conventional", "funnel"}:
        raise ValueError(f"unsupported entry effect mode: {mode}")

    def totals(actor: str | None = None) -> FirstBurstEntryDamageReport:
        if actor is None:
            crown_total = (
                crown_entry.overall.team_c
                if mode == "conventional"
                else crown_entry.overall.team_f
            )
            mast_total = (
                mast_entry.overall.team_c
                if mode == "conventional"
                else mast_entry.overall.team_f
            )
        else:
            crown_pair = crown_entry.by_character[actor]
            mast_pair = mast_entry.by_character[actor]
            crown_total = getattr(crown_pair, mode)
            mast_total = getattr(mast_pair, mode)
        return FirstBurstEntryDamageReport.from_totals(crown_total, mast_total)

    return {
        "team": totals().to_dict(),
        "by_character": {
            actor: totals(actor).to_dict()
            for actor in crown_entry.conventional_result.roster.members
        },
    }


def build_checkpoint_cases(payload: Mapping[str, Any]) -> tuple[SampleCase, ...]:
    payload = _mapping(payload, "request")
    _required_optional_keys(
        payload,
        {"roster", "combat"},
        {"baseline_rotation"},
        "request",
    )
    roster = _parse_roster(payload["roster"])
    combat_settings = _parse_combat(payload["combat"])
    baseline = _parse_baseline_rotation(payload.get("baseline_rotation"))
    fixed_build = BuildProfile.uniform(
        GearState.OL5,
        collection=SR15_COLLECTION,
    )
    cases: list[SampleCase] = []
    for b1_profile in B1_CHECKPOINTS:
        collection_stage = (
            "SR15"
            if b1_profile["collection"] == "SR15"
            or roster.b1 == "moran-favorite-item"
            else "none"
        )
        b1_build = BuildProfile.uniform(
            b1_profile["gear"],
            b1_profile["overload"],
            CollectionProfile(collection_stage),
        )
        for dealer_profile in DEALER_CHECKPOINTS:
            main_gear, main_overload = dealer_profile["main"]
            secondary_gear, secondary_overload = dealer_profile["secondary"]
            builds = {
                roster.b1: b1_build,
                roster.crown: fixed_build,
                roster.mast: fixed_build,
                roster.main_b3: BuildProfile.uniform(
                    main_gear,
                    main_overload,
                    SR15_COLLECTION,
                ),
                roster.secondary_b3: BuildProfile.uniform(
                    secondary_gear,
                    secondary_overload,
                    SR15_COLLECTION,
                ),
            }
            case_id = f"{b1_profile['id']}--{dealer_profile['id']}"
            cases.append(
                SampleCase(
                    case_id=case_id,
                    scenario=ResearchScenario(
                        roster=roster,
                        builds=builds,
                        combat_settings=combat_settings,
                        main_actor=roster.main_b3,
                        baseline_rotation=baseline,
                    ),
                    labels={
                        "b1_profile": b1_profile["id"],
                        "b1_label": b1_profile["label"],
                        "dealer_profile": dealer_profile["id"],
                        "dealer_label": dealer_profile["label"],
                    },
                )
            )
    return tuple(cases)


def calculate_checkpoint_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    cases = build_checkpoint_cases(payload)
    result = run_sample_batch(cases).to_dict()
    roster = cases[0].scenario.roster
    result["display_names"] = _display_names(roster)
    result["baseline_label"] = _baseline_label(
        cases[0].scenario.baseline_rotation
    )
    result["axes"] = {
        "x": "conventional_main_share",
        "y": "relative_change",
    }
    result["checkpoint_definitions"] = {
        "b1": [
            {
                "id": item["id"],
                "label": item["label"],
                "gear": item["gear"].value,
                "collection": (
                    "SR15"
                    if item["collection"] == "SR15"
                    or roster.b1 == "moran-favorite-item"
                    else "none"
                ),
                "overload": _overload_definition(item["overload"]),
            }
            for item in B1_CHECKPOINTS
        ],
        "dealer": [
            {
                "id": item["id"],
                "label": item["label"],
                "main": {
                    "gear": item["main"][0].value,
                    "overload": _overload_definition(item["main"][1]),
                },
                "secondary": {
                    "gear": item["secondary"][0].value,
                    "overload": _overload_definition(item["secondary"][1]),
                },
            }
            for item in DEALER_CHECKPOINTS
        ],
    }
    result["aggregate"] = _aggregate_checkpoint_results(result["results"])
    return result


def _overload_definition(profile: OverloadProfile) -> dict[str, int]:
    return {
        "atk_lines": profile.atk_lines,
        "element_lines": profile.element_lines,
        "ammo_lines": profile.ammo_lines,
    }


def _metric_stats(
    results: list[dict[str, Any]],
    key: str,
) -> dict[str, float | None]:
    values = [
        item["summary"][key]
        for item in results
        if item["summary"].get(key) is not None
    ]
    if not values:
        return {"minimum": None, "average": None, "maximum": None}
    return {
        "minimum": min(values),
        "average": sum(values) / len(values),
        "maximum": max(values),
    }


def _case_digest(item: dict[str, Any]) -> dict[str, Any]:
    summary = item["summary"]
    return {
        "case_id": item["case_id"],
        "labels": dict(item["labels"]),
        "relative_change": summary["relative_change"],
        "conventional_main_share": summary["conventional_main_share"],
        "break_even_main_share_c": summary["break_even_main_share_c"],
        "margin": summary["margin"],
        "outcome_band": summary["outcome_band"],
    }


def _group_checkpoint_results(
    results: list[dict[str, Any]],
    label_key: str,
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        groups.setdefault(item["labels"][label_key], []).append(item)
    grouped = []
    for label, items in groups.items():
        grouped.append(
            {
                "label": label,
                "count": len(items),
                "conventional_wins": sum(
                    "conventional" in item["summary"]["outcome_band"]
                    for item in items
                ),
                "funnel_wins": sum(
                    "funnel" in item["summary"]["outcome_band"]
                    for item in items
                ),
                "tie_band": sum(
                    item["summary"]["outcome_band"] == "tie_band"
                    for item in items
                ),
                "relative_change": _metric_stats(items, "relative_change"),
                "conventional_main_share": _metric_stats(
                    items, "conventional_main_share"
                ),
                "break_even_main_share_c": _metric_stats(
                    items, "break_even_main_share_c"
                ),
            }
        )
    return grouped


def _aggregate_checkpoint_results(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    if not results:
        raise ValueError("checkpoint aggregate requires at least one result")
    conventional_wins = sum(
        "conventional" in item["summary"]["outcome_band"] for item in results
    )
    funnel_wins = sum(
        "funnel" in item["summary"]["outcome_band"] for item in results
    )
    tie_band = sum(
        item["summary"]["outcome_band"] == "tie_band" for item in results
    )
    outcome_bands: dict[str, int] = {}
    for item in results:
        band = item["summary"]["outcome_band"]
        outcome_bands[band] = outcome_bands.get(band, 0) + 1
    valid_margins = [
        item for item in results if item["summary"].get("margin") is not None
    ]
    character_shares: dict[str, Any] = {}
    for actor in results[0]["summary"]["character_shares"]:
        conventional = [
            item["summary"]["character_shares"][actor]["conventional"]
            for item in results
        ]
        funnel = [
            item["summary"]["character_shares"][actor]["funnel"]
            for item in results
        ]
        character_shares[actor] = {
            "conventional": {
                "minimum": min(conventional),
                "average": sum(conventional) / len(conventional),
                "maximum": max(conventional),
            },
            "funnel": {
                "minimum": min(funnel),
                "average": sum(funnel) / len(funnel),
                "maximum": max(funnel),
            },
        }
    first_report = results[0]["report"]
    return {
        "sample_count": len(results),
        "outcomes": {
            "conventional_wins": conventional_wins,
            "funnel_wins": funnel_wins,
            "tie_band": tie_band,
            "bands": outcome_bands,
        },
        "relative_change": _metric_stats(results, "relative_change"),
        "conventional_main_share": _metric_stats(
            results, "conventional_main_share"
        ),
        "break_even_main_share_c": _metric_stats(
            results, "break_even_main_share_c"
        ),
        "margin": _metric_stats(results, "margin"),
        "extremes": {
            "most_funnel_favorable": _case_digest(
                max(results, key=lambda item: item["summary"]["relative_change"])
            ),
            "most_conventional_favorable": _case_digest(
                min(results, key=lambda item: item["summary"]["relative_change"])
            ),
            "closest_to_break_even": (
                None
                if not valid_margins
                else _case_digest(
                    min(
                        valid_margins,
                        key=lambda item: abs(item["summary"]["margin"]),
                    )
                )
            ),
        },
        "by_b1_profile": _group_checkpoint_results(results, "b1_label"),
        "by_dealer_profile": _group_checkpoint_results(results, "dealer_label"),
        "character_shares": character_shares,
        "conditions": {
            "roster": dict(first_report["scenario"]["roster"]),
            "baseline_rotation": first_report["scenario"]["baseline_rotation"],
            "combat_settings": dict(
                first_report["scenario"]["combat_settings"]
            ),
            "thresholds": dict(first_report["scenario"]["thresholds"]),
            "mechanics_signature": dict(first_report["mechanics_signature"]),
        },
    }


def _parse_roster(value: Any) -> TeamRoster:
    roster_payload = _mapping(value, "roster")
    _exact_keys(roster_payload, {"b1", "main_b3", "secondary_b3"}, "roster")
    roster = TeamRoster(
        b1=_actor_for_stage(roster_payload["b1"], "I", "roster.b1"),
        main_b3=_actor_for_stage(
            roster_payload["main_b3"], "III", "roster.main_b3"
        ),
        secondary_b3=_actor_for_stage(
            roster_payload["secondary_b3"], "III", "roster.secondary_b3"
        ),
    )
    if len(set(roster.members)) != len(roster.members):
        raise ValueError("파티에는 같은 캐릭터를 두 번 편성할 수 없습니다.")
    return roster


def _parse_combat(value: Any) -> CombatSettings:
    combat_payload = _mapping(value, "combat")
    _exact_keys(
        combat_payload,
        {"boss_def", "boss_element", "core_hit_rate_pct", "range_bonus_pct"},
        "combat",
    )
    boss_element = combat_payload["boss_element"]
    if boss_element == "":
        boss_element = None
    if boss_element is not None and not isinstance(boss_element, str):
        raise TypeError("combat.boss_element must be a string or null")
    return CombatSettings(
        boss_def=_number(combat_payload["boss_def"], "combat.boss_def"),
        boss_element=boss_element,
        core_hit_rate_pct=_number(
            combat_payload["core_hit_rate_pct"], "combat.core_hit_rate_pct"
        ),
        range_bonus_pct=_number(
            combat_payload["range_bonus_pct"], "combat.range_bonus_pct"
        ),
    )


def _display_names(roster: TeamRoster) -> dict[str, str]:
    return {
        actor: STANDARD_CHARACTER_CATALOG.require(actor).name
        for actor in roster.members
    }


def _build_profile(payload: Mapping[str, Any], actor: str) -> BuildProfile:
    _exact_keys(
        payload,
        {
            "gear_states",
            "collection_stage",
            "atk_lines",
            "element_lines",
            "ammo_lines",
        },
        f"builds.{actor}",
    )
    gear_payload = _mapping(payload["gear_states"], f"builds.{actor}.gear_states")
    _exact_keys(
        gear_payload,
        {slot.value for slot in GEAR_SLOTS},
        f"builds.{actor}.gear_states",
    )
    try:
        states = [GearState(gear_payload[slot.value]) for slot in GEAR_SLOTS]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"builds.{actor}.gear_states contains an unsupported state") from exc
    return BuildProfile(
        equipment=EquipmentLoadout.from_states(*states),
        overload=OverloadProfile(
            atk_lines=_non_negative_int(payload["atk_lines"], f"builds.{actor}.atk_lines"),
            element_lines=_non_negative_int(
                payload["element_lines"], f"builds.{actor}.element_lines"
            ),
            ammo_lines=_non_negative_int(
                payload["ammo_lines"], f"builds.{actor}.ammo_lines"
            ),
        ),
        collection=CollectionProfile(
            _string(payload["collection_stage"], f"builds.{actor}.collection_stage")
        ),
    )


def _actor_for_stage(value: Any, stage: str, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{path} must be a non-empty string")
    definition = STANDARD_CHARACTER_CATALOG.require(value)
    if definition.burst_stage != stage:
        raise ValueError(f"{path} must be a Burst {stage} character")
    return value


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{path} must be a non-empty string")
    return value


def _exact_keys(payload: Mapping[str, Any], expected: set[str], path: str) -> None:
    actual = set(payload)
    if actual != expected:
        raise ValueError(
            f"{path} fields do not match: missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _required_optional_keys(
    payload: Mapping[str, Any],
    required: set[str],
    optional: set[str],
    path: str,
) -> None:
    actual = set(payload)
    missing = required - actual
    unknown = actual - required - optional
    if missing or unknown:
        raise ValueError(
            f"{path} fields do not match: missing={sorted(missing)}, "
            f"unknown={sorted(unknown)}"
        )


def _parse_baseline_rotation(value: Any) -> str:
    name = CROWN_CROWN_MAST.name if value is None else _string(
        value, "baseline_rotation"
    )
    if name not in BASELINE_ROTATIONS:
        raise ValueError(f"unsupported baseline rotation: {name}")
    return name


def _baseline_label(name: str) -> str:
    return next(
        item["label"]
        for item in BASELINE_ROTATION_DEFINITIONS
        if item["id"] == name
    )


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be numeric")
    return float(value)


def _non_negative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 0:
        raise ValueError(f"{path} must be non-negative")
    return value


class InterfaceRequestHandler(BaseHTTPRequestHandler):
    server_version = "CrownMastInterface/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/meta":
            self._json_response(HTTPStatus.OK, interface_metadata())
            return
        relative = "index.html" if path == "/" else path.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in candidate.parents or not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = CONTENT_TYPES.get(candidate.suffix)
        if content_type is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in {"/api/calculate", "/api/checkpoints"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("request body size is invalid")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = (
                calculate_interface_payload(payload)
                if path == "/api/calculate"
                else calculate_checkpoint_payload(payload)
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"error": str(exc) or type(exc).__name__},
            )
            return
        self._json_response(HTTPStatus.OK, result)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _json_response(self, status: HTTPStatus, payload: Mapping[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), InterfaceRequestHandler)
    print(f"Crown–Mast interface: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Crown–Mast research interface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
