from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


class TokenCounter(Protocol):
    def count_tokens(self, text: str) -> int:
        """Return the token count for a text chunk."""


class WhitespaceTokenCounter:
    def count_tokens(self, text: str) -> int:
        return len(re.findall(r"\S+", text))


@dataclass(frozen=True)
class PreparedChunk:
    sentence_index: int
    text: str
    trailing: str


@dataclass(frozen=True)
class PreparedDocument:
    prefix: str
    chunks: tuple[PreparedChunk, ...]
    sentence_count: int

    def original_text(self) -> str:
        return self.reassemble([chunk.text for chunk in self.chunks])

    def reassemble(self, corrected_chunks: list[str]) -> str:
        if len(corrected_chunks) != len(self.chunks):
            raise ValueError("Chunk count mismatch during reassembly.")

        parts = [self.prefix]
        for chunk, corrected in zip(self.chunks, corrected_chunks, strict=True):
            parts.append(corrected)
            parts.append(chunk.trailing)
        return "".join(parts)


class TextPreprocessor:
    """Split text into sentence-sized chunks while preserving separators."""

    _PARAGRAPH_SPLIT = re.compile(r"(\n+)")

    def __init__(
        self,
        max_tokens: int = 256,
        token_counter: TokenCounter | None = None,
    ) -> None:
        self.max_tokens = max_tokens
        self.token_counter = token_counter or WhitespaceTokenCounter()

    def prepare(self, text: str) -> PreparedDocument:
        if not text:
            return PreparedDocument(prefix="", chunks=(), sentence_count=0)

        prefix_match = re.match(r"^\s*", text)
        prefix = prefix_match.group(0) if prefix_match else ""
        body = text[len(prefix) :]
        chunks: list[PreparedChunk] = []
        sentence_index = 0

        for part in self._PARAGRAPH_SPLIT.split(body):
            if not part:
                continue
            if part.startswith("\n"):
                if chunks:
                    previous = chunks[-1]
                    chunks[-1] = PreparedChunk(
                        sentence_index=previous.sentence_index,
                        text=previous.text,
                        trailing=previous.trailing + part,
                    )
                else:
                    prefix += part
                continue

            for sentence_text, trailing in self._split_sentences(part):
                for split_text, split_trailing in self._split_overlong_sentence(
                    sentence_text, trailing
                ):
                    chunks.append(
                        PreparedChunk(
                            sentence_index=sentence_index,
                            text=split_text,
                            trailing=split_trailing,
                        )
                    )
                sentence_index += 1

        return PreparedDocument(
            prefix=prefix,
            chunks=tuple(chunks),
            sentence_count=sentence_index,
        )

    def _split_sentences(self, paragraph: str) -> list[tuple[str, str]]:
        sentences: list[tuple[str, str]] = []
        start = 0
        index = 0

        while index < len(paragraph):
            char = paragraph[index]
            if char in ".?!…":
                boundary = index + 1
                while boundary < len(paragraph) and paragraph[boundary] in "\"'”’)]}":
                    boundary += 1
                if boundary == len(paragraph) or paragraph[boundary].isspace():
                    trailing_end = boundary
                    while trailing_end < len(paragraph) and paragraph[trailing_end] == " ":
                        trailing_end += 1
                    sentence = paragraph[start:boundary]
                    trailing = paragraph[boundary:trailing_end]
                    if sentence:
                        sentences.append((sentence, trailing))
                    start = trailing_end
                    index = trailing_end
                    continue
            index += 1

        if start < len(paragraph):
            sentences.append((paragraph[start:], ""))
        return sentences

    def _split_overlong_sentence(
        self, sentence: str, trailing: str
    ) -> list[tuple[str, str]]:
        if self.token_counter.count_tokens(sentence) <= self.max_tokens:
            return [(sentence, trailing)]

        parts = self._split_by_clause(sentence)
        chunks = self._pack_parts(parts)
        result: list[tuple[str, str]] = []
        for index, chunk in enumerate(chunks):
            if index == len(chunks) - 1:
                result.append((chunk.rstrip(" "), trailing or chunk[len(chunk.rstrip(" ")) :]))
            else:
                stripped = chunk.rstrip(" ")
                result.append((stripped, chunk[len(stripped) :]))
        return result

    def _split_by_clause(self, sentence: str) -> list[str]:
        parts = re.findall(r"[^,;:]+(?:[,;:]\s*|$)", sentence)
        if len(parts) == 1:
            return re.findall(r"\S+\s*", sentence)
        return parts

    def _pack_parts(self, parts: list[str]) -> list[str]:
        packed: list[str] = []
        current = ""

        for part in parts:
            candidate = f"{current}{part}"
            if current and self.token_counter.count_tokens(candidate.rstrip(" ")) > self.max_tokens:
                packed.append(current)
                current = part
                continue

            if not current and self.token_counter.count_tokens(part.rstrip(" ")) > self.max_tokens:
                word_parts = re.findall(r"\S+\s*", part)
                current_words = ""
                for word in word_parts:
                    word_candidate = f"{current_words}{word}"
                    if current_words and self.token_counter.count_tokens(
                        word_candidate.rstrip(" ")
                    ) > self.max_tokens:
                        packed.append(current_words)
                        current_words = word
                    else:
                        current_words = word_candidate
                if current_words:
                    packed.append(current_words)
                current = ""
                continue

            current = candidate

        if current:
            packed.append(current)
        return packed
