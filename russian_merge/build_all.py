from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from .convert_scene import EpkTool, epk_stem, merge_epk_table
from .fpd import FPDArchive, write_archive
from .merge_scene import merge_script


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_russian_archive(
    russian_path: str | Path,
    baseline_path: str | Path,
    restored_english_path: str | Path,
    fpd_key_path: str | Path,
    epk_tool_path: str | Path,
    some_key_path: str | Path,
    output_path: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Build a new Russian-based FPD archive from the English restoration delta."""
    russian_path = Path(russian_path).resolve()
    baseline_path = Path(baseline_path).resolve()
    restored_english_path = Path(restored_english_path).resolve()
    output_path = Path(output_path).resolve()
    inputs = {russian_path, baseline_path, restored_english_path}
    if output_path in inputs:
        raise ValueError("Output must be a new path; source archives are never overwritten.")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output_path} (use --overwrite to replace it)")

    key = Path(fpd_key_path).read_bytes()
    russian = FPDArchive(russian_path, key)
    baseline = FPDArchive(baseline_path, key)
    restored = FPDArchive(restored_english_path, key)

    if baseline.version != restored.version or baseline.version != russian.version:
        raise ValueError("The three FPD archives use different format versions.")

    replacements: dict[str, bytes] = {}
    additions: dict[str, bytes] = {}
    report: dict[str, Any] = {
        "inputs": {
            "russian": str(russian_path),
            "baseline": str(baseline_path),
            "restored_english": str(restored_english_path),
        },
        "counts": Counter(),
        "conflicts": [],
        "fallback_english_rows": [],
    }

    with (
        baseline_path.open("rb") as baseline_file,
        restored_english_path.open("rb") as restored_file,
        russian_path.open("rb") as russian_file,
        EpkTool(epk_tool_path, some_key_path) as cipher,
    ):
        for name in baseline.by_name.keys() & restored.by_name.keys():
            base_entry = baseline.by_name[name]
            restored_entry = restored.by_name[name]
            baseline_bytes = baseline.read(base_entry)
            restored_bytes = restored.read(restored_entry)
            if baseline_bytes == restored_bytes:
                continue

            report["counts"]["changed_baseline_entries"] += 1
            if name.endswith(".ks"):
                russian_entry = russian.by_name.get(name)
                if russian_entry is None:
                    raise ValueError(f"Changed script is missing from the Russian archive: {name}")
                russian_bytes = russian.read(russian_entry)
                replacements[name] = merge_script(
                    baseline_bytes, restored_bytes, russian_bytes, name
                )
                report["counts"]["merged_scripts"] += 1
                continue

            if name.endswith(".epk"):
                russian_entry = russian.by_name.get(name)
                if russian_entry is None:
                    additions[name] = restored_bytes
                    report["counts"]["fallback_english_epks"] += 1
                    continue
                russian_bytes = russian.read(russian_entry)
                merged, row_count = merge_epk_table(
                    baseline_bytes,
                    restored_bytes,
                    russian_bytes,
                    epk_stem(name),
                    cipher,
                )
                if row_count:
                    replacements[name] = merged
                    report["counts"]["merged_epks"] += 1
                    report["counts"]["added_epk_rows"] += row_count
                    if "/locale/us/" in name:
                        report["fallback_english_rows"].append(
                            {"entry": name, "rows": row_count}
                        )
                continue

            raise ValueError(f"Unsupported modified entry type; refusing to skip it: {name}")

        for name in restored.by_name.keys() - baseline.by_name.keys():
            if name in russian.by_name:
                continue
            restored_bytes = restored.read(restored.by_name[name])
            if name.endswith((".ks", ".tl", ".epk")) or name == "root/data/fsn_restore.marker":
                additions[name] = restored_bytes
                report["counts"]["added_entries"] += 1
                if name.endswith(".ks"):
                    report["counts"]["added_scripts"] += 1
                elif name.endswith(".tl"):
                    report["counts"]["added_tl_files"] += 1
                elif name.endswith(".epk"):
                    report["counts"]["added_epks"] += 1
                continue
            raise ValueError(f"Unsupported new entry type; refusing to skip it: {name}")

    # Keep the merge output alongside the destination, and publish only after
    # the complete archive has passed its structural and content checks.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, staging_name = tempfile.mkstemp(
        dir=output_path.parent, prefix=output_path.name + ".", suffix=".verify.tmp"
    )
    os.close(fd)
    os.remove(staging_name)
    try:
        write_archive(russian, staging_name, replacements, additions)
        merged_archive = FPDArchive(staging_name, key)
        expected_names = russian.by_name.keys() | additions.keys()
        if merged_archive.by_name.keys() != expected_names:
            raise ValueError("Output verification failed: Russian archive entries were lost or added unexpectedly.")

        for name, expected in replacements.items():
            if merged_archive.read(merged_archive.by_name[name]) != expected:
                raise ValueError(f"Output verification failed for merged entry {name!r}.")
        for name, expected in additions.items():
            if merged_archive.read(merged_archive.by_name[name]) != expected:
                raise ValueError(f"Output verification failed for added entry {name!r}.")
        with russian_path.open("rb") as source_file, Path(staging_name).open("rb") as output_file:
            for name, source_entry in russian.by_name.items():
                if name in replacements:
                    continue
                output_entry = merged_archive.by_name[name]
                source_file.seek(56 + russian.block_size + source_entry.offset)
                output_file.seek(56 + merged_archive.block_size + output_entry.offset)
                remaining = source_entry.size
                while remaining:
                    size = min(remaining, 1 << 20)
                    if source_file.read(size) != output_file.read(size):
                        raise ValueError(f"Output verification failed: Russian payload changed for {name!r}.")
                    remaining -= size

        os.replace(staging_name, output_path)
    finally:
        if os.path.exists(staging_name):
            os.remove(staging_name)

    output_hash = hashlib.sha256()
    with output_path.open("rb") as output_file:
        for chunk in iter(lambda: output_file.read(1 << 20), b""):
            output_hash.update(chunk)
    report["output"] = str(output_path)
    report["output_sha256"] = output_hash.hexdigest()
    report["counts"] = dict(report["counts"])
    report["fallback_english_rows_count"] = sum(
        item["rows"] for item in report["fallback_english_rows"]
    )
    return report


def main() -> None:
    import argparse

    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Merge the English restoration delta onto a Russian FPD base."
    )
    parser.add_argument(
        "--russian", default=project_root / "rus/obb/patch00m.bin"
    )
    parser.add_argument(
        "--baseline",
        default=project_root / "FSNRestoration_unpacked/backup-obb/patch00m.bin",
    )
    parser.add_argument(
        "--restored-english",
        default=project_root / "FSNRestoration_unpacked/cache/patch00m.en.bin",
    )
    parser.add_argument(
        "--fpd-key",
        default=project_root / "FSNRestoration_unpacked/keys/decryptKey.bin",
    )
    parser.add_argument(
        "--some-key", default=project_root / "FSNRestoration_unpacked/keys/SomeKey.bin"
    )
    parser.add_argument("--epk-tool", default=project_root / "fsnr/build/main.exe")
    parser.add_argument(
        "--output",
        default=project_root / "FSNRestoration_unpacked/cache/patch00m.ru.bin",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    result = build_russian_archive(
        args.russian,
        args.baseline,
        args.restored_english,
        args.fpd_key,
        args.epk_tool,
        args.some_key,
        args.output,
        overwrite=args.overwrite,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
