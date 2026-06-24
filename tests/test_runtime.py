from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.convert_to_onnx import SIDECAR_FILES as EXPORT_SIDECAR_FILES
from scripts.quantize_model import SIDECAR_FILES as QUANTIZE_SIDECAR_FILES
from vicorrect.runtime import (
    ModelArtifactPaths,
    ModelSetupError,
    _load_local_tokenizer,
    default_model_dir,
)


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

    def test_load_local_tokenizer_falls_back_to_explicit_bartpho_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            for filename in [
                "encoder_model.onnx",
                "decoder_model.onnx",
                "decoder_with_past_model.onnx",
                "config.json",
                "tokenizer_config.json",
                "sentencepiece.bpe.model",
                "dict.txt",
            ]:
                (model_dir / filename).write_text("stub", encoding="utf-8")

            artifacts = ModelArtifactPaths.from_dir(model_dir)
            fallback_tokenizer = object()
            auto_tokenizer = Mock()
            auto_tokenizer.from_pretrained.side_effect = TypeError(
                "expected str, bytes or os.PathLike object, not NoneType"
            )
            bartpho_tokenizer = Mock(return_value=fallback_tokenizer)

            tokenizer = _load_local_tokenizer(
                artifacts,
                auto_tokenizer_cls=auto_tokenizer,
                bartpho_tokenizer_cls=bartpho_tokenizer,
            )

        self.assertIs(tokenizer, fallback_tokenizer)
        bartpho_tokenizer.assert_called_once_with(
            vocab_file=str(artifacts.sentencepiece_model),
            monolingual_vocab_file=str(artifacts.monolingual_vocab),
        )

    def test_default_model_dir_prefers_non_quantized_onnx_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            model_root = repo_root / "models"
            preferred = model_root / "bartpho-correction-v2-onnx"
            fallback = model_root / "bartpho-correction-v2-onnx-int8"
            preferred.mkdir(parents=True)
            fallback.mkdir(parents=True)

            with patch.dict("os.environ", {}, clear=True):
                with patch("vicorrect.runtime.Path.resolve", return_value=repo_root / "src" / "vicorrect" / "runtime.py"):
                    self.assertEqual(default_model_dir(), preferred)

    def test_default_model_dir_falls_back_to_quantized_onnx(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            model_root = repo_root / "models"
            fallback = model_root / "bartpho-correction-v2-onnx-int8"
            fallback.mkdir(parents=True)

            with patch.dict("os.environ", {}, clear=True):
                with patch("vicorrect.runtime.Path.resolve", return_value=repo_root / "src" / "vicorrect" / "runtime.py"):
                    self.assertEqual(default_model_dir(), fallback)

    def test_default_model_dir_uses_env_override(self) -> None:
        configured = r"D:\custom-model"
        with patch.dict("os.environ", {"VICORRECT_MODEL_DIR": configured}, clear=True):
            self.assertEqual(default_model_dir(), Path(configured))


if __name__ == "__main__":
    unittest.main()
