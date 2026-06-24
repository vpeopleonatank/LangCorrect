from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.convert_to_onnx import SIDECAR_FILES as EXPORT_SIDECAR_FILES
from scripts.quantize_model import SIDECAR_FILES as QUANTIZE_SIDECAR_FILES
from vicorrect.runtime import ModelSetupError, ModelArtifactPaths


class RuntimeTests(unittest.TestCase):
    def test_missing_model_artifacts_raise_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            with self.assertRaises(ModelSetupError) as context:
                ModelArtifactPaths.from_dir(model_dir)

        self.assertIn("scripts/download_model.py", str(context.exception))
        self.assertIn("VICORRECT_MODEL_DIR", str(context.exception))

    def test_missing_bartpho_dictionary_is_reported_as_setup_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            for filename in [
                "encoder_model.onnx",
                "decoder_model.onnx",
                "decoder_with_past_model.onnx",
                "config.json",
                "tokenizer_config.json",
                "sentencepiece.bpe.model",
            ]:
                (model_dir / filename).write_text("stub", encoding="utf-8")

            with self.assertRaises(ModelSetupError) as context:
                ModelArtifactPaths.from_dir(model_dir)

        self.assertIn("dict.txt", str(context.exception))

    def test_model_export_scripts_copy_bartpho_dictionary(self) -> None:
        self.assertIn("dict.txt", EXPORT_SIDECAR_FILES)
        self.assertIn("dict.txt", QUANTIZE_SIDECAR_FILES)


if __name__ == "__main__":
    unittest.main()
