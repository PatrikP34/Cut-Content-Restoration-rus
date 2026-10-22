from __future__ import annotations

import os
import struct
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Mapping


HEADER_SIZE = 56


def xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("The FPD encryption key is empty.")
    repetitions = (len(data) + len(key) - 1) // len(key)
    stream = (key * repetitions)[:len(data)]
    return (int.from_bytes(data, "little") ^ int.from_bytes(stream, "little")).to_bytes(
        len(data), "little"
    )


@dataclass(frozen=True)
class Entry:
    name: str
    offset: int
    size: int
    uncompressed_size: int


class FPDArchive:
    def __init__(self, path: str | Path, key: bytes) -> None:
        self.path = Path(path)
        self.key = key
        self._file_size = self.path.stat().st_size
        with self.path.open("rb") as source:
            header = source.read(HEADER_SIZE)
            if len(header) != HEADER_SIZE or header[:4] != b"FPD\x00":
                raise ValueError(f"Not a valid FPD archive: {self.path}")

            self.version = int.from_bytes(header[4:8], "big")
            count = int.from_bytes(header[8:16], "big")
            self.block_size = int.from_bytes(header[16:24], "big") - HEADER_SIZE
            if count < 0 or self.block_size < count * 32:
                raise ValueError(f"Invalid FPD directory dimensions: {self.path}")
            if HEADER_SIZE + self.block_size > self._file_size:
                raise ValueError(f"Truncated FPD directory: {self.path}")

            encrypted_block = source.read(self.block_size)
            if len(encrypted_block) != self.block_size:
                raise ValueError(f"Truncated FPD directory: {self.path}")
            block = xor_bytes(encrypted_block, key)
            name_table = zlib.decompress(block[count * 32:])

            entries: list[Entry] = []
            names: set[str] = set()
            payload_size = self._file_size - HEADER_SIZE - self.block_size
            for index in range(count):
                name_offset, offset, size, uncompressed_size = struct.unpack_from(
                    ">QQQQ", block, index * 32
                )
                if name_offset >= len(name_table):
                    raise ValueError(f"Invalid path offset in FPD entry {index}.")
                end = name_table.find(b"\x00", name_offset)
                if end < 0:
                    raise ValueError(f"Unterminated path in FPD entry {index}.")
                name = name_table[name_offset:end].decode("utf-8")
                if not name or name in names:
                    raise ValueError(f"Empty or duplicate FPD entry name: {name!r}")
                if offset + size > payload_size:
                    raise ValueError(f"Invalid payload bounds for FPD entry {name!r}.")
                names.add(name)
                entries.append(Entry(name, offset, size, uncompressed_size))

        self.entries = entries
        self.by_name = {entry.name: entry for entry in entries}

    def read_stored(self, entry: Entry) -> bytes:
        with self.path.open("rb") as source:
            source.seek(HEADER_SIZE + self.block_size + entry.offset)
            data = source.read(entry.size)
        if len(data) != entry.size:
            raise ValueError(f"Truncated payload for FPD entry {entry.name!r}.")
        return data

    def read(self, entry: Entry) -> bytes:
        data = xor_bytes(self.read_stored(entry), self.key)
        return zlib.decompress(data) if entry.uncompressed_size else data


def _write_all(
    source_archive: FPDArchive,
    destination: str | Path,
    replacements: Mapping[str, bytes],
    additions: Mapping[str, bytes],
    compress_new: bool = True,
) -> int:
    replacements = dict(replacements)
    additions = dict(additions)
    old = source_archive.by_name
    missing = replacements.keys() - old.keys()
    clashes = additions.keys() & old.keys()
    if missing:
        raise ValueError(f"Replacement entries are absent from the Russian archive: {sorted(missing)[:5]}")
    if clashes:
        raise ValueError(f"New entries already exist in the Russian archive: {sorted(clashes)[:5]}")

    names = sorted(old.keys() | additions.keys())
    table_rows: list[tuple[int, int, int, int]] = []
    names_blob = bytearray()
    payload_sizes: list[int] = []
    encoded_payloads: dict[str, bytes] = {}
    payload_offset = 0

    for name in names:
        is_new = name in additions
        if is_new or name in replacements:
            plain = additions[name] if is_new else replacements[name]
            was_compressed = compress_new if is_new else bool(old[name].uncompressed_size)
            encoded = xor_bytes(
                zlib.compress(plain, 6) if was_compressed else plain,
                source_archive.key,
            )
            encoded_payloads[name] = encoded
            size = len(encoded)
            uncompressed_size = len(plain) if was_compressed else 0
        else:
            entry = old[name]
            size = entry.size
            uncompressed_size = entry.uncompressed_size

        table_rows.append((len(names_blob), payload_offset, size, uncompressed_size))
        names_blob.extend(name.encode("utf-8"))
        names_blob.append(0)
        payload_sizes.append(size)
        payload_offset += size

    raw_table = b"".join(struct.pack(">QQQQ", *row) for row in table_rows)
    encrypted_block = xor_bytes(raw_table + zlib.compress(bytes(names_blob), 6), source_archive.key)
    header = (
        b"FPD\x00"
        + source_archive.version.to_bytes(4, "big")
        + len(names).to_bytes(8, "big")
        + (HEADER_SIZE + len(encrypted_block)).to_bytes(8, "big")
        + bytes(32)
    )

    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        dir=target.parent, prefix=target.name + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as output, source_archive.path.open("rb") as source:
            output.write(header)
            output.write(encrypted_block)
            for name in names:
                encoded = encoded_payloads.get(name)
                if encoded is not None:
                    output.write(encoded)
                else:
                    entry = old[name]
                    source.seek(HEADER_SIZE + source_archive.block_size + entry.offset)
                    remaining = entry.size
                    while remaining:
                        chunk = source.read(min(remaining, 1 << 20))
                        if not chunk:
                            raise ValueError(f"Truncated payload for FPD entry {name!r}.")
                        output.write(chunk)
                        remaining -= len(chunk)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, target)
    finally:
        if os.path.exists(temporary_name):
            os.remove(temporary_name)

    return len(names)


def write_archive(
    source_archive: FPDArchive,
    destination: str | Path,
    replacements: Mapping[str, bytes],
    additions: Mapping[str, bytes],
    compress_new: bool = True,
) -> int:
    return _write_all(source_archive, destination, replacements, additions, compress_new)
