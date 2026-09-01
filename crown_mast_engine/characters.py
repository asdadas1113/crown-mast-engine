from __future__ import annotations

import json
from dataclasses import dataclass, replace
from importlib.resources import files
from math import isfinite
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class WeaponProfile:
    weapon_type: str
    normal_attack_pct: float
    core_attack_pct: float
    ammo: int
    reload_frames: int
    charge_frames: int
    charge_multiplier_pct: float
    hits_per_shot: int
    burst_gauge_per_shot: float
    charge_release_recovery_frames: int = 22


@dataclass(frozen=True)
class CharacterDefinition:
    slug: str
    name: str
    unit_class: str
    burst_stage: str
    burst_cooldown_sec: float
    element: str
    progression_atk: float
    base_crit_rate_pct: float
    base_crit_damage_pct: float
    weapon: WeaponProfile
    skills: Mapping[str, Mapping[str, float]]
    extra_advantage_against: tuple[str, ...] = ()

    def skill_value(self, skill: str, key: str) -> float:
        try:
            return self.skills[skill][key]
        except KeyError as exc:
            raise KeyError(f"missing skill value: {self.slug}.{skill}.{key}") from exc


@dataclass(frozen=True)
class CharacterDataScope:
    level: int
    gear: str
    core: int
    skill_levels: tuple[int, int, int]
    source_revision: str


class CharacterCatalog:
    def __init__(
        self,
        definitions: tuple[CharacterDefinition, ...],
        scope: CharacterDataScope,
    ) -> None:
        by_slug = {definition.slug: definition for definition in definitions}
        if len(by_slug) != len(definitions):
            raise ValueError("character slugs must be unique")
        self._by_slug = MappingProxyType(by_slug)
        self.scope = scope

    @property
    def definitions(self) -> tuple[CharacterDefinition, ...]:
        return tuple(self._by_slug.values())

    def get(self, slug: str) -> CharacterDefinition | None:
        return self._by_slug.get(slug)

    def require(self, slug: str) -> CharacterDefinition:
        definition = self.get(slug)
        if definition is None:
            raise KeyError(f"unknown character: {slug}")
        return definition

    def with_skill_value(
        self,
        slug: str,
        skill: str,
        key: str,
        value: float,
    ) -> CharacterCatalog:
        definition = self.require(slug)
        definition.skill_value(skill, key)
        value = float(value)
        if not isfinite(value):
            raise ValueError("skill value must be finite")

        skills = {
            skill_name: dict(values)
            for skill_name, values in definition.skills.items()
        }
        skills[skill][key] = value
        replacement = replace(
            definition,
            skills=MappingProxyType(
                {
                    skill_name: MappingProxyType(values)
                    for skill_name, values in skills.items()
                }
            ),
        )
        definitions = tuple(
            replacement if item.slug == slug else item
            for item in self.definitions
        )
        return CharacterCatalog(definitions, self.scope)


def load_character_catalog() -> CharacterCatalog:
    path = files("crown_mast_engine").joinpath("data", "characters.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"unsupported character schema: {payload.get('schema_version')}")

    scope_data = payload["scope"]
    scope = CharacterDataScope(
        level=int(scope_data["level"]),
        gear=str(scope_data["gear"]),
        core=int(scope_data["core"]),
        skill_levels=tuple(int(value) for value in scope_data["skill_levels"]),
        source_revision=str(scope_data["source_revision"]),
    )

    definitions: list[CharacterDefinition] = []
    for item in payload["characters"]:
        weapon = WeaponProfile(**item["weapon"])
        skills = MappingProxyType(
            {
                skill: MappingProxyType({key: float(value) for key, value in values.items()})
                for skill, values in item["skills"].items()
            }
        )
        definitions.append(
            CharacterDefinition(
                slug=str(item["slug"]),
                name=str(item["name"]),
                unit_class=str(item["unit_class"]),
                burst_stage=str(item["burst_stage"]),
                burst_cooldown_sec=float(item["burst_cooldown_sec"]),
                element=str(item["element"]),
                progression_atk=float(item["progression_atk"]),
                base_crit_rate_pct=float(item["base_crit_rate_pct"]),
                base_crit_damage_pct=float(item["base_crit_damage_pct"]),
                weapon=weapon,
                skills=skills,
                extra_advantage_against=tuple(
                    str(value)
                    for value in item.get("extra_advantage_against", ())
                ),
            )
        )
    return CharacterCatalog(tuple(definitions), scope)


STANDARD_CHARACTER_CATALOG = load_character_catalog()
