import sys
import os.path
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ping3 import command_line  # noqa: linter (pycodestyle) should not lint this line.


class test_cli_validation(unittest.TestCase):
    """command-line argument validation unittest (no network needed)"""

    def test_negative_count_rejected(self):
        with self.assertRaises(SystemExit) as cm:
            command_line.main(["-c=-1", "127.0.0.1"])
        self.assertEqual(cm.exception.code, 2)

    def test_zero_count_still_allowed(self):
        # count=0 means infinite loop; validation must not reject it here,
        # so patch verbose_ping to avoid looping forever.
        from unittest.mock import patch
        with patch("ping3.command_line.ping3.verbose_ping") as mock_vp:
            command_line.main(["-c=0", "127.0.0.1"])
            mock_vp.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
