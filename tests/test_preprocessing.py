from __future__ import annotations

import unittest

from vicorrect.preprocessing import TextPreprocessor


class WordCounter:
    def count_tokens(self, text: str) -> int:
        return len(text.split())


class PreprocessorTests(unittest.TestCase):
    def test_prepare_preserves_newlines_and_order(self) -> None:
        text = "Xin chao ban.\n\nToi dang hoc AI. Cam on ban."
        preprocessor = TextPreprocessor(max_tokens=20, token_counter=WordCounter())

        document = preprocessor.prepare(text)

        self.assertEqual(document.sentence_count, 3)
        self.assertEqual(document.original_text(), text)
        self.assertEqual(document.chunks[0].trailing, "\n\n")
        self.assertEqual(document.chunks[1].trailing, " ")

    def test_prepare_splits_overlong_sentence_without_losing_content(self) -> None:
        text = "mot hai ba bon nam sau bay tam chin muoi."
        preprocessor = TextPreprocessor(max_tokens=3, token_counter=WordCounter())

        document = preprocessor.prepare(text)

        self.assertEqual(document.sentence_count, 1)
        self.assertGreater(len(document.chunks), 1)
        self.assertEqual(document.original_text(), text)
        self.assertTrue(all(len(chunk.text.split()) <= 3 for chunk in document.chunks))


if __name__ == "__main__":
    unittest.main()
