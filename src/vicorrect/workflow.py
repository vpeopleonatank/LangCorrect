from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .diffing import DiffChange, DiffEngine
from .preprocessing import PreparedDocument, TextPreprocessor
from .runtime import CorrectionAdapter


ProgressCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class CorrectionResult:
    original_text: str
    corrected_text: str
    diff_html: str
    changes: tuple[DiffChange, ...]
    prepared_document: PreparedDocument


class CorrectionWorkflow:
    def __init__(
        self,
        adapter: CorrectionAdapter,
        preprocessor: TextPreprocessor,
        diff_engine: DiffEngine | None = None,
    ) -> None:
        self.adapter = adapter
        self.preprocessor = preprocessor
        self.diff_engine = diff_engine or DiffEngine()

    def run(
        self,
        text: str,
        progress_callback: ProgressCallback | None = None,
    ) -> CorrectionResult:
        self.adapter.load()
        document = self.preprocessor.prepare(text)

        corrected_chunks: list[str] = []
        last_sentence = -1
        completed_sentences = 0

        for chunk in document.chunks:
            corrected_chunks.append(self.adapter.correct(chunk.text))
            if chunk.sentence_index != last_sentence:
                if last_sentence != -1:
                    completed_sentences += 1
                    if progress_callback is not None:
                        progress_callback(completed_sentences, document.sentence_count)
                last_sentence = chunk.sentence_index

        if document.sentence_count:
            completed_sentences += 1
            if progress_callback is not None:
                progress_callback(completed_sentences, document.sentence_count)

        corrected_text = document.reassemble(corrected_chunks)
        changes = tuple(self.diff_engine.build_changes(text, corrected_text))
        return CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            diff_html=self.diff_engine.render_html(text, corrected_text),
            changes=changes,
            prepared_document=document,
        )
