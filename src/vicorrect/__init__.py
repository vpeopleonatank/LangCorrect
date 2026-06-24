"""ViCorrect package."""

from .diffing import ChangeType, DiffChange, DiffEngine
from .preprocessing import PreparedChunk, PreparedDocument, TextPreprocessor
from .workflow import CorrectionResult, CorrectionWorkflow

__all__ = [
    "ChangeType",
    "CorrectionResult",
    "CorrectionWorkflow",
    "DiffChange",
    "DiffEngine",
    "PreparedChunk",
    "PreparedDocument",
    "TextPreprocessor",
]
