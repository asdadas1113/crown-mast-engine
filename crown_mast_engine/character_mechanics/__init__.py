from .anis_star import AnisStarSkillHook
from .bready import BreadySkillHook
from .cinderella import CinderellaSkillHook
from .cinderella_crystal_wave import CinderellaCrystalWaveSkillHook
from .crown import CrownSkillHook
from .epinel import EpinelSkillHook
from .helm import HelmSkillHook
from .liberalio import LiberalioSkillHook
from .little_mermaid import LittleMermaidSkillHook
from .liter import LiterSkillHook
from .milk_blooming_bunny import MilkBloomingBunnySkillHook
from .moran_favorite_item import MoranFavoriteItemSkillHook
from .neon_vision_eye import NeonVisionEyeSkillHook
from .phantom_favorite_item import PhantomFavoriteItemSkillHook
from .quency_escape_queen import QuencyEscapeQueenSkillHook
from .rapi_red_hood import RapiRedHoodSkillHook
from .raven import RavenSkillHook
from .scarlet_black_shadow import ScarletBlackShadowSkillHook
from .snow_white_heavy_arms import SnowWhiteHeavyArmsSkillHook
from .. import combat as _combat
from ..mechanics import SkillHookRegistry
from ..weapon_cadence import generate_weapon_shots as _generate_weapon_shots


# Engine imports the combat generator after loading this registry. Install the
# audited triggered-charge extension here so existing ordinary weapons retain the
# baseline generator while original Cinderella can use her reload-reset cadence.
_combat.generate_weapon_shots = _generate_weapon_shots


STANDARD_SKILL_HOOKS = SkillHookRegistry(
    {
        "bready": BreadySkillHook,
        "cinderella": CinderellaSkillHook,
        "cinderella-crystal-wave": CinderellaCrystalWaveSkillHook,
        "crown": CrownSkillHook,
        "rapi-red-hood": RapiRedHoodSkillHook,
        "helm": HelmSkillHook,
        "liberalio": LiberalioSkillHook,
        "liter": LiterSkillHook,
        "milk-blooming-bunny": MilkBloomingBunnySkillHook,
        "phantom": PhantomFavoriteItemSkillHook,
        "quency-escape-queen": QuencyEscapeQueenSkillHook,
        "raven": RavenSkillHook,
        "scarlet-black-shadow": ScarletBlackShadowSkillHook,
        "anis-star": AnisStarSkillHook,
        "moran-favorite-item": MoranFavoriteItemSkillHook,
        "little-mermaid": LittleMermaidSkillHook,
        "snow-white-heavy-arms": SnowWhiteHeavyArmsSkillHook,
        "epinel": EpinelSkillHook,
        "neon-vision-eye": NeonVisionEyeSkillHook,
    },
    revision="standard-hooks-r13-audited-cinderella",
)


__all__ = [
    "AnisStarSkillHook",
    "BreadySkillHook",
    "CinderellaSkillHook",
    "CinderellaCrystalWaveSkillHook",
    "CrownSkillHook",
    "EpinelSkillHook",
    "HelmSkillHook",
    "LiberalioSkillHook",
    "LittleMermaidSkillHook",
    "LiterSkillHook",
    "MilkBloomingBunnySkillHook",
    "MoranFavoriteItemSkillHook",
    "NeonVisionEyeSkillHook",
    "PhantomFavoriteItemSkillHook",
    "QuencyEscapeQueenSkillHook",
    "RapiRedHoodSkillHook",
    "RavenSkillHook",
    "ScarletBlackShadowSkillHook",
    "SnowWhiteHeavyArmsSkillHook",
    "STANDARD_SKILL_HOOKS",
]
