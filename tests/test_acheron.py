import importlib.util
import pathlib
import unittest


SOURCE = pathlib.Path(__file__).parents[1] / "src" / "acheron.py"
SPEC = importlib.util.spec_from_file_location("acheron", SOURCE)
acheron = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acheron)


class AcheronTests(unittest.TestCase):
    def test_bar_clamps_and_fills(self):
        self.assertEqual(acheron.bar(-5, 4), "[....]")
        self.assertEqual(acheron.bar(50, 4), "[##..]")
        self.assertEqual(acheron.bar(150, 4), "[####]")

    def test_rate_formats_network_speed(self):
        self.assertEqual(acheron.rate(900), "900 B/s")
        self.assertEqual(acheron.rate(1500), "1.5 KB/s")

    def test_mood_is_reassuring(self):
        self.assertIn("Take a breath", acheron.mood(2, 30, 0))
        self.assertIn("breathing room", acheron.mood(20, 95, 0))

    def test_landscape_has_requested_width(self):
        self.assertTrue(all(len(row) == 60 for row in acheron.landscape(60, 30, 45, 8)))


if __name__ == "__main__":
    unittest.main()
