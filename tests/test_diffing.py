from __future__ import annotations

import unittest

from vicorrect.diffing import ChangeType, DiffEngine


class DiffEngineTests(unittest.TestCase):
    def test_build_changes_detects_replacements(self) -> None:
        changes = DiffEngine().build_changes("toi dang hoc", "tôi đang học")
        meaningful = [change for change in changes if change.change_type != ChangeType.EQUAL]

        self.assertEqual(len(meaningful), 3)
        self.assertEqual(meaningful[0].change_type, ChangeType.REPLACED)
        self.assertEqual(meaningful[0].original, "toi")
        self.assertEqual(meaningful[0].corrected, "tôi")
        self.assertEqual(meaningful[1].change_type, ChangeType.REPLACED)
        self.assertEqual(meaningful[2].change_type, ChangeType.REPLACED)

    def test_build_changes_detects_insert_and_delete(self) -> None:
        removed_changes = DiffEngine().build_changes("xin chao ban", "xin chao")
        inserted_changes = DiffEngine().build_changes("xin", "xin chao")
        replaced_changes = DiffEngine().build_changes("xin chao ban", "xin chào")

        self.assertTrue(any(change.change_type == ChangeType.REMOVED for change in removed_changes))
        self.assertTrue(any(change.change_type == ChangeType.ADDED for change in inserted_changes))
        self.assertTrue(any(change.change_type == ChangeType.REPLACED for change in replaced_changes))

    def test_render_html_contains_color_classes(self) -> None:
        html = DiffEngine().render_html("toi dang hoc", "tôi đang học")

        self.assertIn("class='removed'", html)
        self.assertIn("class='replaced'", html)


if __name__ == "__main__":
    unittest.main()
