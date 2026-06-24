from __future__ import annotations

import unittest

from vicorrect.preprocessing import TextPreprocessor
from vicorrect.workflow import CorrectionWorkflow


class FakeAdapter:
    def __init__(self, replacements: dict[str, str]) -> None:
        self.replacements = replacements
        self.loaded = False

    def load(self) -> None:
        self.loaded = True

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def correct(self, text: str) -> str:
        return self.replacements.get(text, text)


class WorkflowTests(unittest.TestCase):
    def test_correction_flow_reassembles_chunks(self) -> None:
        adapter = FakeAdapter(
            {
                "toi dang hoc AI.": "tôi đang học AI.",
                "Cam on ban.": "Cảm ơn bạn.",
            }
        )
        workflow = CorrectionWorkflow(
            adapter=adapter,
            preprocessor=TextPreprocessor(max_tokens=20, token_counter=adapter),
        )

        result = workflow.run("toi dang hoc AI.\nCam on ban.")

        self.assertTrue(adapter.loaded)
        self.assertEqual(result.corrected_text, "tôi đang học AI.\nCảm ơn bạn.")
        self.assertIn("replaced", result.diff_html)

    def test_progress_is_reported_per_sentence_even_when_sentence_splits(self) -> None:
        text = "mot hai ba bon nam sau bay tam chin muoi."
        adapter = FakeAdapter(
            {
                "mot hai ba": "một hai ba",
                "bon nam sau": "bốn năm sáu",
                "bay tam chin": "bảy tám chín",
                "muoi.": "mười.",
            }
        )
        workflow = CorrectionWorkflow(
            adapter=adapter,
            preprocessor=TextPreprocessor(max_tokens=3, token_counter=adapter),
        )
        progress: list[tuple[int, int]] = []

        result = workflow.run(text, lambda done, total: progress.append((done, total)))

        self.assertEqual(progress, [(1, 1)])
        self.assertEqual(result.corrected_text, "một hai ba bốn năm sáu bảy tám chín mười.")


if __name__ == "__main__":
    unittest.main()
