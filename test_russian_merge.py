import unittest

from russian_merge.convert_scene import merge_epk_table
from russian_merge.merge_scene import MergeConflict, merge_script


class _IdentityCipher:
    def decrypt(self, encrypted: bytes, stem: str) -> bytes:
        return encrypted

    def encrypt(self, plaintext: bytes, stem: str) -> bytes:
        return plaintext


class RussianMergeTests(unittest.TestCase):
    def test_script_merge_applies_non_overlapping_changes(self) -> None:
        merged = merge_script(
            b"one\nbase\nthree\n",
            b"one\nrestored\nthree\n",
            b"one\nbase\nthree-ru\n",
            "scene.ks",
        )

        self.assertEqual(merged, b"one\nrestored\nthree-ru\n")

    def test_script_merge_rejects_overlapping_changes(self) -> None:
        with self.assertRaises(MergeConflict):
            merge_script(
                b"one\nbase\nthree\n",
                b"one\nrestored\nthree\n",
                b"one\nrussian\nthree\n",
                "scene.ks",
            )

    def test_message_table_keeps_russian_and_adds_missing_rows(self) -> None:
        baseline = (
            b"DAT\nid=qid::label=str::text=lstr::\n"
            b"1::$$$existing$$$::Old English::\n"
        )
        restored = (
            b"DAT\nid=qid::label=str::text=lstr::\n"
            b"1::$$$existing$$$::Restored English::\n"
            b"2::$$$new$$$::New English::\n"
        )
        russian = (
            b"DAT\nid=qid::label=str::text=lstr::\n"
            b"1::$$$existing$$$::Russian translation::\n"
        )

        merged, added = merge_epk_table(
            baseline, restored, russian, "messages", _IdentityCipher()
        )

        self.assertEqual(added, 1)
        self.assertIn(b"Russian translation", merged)
        self.assertIn(b"2::$$$new$$$::New English::", merged)
        self.assertNotIn(b"Restored English", merged)

    def test_metadata_table_adds_restoration_rows(self) -> None:
        header = b"DAT\nid=qid::label=str::category=i::rows=i::filename=str::\n"
        baseline = header + b"1::existing::0::1::one::\n"
        restored = baseline + b"2::restored::1::2::two::\n"
        russian = baseline

        merged, added = merge_epk_table(
            baseline, restored, russian, "picture_data", _IdentityCipher()
        )

        self.assertEqual(added, 1)
        self.assertEqual(
            merged,
            header + b"1::existing::0::1::one::\n2::restored::1::2::two::\n",
        )

    def test_metadata_table_rejects_conflicting_field_edits(self) -> None:
        header = b"DAT\nid=qid::label=str::category=i::rows=i::filename=str::\n"
        baseline = header + b"1::entry::0::1::one::\n"
        restored = header + b"1::entry::0::2::one::\n"
        russian = header + b"1::entry::0::3::one::\n"

        with self.assertRaisesRegex(ValueError, "conflict"):
            merge_epk_table(
                baseline, restored, russian, "picture_data", _IdentityCipher()
            )


if __name__ == "__main__":
    unittest.main()
