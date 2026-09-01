from .anis_star import AnisStarSkillHook
from .bready import BreadySkillHook
from .crown import CrownSkillHook
from .epinel import EpinelSkillHook
from .helm import HelmSkillHook
from .liberalio import LiberalioSkillHook
from .little_mermaid import LittleMermaidSkillHook
from .liter import LiterSkillHook
from .moran_favorite_item import MoranFavoriteItemSkillHook
from .neon_vision_eye import NeonVisionEyeSkillHook
from .rapi_red_hood import RapiRedHoodSkillHook
from .scarlet_black_shadow import ScarletBlackShadowSkillHook
from .snow_white_heavy_arms import SnowWhiteHeavyArmsSkillHook
from ..mechanics import SkillHookRegistry


STANDARD_SKILL_HOOKS = SkillHookRegistry(
    {
        "bready": BreadySkillHook,
        "crown": CrownSkillHook,
        "rapi-red-hood": RapiRedHoodSkillHook,
        "helm": HelmSkillHook,
        "liberalio": LiberalioSkillHook,
        "liter": LiterSkillHook,
        "scarlet-black-shadow": ScarletBlackShadowSkillHook,
        "anis-star": AnisStarSkillHook,
        "moran-favorite-item": MoranFavoriteItemSkillHook,
        "little-mermaid": LittleMermaidSkillHook,
        "snow-white-heavy-arms": SnowWhiteHeavyArmsSkillHook,
        "epinel": EpinelSkillHook,
        "neon-vision-eye": NeonVisionEyeSkillHook,
    },
    revision="standard-hooks-r8",
)


__all__ = [
    "AnisStarSkillHook",
    "BreadySkillHook",
    "CrownSkillHook",
    "EpinelSkillHook",
    "HelmSkillHook",
    "LiberalioSkillHook",
    "LittleMermaidSkillHook",
    "LiterSkillHook",
    "MoranFavoriteItemSkillHook",
    "NeonVisionEyeSkillHook",
    "RapiRedHoodSkillHook",
    "ScarletBlackShadowSkillHook",
    "SnowWhiteHeavyArmsSkillHook",
    "STANDARD_SKILL_HOOKS",
]
