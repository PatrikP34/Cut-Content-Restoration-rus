from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


_LABEL = re.compile(r"\$\$\$(.+?)\$\$\$")


class EpkTool:
    """Use the supplied FSNr_tools executable for EPK decryption and encryption."""

    def __init__(self, executable: str | Path, some_key: str | Path) -> None:
        self.executable = Path(executable)
        self.some_key = Path(some_key)
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self._work: Path | None = None

    def __enter__(self) -> EpkTool:
        if not self.executable.is_file():
            raise FileNotFoundError(f"EPK tool not found: {self.executable}")
        if not self.some_key.is_file():
            raise FileNotFoundError(f"SomeKey.bin not found: {self.some_key}")
        if self.some_key.stat().st_size != 5120:
            raise ValueError("SomeKey.bin must contain exactly 5120 bytes.")

        self._temporary = tempfile.TemporaryDirectory(prefix="fsn-russian-epk-")
        self._work = Path(self._temporary.name)
        shutil.copyfile(self.executable, self._work / "main.exe")
        shutil.copyfile(self.some_key, self._work / "SomeKey.bin")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._temporary is not None:
            self._temporary.cleanup()
        self._temporary = None
        self._work = None

    def _run(self, mode: str, path: Path) -> None:
        if self._work is None:
            raise RuntimeError("EpkTool must be used as a context manager.")
        result = subprocess.run(
            [str(self._work / "main.exe"), mode, str(path)],
            cwd=self._work,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"EPK {mode} failed for {path.name}: {detail}")

    @staticmethod
    def _safe_stem(stem: str) -> str:
        if not stem or not re.fullmatch(r"[A-Za-z0-9_-]+", stem):
            raise ValueError(f"Unsupported EPK filename stem: {stem!r}")
        return stem

    def decrypt(self, encrypted: bytes, stem: str) -> bytes:
        if self._work is None:
            raise RuntimeError("EpkTool must be used as a context manager.")
        stem = self._safe_stem(stem)
        source = self._work / f"{stem}.epk"
        destination = self._work / f"{stem}.epk_dec"
        source.write_bytes(encrypted)
        destination.unlink(missing_ok=True)
        self._run("dec", source)
        if not destination.is_file():
            raise RuntimeError(f"EPK tool did not produce {destination.name}.")
        return destination.read_bytes()

    def encrypt(self, plaintext: bytes, stem: str) -> bytes:
        if self._work is None:
            raise RuntimeError("EpkTool must be used as a context manager.")
        stem = self._safe_stem(stem)
        source = self._work / f"{stem}.epk_dec"
        destination = self._work / f"{stem}.epk_enc"
        source.write_bytes(plaintext)
        destination.unlink(missing_ok=True)
        self._run("enc", source)
        if not destination.is_file():
            raise RuntimeError(f"EPK tool did not produce {destination.name}.")
        encrypted = destination.read_bytes()
        if self.decrypt(encrypted, stem) != plaintext:
            raise RuntimeError(f"EPK round-trip check failed for {stem}.")
        return encrypted


@dataclass(frozen=True)
class _TableRow:
    identifier: str
    label: str | None
    raw: str
    fields: tuple[str, ...]


def _table_rows(
    plaintext: bytes, name: str
) -> tuple[list[str], list[_TableRow], str]:
    try:
        text = plaintext.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{name} is not UTF-8.") from error
    if not text.startswith("DAT\n") or "label=str" not in text[:256]:
        raise ValueError(f"{name} is not a supported DAT message table.")

    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    headers = lines[:2]
    rows: list[_TableRow] = []
    identifiers: set[str] = set()
    has_message_labels = "text=lstr" in headers[1]
    for line in lines[2:]:
        fields = line.split("::")
        if len(fields) < 2:
            if line:
                raise ValueError(f"Malformed DAT row in {name}: {line[:80]!r}")
            continue
        identifier = fields[0]
        if not identifier or identifier in identifiers:
            raise ValueError(f"Empty or duplicate DAT row ID {identifier!r} in {name}.")
        identifiers.add(identifier)
        label = None
        if has_message_labels:
            match = _LABEL.fullmatch(fields[1])
            if not match:
                raise ValueError(f"DAT row has no message label in {name}: {line[:80]!r}")
            label = match.group(1)
        rows.append(_TableRow(identifier, label, line, tuple(fields)))
    return headers, rows, newline


