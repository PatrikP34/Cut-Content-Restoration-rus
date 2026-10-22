from __future__ import annotations

import difflib
from dataclasses import dataclass


class MergeConflict(ValueError):
    """Raised when Russian and restoration edits overlap in the same source lines."""


@dataclass(frozen=True)
class _Edit:
    start: int
    end: int
    replacement: tuple[str, ...]


def _lines(data: bytes, source_name: str) -> tuple[list[str], str, bool, bool]:
    has_bom = data.startswith(b"\xef\xbb\xbf")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"{source_name} is not valid UTF-8.") from error

    newline = "\r\n" if "\r\n" in text else "\n"
    has_trailing_newline = text.endswith(("\n", "\r"))
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.split("\n"), newline, has_trailing_newline, has_bom


def _edits(original: list[str], changed: list[str]) -> list[_Edit]:
    matcher = difflib.SequenceMatcher(None, original, changed, autojunk=False)
    return [
        _Edit(start, end, tuple(changed[changed_start:changed_end]))
        for operation, start, end, changed_start, changed_end in matcher.get_opcodes()
        if operation != "equal"
    ]


def _overlaps(left: _Edit, right: _Edit) -> bool:
    if left.start == right.start and left.end == right.end and left.replacement == right.replacement:
        return False
    if left.start == left.end and right.start == right.end:
        return left.start == right.start
    if left.start == left.end:
        return right.start <= left.start <= right.end
    if right.start == right.end:
        return left.start <= right.start <= left.end
    return max(left.start, right.start) < min(left.end, right.end)


def merge_script(
    baseline: bytes,
    restored_english: bytes,
    russian: bytes,
    script_name: str,
) -> bytes:
    """Apply non-overlapping baseline→English changes to a Russian script."""
    base_lines, _, _, _ = _lines(baseline, f"{script_name} baseline")
    english_lines, _, _, _ = _lines(restored_english, f"{script_name} English patch")
    russian_lines, newline, trailing_newline, has_bom = _lines(russian, f"{script_name} Russian base")

    english_edits = _edits(base_lines, english_lines)
    russian_edits = _edits(base_lines, russian_lines)
    combined = list(english_edits)

    for russian_edit in russian_edits:
        duplicate = False
        for english_edit in english_edits:
            if (
                russian_edit.start == english_edit.start
                and russian_edit.end == english_edit.end
                and russian_edit.replacement == english_edit.replacement
            ):
                duplicate = True
                break
            if _overlaps(russian_edit, english_edit):
                raise MergeConflict(
                    f"{script_name}: English restoration overlaps a Russian edit "
                    f"at baseline lines {max(russian_edit.start, english_edit.start) + 1}-"
                    f"{min(russian_edit.end, english_edit.end)}."
                )
        if not duplicate:
            combined.append(russian_edit)

    combined.sort(key=lambda edit: (edit.start, edit.end))
    output: list[str] = []
    cursor = 0
    for edit in combined:
        if edit.start < cursor:
            raise MergeConflict(f"{script_name}: edits cannot be ordered safely.")
        output.extend(base_lines[cursor:edit.start])
        output.extend(edit.replacement)
        cursor = edit.end
    output.extend(base_lines[cursor:])

    text = newline.join(output)
    if trailing_newline and not text.endswith(newline):
        text += newline
    result = text.encode("utf-8")
    return b"\xef\xbb\xbf" + result if has_bom else result
