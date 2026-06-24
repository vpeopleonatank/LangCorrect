from __future__ import annotations

import unittest

from vicorrect.preprocessing import TextPreprocessor
from vicorrect.workflow import CorrectionWorkflow, _normalize_chunk_output


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
                "toi dang hoc AI": "tôi đang học AI.",
                "Cam on ban": "Cảm ơn bạn.",
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
                "muoi": "mười.",
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

    def test_chunk_output_preserves_source_punctuation_and_case(self) -> None:
        self.assertEqual(
            _normalize_chunk_output(
                "Hôm nay toi đi hoc ở truòng từ rất som,",
                "Hôm nay tôi đi học ở trường từ rất sớm,.",
            ),
            "Hôm nay tôi đi học ở trường từ rất sớm,",
        )
        self.assertEqual(
            _normalize_chunk_output(
                "mình gặp một nguời bạn cu tên là Nam,",
                "Mình gặp một người bạn cũ tên là Nam.",
            ),
            "mình gặp một người bạn cũ tên là Nam,",
        )

    def test_workflow_uses_stripped_chunks_and_restores_original_punctuation(self) -> None:
        text = (
            "Hôm nay toi đi hoc ở truòng từ rất som, nhưng vì quên mang theo sach vở nên mình phải quay về nhà lấy."
        )
        adapter = FakeAdapter(
            {
                "Hôm nay toi đi hoc ở truòng từ rất som": "Hôm nay tôi đi học ở trường từ rất sớm.",
                "nhưng vì quên mang theo sach vở nên mình phải quay về nhà lấy": (
                    "Nhưng vì quên mang theo sách vở nên mình phải quay về nhà lấy."
                ),
            }
        )
        workflow = CorrectionWorkflow(
            adapter=adapter,
            preprocessor=TextPreprocessor(max_tokens=16, token_counter=adapter),
        )

        result = workflow.run(text)

        self.assertEqual(
            result.corrected_text,
            "Hôm nay tôi đi học ở trường từ rất sớm, nhưng vì quên mang theo sách vở nên mình phải quay về nhà lấy.",
        )


if __name__ == "__main__":
    unittest.main()
