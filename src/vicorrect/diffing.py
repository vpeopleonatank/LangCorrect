from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from html import escape
import difflib
import re


class ChangeType(str, Enum):
    EQUAL = "equal"
    ADDED = "added"
    REMOVED = "removed"
    REPLACED = "replaced"


@dataclass(frozen=True)
class DiffChange:
    change_type: ChangeType
    original: str
    corrected: str


class DiffEngine:
    """Build word-level changes and render a lightweight HTML diff."""

    _TOKEN_PATTERN = re.compile(r"\s+|\S+")

    def build_changes(self, original: str, corrected: str) -> list[DiffChange]:
        original_tokens = self._TOKEN_PATTERN.findall(original)
        corrected_tokens = self._TOKEN_PATTERN.findall(corrected)
        matcher = difflib.SequenceMatcher(a=original_tokens, b=corrected_tokens)
        changes: list[DiffChange] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            original_text = "".join(original_tokens[i1:i2])
            corrected_text = "".join(corrected_tokens[j1:j2])
            if tag == "equal":
                changes.append(
                    DiffChange(
                        change_type=ChangeType.EQUAL,
                        original=original_text,
                        corrected=corrected_text,
                    )
                )
            elif tag == "insert":
                changes.append(
                    DiffChange(
                        change_type=ChangeType.ADDED,
                        original="",
                        corrected=corrected_text,
                    )
                )
            elif tag == "delete":
                changes.append(
                    DiffChange(
                        change_type=ChangeType.REMOVED,
                        original=original_text,
                        corrected="",
                    )
                )
            else:
                changes.append(
                    DiffChange(
                        change_type=ChangeType.REPLACED,
                        original=original_text,
                        corrected=corrected_text,
                    )
                )

        return changes

    def render_html(self, original: str, corrected: str) -> str:
        parts = [
            "<html><head><style>",
            "body{font-family:'Segoe UI',sans-serif;font-size:14px;line-height:1.6;color:#0f172a;}",
            ".added{background:#dcfce7;color:#166534;border-radius:4px;padding:1px 2px;}",
            ".removed{background:#fee2e2;color:#991b1b;border-radius:4px;padding:1px 2px;text-decoration:line-through;}",
            ".replaced{background:#fef3c7;color:#92400e;border-radius:4px;padding:1px 2px;}",
            ".legend{margin-bottom:12px;color:#334155;}",
            ".block{white-space:pre-wrap;}",
            "</style></head><body>",
            "<div class='legend'>Xanh: thêm mới. Đỏ: xóa. Vàng: thay thế.</div>",
            "<div class='block'>",
        ]

        for change in self.build_changes(original, corrected):
            if change.change_type == ChangeType.EQUAL:
                parts.append(escape(change.corrected))
            elif change.change_type == ChangeType.ADDED:
                parts.append(f"<span class='added'>{escape(change.corrected)}</span>")
            elif change.change_type == ChangeType.REMOVED:
                parts.append(f"<span class='removed'>{escape(change.original)}</span>")
            else:
                parts.append(f"<span class='removed'>{escape(change.original)}</span>")
                parts.append(f"<span class='replaced'>{escape(change.corrected)}</span>")

        parts.append("</div></body></html>")
        return "".join(parts)
