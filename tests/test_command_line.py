import sys
import os.path
import io
import time
import unittest
import socket
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ping3 import command_line  # noqa: linter (pycodestyle) should not lint this line.
from ping3 import errors  # noqa: linter (pycodestyle) should not lint this line.

DEST_DOMAIN = "example.com"


class test_ping3(unittest.TestCase):
    """command-line ping3 unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dest_addr_0(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main()
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_dest_addr_1(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["127.0.0.1"])
            self.assertIn("127.0.0.1", fake_out.getvalue())

    def test_dest_addr_2(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["127.0.0.1", "8.8.8.8"])
            self.assertIn("127.0.0.1", fake_out.getvalue())
            self.assertIn("8.8.8.8", fake_out.getvalue())

    def test_count(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-c", "1", DEST_DOMAIN])
            self.assertEqual(fake_out.getvalue().count("\n"), 1)

    def test_timeout(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-t", "0.0001", DEST_DOMAIN])
            self.assertRegex(fake_out.getvalue(), r".*Timeout \> [0-9\.]+s.*")

    @unittest.skipIf(sys.platform.startswith("win"), "Linux and macOS Only")
    def test_ttl(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-T", "1", DEST_DOMAIN])
            self.assertRegex(fake_out.getvalue(), r".*Error.*")

    def test_size(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-s", "100", DEST_DOMAIN])
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")
            with self.assertRaises(OSError):
                command_line.main(["-s", "99999", DEST_DOMAIN])

    def test_interval(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            start_time = time.time()
            command_line.main(["-i", "1", DEST_DOMAIN])
            end_time = time.time()
            self.assertTrue((end_time - start_time) >= 3)  # time_expect = (count - 1) * interval
            self.assertNotIn("Timeout", fake_out.getvalue())

    @unittest.skipUnless(sys.platform == "linux", "Linux only")
    def test_interface(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            try:
                route_cmd = os.popen("ip -o -4 route show to default")
                default_route = route_cmd.read()
            finally:
                route_cmd.close()
            my_interface = default_route.split()[4]
            try:
                socket.if_nametoindex(my_interface)  # test if the interface exists.
            except OSError:
                self.fail("Interface Name Error: {}".format(my_interface))
            command_line.main(["-I", my_interface, DEST_DOMAIN])
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_src_addr(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            my_ip = socket.gethostbyname(socket.gethostname())
            if my_ip in ("127.0.0.1", "127.0.1.1"):  # This may caused by /etc/hosts settings.
                dest_addr = my_ip  # only localhost can send and receive from 127.0.0.1 (or 127.0.1.1 on Ubuntu).
            else:
                dest_addr = DEST_DOMAIN
            command_line.main(["-S", my_ip, dest_addr])
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_debug(self):
        with patch("sys.stdout", new=io.StringIO()), patch("sys.stderr", new=io.StringIO()) as fake_err:
            command_line.main(["--debug", "-c", "1", DEST_DOMAIN])
            self.assertIn("[DEBUG]", fake_err.getvalue())

    def test_exceptions(self):
        with self.assertRaises(errors.Timeout):
            command_line.main(["--exceptions", "-t", "0.0001", DEST_DOMAIN])


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
