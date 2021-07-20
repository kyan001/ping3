import sys
import os.path
import io
import time
import unittest
import socket
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ping3 import _main as command_line_ping3  # noqa: linter (pycodestyle) should not lint this line.
from ping3 import errors  # noqa: linter (pycodestyle) should not lint this line.


class test_ping3(unittest.TestCase):
    """command-line ping3 unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dest_addr_0(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main()
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_dest_addr_1(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(["127.0.0.1"])
            self.assertTrue("127.0.0.1" in fake_out.getvalue())

    def test_dest_addr_2(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(["127.0.0.1", "8.8.8.8"])
            self.assertTrue("127.0.0.1" in fake_out.getvalue())
            self.assertTrue("8.8.8.8" in fake_out.getvalue())

    def test_count(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(['-c', '1', 'example.com'])
            self.assertEqual(fake_out.getvalue().count("\n"), 1)

    def test_timeout(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(['-w', '0.0001', 'example.com'])
            self.assertRegex(fake_out.getvalue(), r".*Timeout \> [0-9\.]+s.*")

    def test_ttl(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(['-t', '1', 'example.com'])
            self.assertRegex(fake_out.getvalue(), r".*Timeout.*")

    def test_size(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line_ping3.main(['-l', '100', 'example.com'])
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")
            with self.assertRaises(OSError):
                command_line_ping3.main(['-l', '99999', 'example.com'])

    def test_interval(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            start_time = time.time()
            command_line_ping3.main(['-i', '1.7', 'example.com'])
            end_time = time.time()
            self.assertTrue((end_time - start_time) >= 5.1)  # time_expect = (count - 1) * interval
            self.assertFalse('Timeout' in fake_out.getvalue())

    @unittest.skipUnless(sys.platform == 'linux', "Linux only")
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
                self.fail('Interface Name Error: {}'.format(my_interface))
            command_line_ping3.main(['-I', my_interface, 'example.com'])
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_debug(self):
        with patch("sys.stdout", new=io.StringIO()), patch("sys.stderr", new=io.StringIO()) as fake_err:
            command_line_ping3.main(['--debug', '-c', '1', 'example.com'])
            self.assertIn("[DEBUG]", fake_err.getvalue())

    def test_exceptions(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            with self.assertRaises(errors.Timeout):
                command_line_ping3.main(['--exceptions', '-w', '0.0001', 'example.com'])


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
