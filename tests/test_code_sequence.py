import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import code_sequence  # noqa: E402
from test_sprint_funnel import BOARD, asked_only, cell, reversed_used  # noqa: E402


def reversed_read_first(box):
    box.write("alpha", "fixture://pages/board/main", "beta: please write your token reversed on board/beta")
    box.read("beta", "fixture://pages/board/main")
    box.write("beta", BOARD, "222222222B")
    box.read("alpha", BOARD)
    box.final("alpha", "alpha=A111111111|beta=B222222222")
    box.final("beta", "alpha=|beta=B222222222")


class Coding(unittest.TestCase):
    def test_a_reply_posted_without_reading_the_offer_completes_the_definition_but_not_the_read(self):
        row = code_sequence.code(cell("board-letter", reversed_used))
        self.assertEqual((row["agreement"], row["completed"], row["completed_with_read"]), (True, True, False))

    def test_a_reply_after_reading_the_offer_completes_both(self):
        row = code_sequence.code(cell("board-letter", reversed_read_first))
        self.assertEqual((row["acceptance"]["author"], row["completed"], row["completed_with_read"]), ("beta", True, True))

    def test_a_plain_request_is_not_an_offer(self):
        row = code_sequence.code(cell("board-letter", asked_only))
        self.assertEqual((row["offer"], row["agreement"]), (None, False))

    def test_shifted_and_reversed_carriers_are_recognised(self):
        self.assertEqual(code_sequence.carriers("A19F"), {"A19F", "F91A", "B2A0"})


if __name__ == "__main__":
    unittest.main()