def merge_epk_table(
    baseline_epk: bytes,
    restored_epk: bytes,
    russian_epk: bytes,
    stem: str,
    cipher: EpkTool,
) -> tuple[bytes, int]:
    """Add only restoration-edited rows, keeping every existing Russian translation."""
    baseline_plain = cipher.decrypt(baseline_epk, stem)
    restored_plain = cipher.decrypt(restored_epk, stem)
    russian_plain = cipher.decrypt(russian_epk, stem)

    baseline_headers, baseline_rows, _ = _table_rows(
        baseline_plain, f"{stem} baseline"
    )
    restored_headers, restored_rows, _ = _table_rows(
        restored_plain, f"{stem} restored English"
    )
    headers, russian_rows, newline = _table_rows(
        russian_plain, f"{stem} Russian base"
    )
    if baseline_headers != restored_headers or baseline_headers != headers:
        raise ValueError(f"{stem}: DAT table schemas do not match.")

    if "text=lstr" in headers[1]:
        baseline_by_label = {row.label: row for row in baseline_rows}
        russian_by_label = {row.label: row for row in russian_rows}
        russian_ids = {row.identifier: row.label for row in russian_rows}
        additions: list[_TableRow] = []
        for row in restored_rows:
            previous = baseline_by_label.get(row.label)
            if previous is not None and previous.raw == row.raw:
                continue
            if row.label in russian_by_label:
                continue
            conflicting_label = russian_ids.get(row.identifier)
            if conflicting_label is not None and conflicting_label != row.label:
                raise ValueError(
                    f"{stem}: message ID {row.identifier!r} is already used by "
                    f"{conflicting_label!r}; cannot add {row.label!r} safely."
                )
            additions.append(row)
        if not additions:
            return russian_epk, 0
        output_lines = headers + [row.raw for row in russian_rows]
        output_lines.extend(row.raw for row in additions)
        count = len(additions)
    else:
        baseline_by_id = {row.identifier: row for row in baseline_rows}
        restored_by_id = {row.identifier: row for row in restored_rows}
        russian_by_id = {row.identifier: row for row in russian_rows}
        merged_by_id = dict(russian_by_id)
        additions = []

        for identifier, row in restored_by_id.items():
            previous = baseline_by_id.get(identifier)
            russian_row = russian_by_id.get(identifier)
            if previous is None:
                if russian_row is None:
                    additions.append(row)
                    merged_by_id[identifier] = row
                elif russian_row.raw != row.raw:
                    raise ValueError(
                        f"{stem}: new DAT row ID {identifier!r} conflicts with "
                        "an existing Russian row."
                    )
                continue
            if previous.raw == row.raw:
                continue
            if russian_row is None:
                raise ValueError(
                    f"{stem}: changed DAT row ID {identifier!r} is missing "
                    "from the Russian table."
                )
            if len(previous.fields) != len(row.fields) or len(previous.fields) != len(
                russian_row.fields
            ):
                raise ValueError(
                    f"{stem}: changed DAT row ID {identifier!r} has an "
                    "incompatible field count."
                )

            merged_fields = list(russian_row.fields)
            for index, (base_value, restored_value, russian_value) in enumerate(
                zip(previous.fields, row.fields, russian_row.fields)
            ):
                if restored_value == base_value:
                    continue
                if russian_value not in (base_value, restored_value):
                    raise ValueError(
                        f"{stem}: restoration and Russian edits conflict in "
                        f"DAT row {identifier!r}, field {index}."
                    )
                merged_fields[index] = restored_value
            merged_by_id[identifier] = _TableRow(
                identifier, None, "::".join(merged_fields), tuple(merged_fields)
            )

        for identifier, previous in baseline_by_id.items():
            if identifier in restored_by_id or identifier not in russian_by_id:
                continue
            russian_row = russian_by_id[identifier]
            if russian_row.raw != previous.raw:
                raise ValueError(
                    f"{stem}: restoration removes DAT row {identifier!r}, "
                    "which was also changed in Russian."
                )
            del merged_by_id[identifier]

        if not additions and all(
            merged_by_id.get(row.identifier) == row for row in russian_rows
        ) and len(merged_by_id) == len(russian_rows):
            return russian_epk, 0
        output_rows = [
            merged_by_id[row.identifier]
            for row in russian_rows
            if row.identifier in merged_by_id
        ]
        output_rows.extend(additions)
        output_lines = headers + [row.raw for row in output_rows]
        count = len(additions) + sum(
            merged_by_id.get(row.identifier) != row for row in russian_rows
        )

    plaintext = (newline.join(output_lines) + newline).encode("utf-8")
    return cipher.encrypt(plaintext, stem), count


def epk_stem(entry_name: str) -> str:
    return Path(entry_name).stem
