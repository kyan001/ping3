import sys
import os.path
import io
import unittest
import time
from unittest.mock import patch
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ping3  # noqa: linter (pycodestyle) should not lint this line.
from ping3 import errors  # noqa: linter (pycodestyle) should not lint this line.


class test_ping3(unittest.TestCase):
    """ping3 unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertTrue(isinstance(ping3.__version__, str))

    def test_ping_normal(self):
        delay = ping3.ping("example.com")
        self.assertIsInstance(delay, float)

    def test_verbose_ping_normal(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com")
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_ping_timeout(self):
        delay = ping3.ping("example.com", timeout=0.0001)
        self.assertIsNone(delay)

    def test_ping_timeout_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            with self.assertRaises(errors.Timeout):
                ping3.ping("example.com", timeout=0.0001)

    def test_verbose_ping_timeout(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", timeout=0.0001)
            self.assertRegex(fake_out.getvalue(), r".*Timeout \> [0-9\.]+s.*")

    def test_verbose_ping_timeout_exception(self):
        with patch("sys.stdout", new=io.StringIO()):
            with patch("ping3.EXCEPTIONS", True):
                with self.assertRaises(errors.Timeout):
                    ping3.verbose_ping("example.com", timeout=0.0001)

    def test_ping_seq(self):
        delay = ping3.ping("example.com", seq=199)
        self.assertIsInstance(delay, float)

    def test_ping_size(self):
        delay = ping3.ping("example.com", size=100)
        self.assertIsInstance(delay, float)
        with self.assertRaises(OSError):
            ping3.ping("example.com", size=99999)  # most router has 1480 MTU, which is IP_Header(20) + ICMP_Header(8) + ICMP_Payload(1452)

    def test_verbose_ping_size(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", size=100)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")
            with self.assertRaises(OSError):
                ping3.ping("example.com", size=99999)

    def test_ping_unit(self):
        delay = ping3.ping("example.com", unit="ms")
        self.assertIsInstance(delay, float)
        self.assertTrue(delay > 1)

    def test_verbose_ping_unit(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", unit="ms")
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    @unittest.skipUnless(sys.platform == 'linux', "Linux only")
    def test_ping_interface(self):
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
        dest_addr = "example.com"
        delay = ping3.ping(dest_addr, interface=my_interface)
        self.assertIsInstance(delay, float)

    @unittest.skipUnless(sys.platform == 'linux', "Linux only")
    def test_verbose_ping_interface(self):
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
            dest_addr = "example.com"
            ping3.verbose_ping(dest_addr, interface=my_interface)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_ping_bind(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        dest_addr = "example.com"
        if my_ip == "127.0.0.1" or my_ip == "127.0.1.1":  # This may caused by /etc/hosts settings.
            dest_addr = my_ip  # only localhost can send and receive from 127.0.0.1 (or 127.0.1.1 on Ubuntu).
        delay = ping3.ping(dest_addr, src_addr=my_ip)
        self.assertIsInstance(delay, float)

    def test_verbose_ping_bind(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            my_ip = socket.gethostbyname(socket.gethostname())
            dest_addr = "example.com"
            if my_ip == "127.0.0.1" or my_ip == "127.0.1.1":  # This may caused by /etc/hosts settings.
                dest_addr = my_ip  # only localhost can send and receive from 127.0.0.1 (or 127.0.1.1 on Ubuntu).
            ping3.verbose_ping(dest_addr, src_addr=my_ip)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_ping_ttl(self):
        delay = ping3.ping("example.com", ttl=1)
        self.assertIsNone(delay)

    def test_ping_ttl_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            with self.assertRaises((errors.TimeToLiveExpired, errors.Timeout)):  # When TTL expired, some routers report nothing.
                ping3.ping("example.com", ttl=1)

    def test_verbose_ping_ttl(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", ttl=1)
            self.assertRegex(fake_out.getvalue(), r".*Timeout.*")

    def test_verbose_ping_ttl_exception(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", ttl=1)
            self.assertRegex(fake_out.getvalue(), r".*Timeout.*")

    def test_verbose_ping_count(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("example.com", count=1)
            self.assertEqual(fake_out.getvalue().count("\n"), 1)

    def test_verbose_ping_interval(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            start_time = time.time()
            ping3.verbose_ping("example.com", interval=1.7)
            end_time = time.time()
            self.assertTrue((end_time - start_time) >= 5.1)  # time_expect = (count - 1) * interval
            self.assertFalse('Timeout' in fake_out.getvalue())

    def test_ping_hostunknown(self):
        not_exist_url = "not-exist.com"
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            self.assertFalse(ping3.ping(not_exist_url))

    def test_ping_hostunknown_exception(self):
        with patch("sys.stdout", new=io.StringIO()):
            with patch("ping3.EXCEPTIONS", True):
                with self.assertRaises(errors.HostUnknown):
                    ping3.ping("not-exist.com")

    def test_DEBUG(self):
        with patch("ping3.DEBUG", True), patch("sys.stderr", new=io.StringIO()):
            delay = ping3.ping("example.com")
            self.assertIsNotNone(ping3.LOGGER)


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
