from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.manual_test_hf_model import format_result, load_texts, resolve_device


class ManualTestScriptTests(unittest.TestCase):
    def test_load_texts_merges_cli_values_and_non_empty_file_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "inputs.txt"
            file_path.write_text("dong thu nhat\n\n dong thu hai \n", encoding="utf-8")

            texts = load_texts(["cau tu cli", "   "], file_path)

        self.assertEqual(texts, ["cau tu cli", "dong thu nhat", "dong thu hai"])

    def test_resolve_device_auto_falls_back_to_cpu(self) -> None:
        self.assertEqual(resolve_device("auto", cuda_available=False), "cpu")

    def test_resolve_device_cuda_requires_available_gpu(self) -> None:
        with self.assertRaises(RuntimeError):
            resolve_device("cuda", cuda_available=False)

    def test_format_result_labels_input_and_output(self) -> None:
        formatted = format_result(3, "toi dang hoc", "tôi đang học")

        self.assertIn("[3] Input : toi dang hoc", formatted)
        self.assertIn("[3] Output: tôi đang học", formatted)


if __name__ == "__main__":
    unittest.main()
