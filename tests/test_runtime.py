from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vicorrect.runtime import ModelSetupError, ModelArtifactPaths


class RuntimeTests(unittest.TestCase):
    def test_missing_model_artifacts_raise_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            with self.assertRaises(ModelSetupError) as context:
                ModelArtifactPaths.from_dir(model_dir)

        self.assertIn("scripts/download_model.py", str(context.exception))
        self.assertIn("VICORRECT_MODEL_DIR", str(context.exception))


if __name__ == "__main__":
    unittest.main()
