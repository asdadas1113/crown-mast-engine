import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class HandoffPolicyTests(unittest.TestCase):
    def test_agent_entrypoint_requires_current_handoff_protocol(self) -> None:
        policy = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/CURRENT_RESEARCH_HANDOFF.md", policy)
        self.assertIn("docs/AI_HANDOFF_PROTOCOL.md", policy)
        self.assertIn("사용자의 명시적 승인 없이 실행하지 않는다", policy)

    def test_current_pointer_names_the_canonical_handoff(self) -> None:
        handoff = (
            REPOSITORY_ROOT / "docs" / "CURRENT_RESEARCH_HANDOFF.md"
        ).read_text(encoding="utf-8")
        self.assertIn("CURRENT_RESEARCH_HANDOFF_2026-09-07.md", handoff)
        self.assertIn("crown-mast-study-01-exploratory-v1", handoff)
        self.assertIn("28,188/28,188", handoff)
        self.assertIn("full regression **327/327**", handoff)

    def test_protocol_isolates_future_code_changes_from_completed_runs(self) -> None:
        protocol = (
            REPOSITORY_ROOT / "docs" / "AI_HANDOFF_PROTOCOL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("기존 scenario/raw/aggregate/manifest를 덮어쓰지 않는다", protocol)
        self.assertIn("research/post-study1-<topic>", protocol)
        self.assertIn("변경된 코드로 다시 계산해야 하면 새 `run_id`", protocol)
        self.assertIn("원본 manifest는 보존", protocol)


if __name__ == "__main__":
    unittest.main()
