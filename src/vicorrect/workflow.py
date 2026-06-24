from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable

from .diffing import DiffChange, DiffEngine
from .preprocessing import PreparedDocument, TextPreprocessor
from .runtime import CorrectionAdapter


ProgressCallback = Callable[[int, int], None]
_TRAILING_PUNCTUATION = re.compile(r"^(.*?)([\"'”’)\]}.,;:?!…]+)?$")


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
            corrected = self.adapter.correct(_strip_trailing_punctuation(chunk.text))
            corrected_chunks.append(_normalize_chunk_output(chunk.text, corrected))
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


def _strip_trailing_punctuation(text: str) -> str:
    core, _ = _split_trailing_punctuation(text)
    return core


def _normalize_chunk_output(source: str, corrected: str) -> str:
    source_core, source_suffix = _split_trailing_punctuation(source)
    corrected_core, _ = _split_trailing_punctuation(corrected.strip())
    corrected_core = _preserve_leading_case(source_core, corrected_core)
    return f"{corrected_core}{source_suffix}"


def _split_trailing_punctuation(text: str) -> tuple[str, str]:
    match = _TRAILING_PUNCTUATION.match(text)
    if match is None:
        return text, ""
    return match.group(1), match.group(2) or ""


def _preserve_leading_case(source: str, corrected: str) -> str:
    source_index = next((index for index, char in enumerate(source) if char.isalpha()), None)
    corrected_index = next((index for index, char in enumerate(corrected) if char.isalpha()), None)
    if source_index is None or corrected_index is None:
        return corrected

    corrected_chars = list(corrected)
    if source[source_index].islower() and corrected_chars[corrected_index].isupper():
        corrected_chars[corrected_index] = corrected_chars[corrected_index].lower()
    elif source[source_index].isupper() and corrected_chars[corrected_index].islower():
        corrected_chars[corrected_index] = corrected_chars[corrected_index].upper()
    return "".join(corrected_chars)
