import unittest

from crown_mast_engine import simulate_rotation
from crown_mast_engine.models import EventType, TeamRoster
from crown_mast_engine.rotations import CROWN_CROWN_MAST
from crown_mast_engine.timeline import RAID14_TIMELINE


class TeamRosterValidationTests(unittest.TestCase):
    def test_rapi_b1_cannot_also_be_main_b3(self) -> None:
        with self.assertRaisesRegex(ValueError, "같은 캐릭터"):
            TeamRoster(
                b1="rapi-red-hood",
                main_b3="rapi-red-hood",
                secondary_b3="helm",
            )

    def test_rapi_b1_cannot_also_be_secondary_b3(self) -> None:
        with self.assertRaisesRegex(ValueError, "같은 캐릭터"):
            TeamRoster(
                b1="rapi-red-hood",
                main_b3="scarlet-black-shadow",
                secondary_b3="rapi-red-hood",
            )

    def test_rapi_b1_never_receives_a_b3_stage_event(self) -> None:
        roster = TeamRoster(
            b1="rapi-red-hood",
            main_b3="scarlet-black-shadow",
            secondary_b3="helm",
        )
        result = simulate_rotation(
            CROWN_CROWN_MAST,
            roster=roster,
            timeline=RAID14_TIMELINE,
        )
        self.assertFalse(
            any(
                event.event_type == EventType.B3_STAGE_ENTER
                and event.actor == "rapi-red-hood"
                for event in result.events
            )
        )


if __name__ == "__main__":
    unittest.main()
