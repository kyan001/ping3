import sys
import os.path
import io
import unittest
import time
from unittest.mock import patch
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ping3  # noqa: linter (pycodestyle) should not lint this line.


class test_ping3(unittest.TestCase):
    """ping3 unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertIsInstance(ping3.__version__, str)

    def test_ping_normal(self):
        delay = ping3.ping("dns.google")
        self.assertIsInstance(delay, float)

    def test_verbose_ping_normal(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google")
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_ping_timeout(self):
        delay = ping3.ping("dns.google", timeout=0.0001)
        self.assertIsNone(delay)

    def test_ping_timeout_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            with self.assertRaises(ping3.errors.Timeout):
                ping3.ping("dns.google", timeout=0.0001)

    def test_verbose_ping_timeout(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google", timeout=0.0001)
            self.assertRegex(fake_out.getvalue(), r".*Timeout \> [0-9\.]+s.*")

    def test_verbose_ping_timeout_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            with self.assertRaises(ping3.errors.Timeout):
                ping3.verbose_ping("dns.google", timeout=0.0001)

    def test_ping_error(self):
        delay = ping3.ping("not.exist.com")
        self.assertFalse(delay)

    def test_ping_error_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            try:
                ping3.ping("not.exist.com")
            except ping3.errors.HostUnknown as e:
                self.assertEqual(e.dest_addr, "not.exist.com")

    def test_ping_seq(self):
        delay = ping3.ping("dns.google", seq=199)
        self.assertIsInstance(delay, float)

    def test_ping_size(self):
        delay = ping3.ping("dns.google", size=100)
        self.assertIsInstance(delay, float)

    def test_ping_size_exception(self):
        with self.assertRaises(OSError):
            ping3.ping("dns.google", size=99999)  # most router has 1480 MTU, which is IP_Header(20) + ICMP_Header(8) + ICMP_Payload(1452)

    def test_verbose_ping_size(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google", size=100)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_verbose_ping_size_exception(self):
        with self.assertRaises(OSError):
            ping3.verbose_ping("dns.google", size=99999)

    def test_ping_unit(self):
        delay = ping3.ping("dns.google", unit="ms")
        self.assertIsInstance(delay, float)
        self.assertTrue(delay > 1)

    def test_verbose_ping_unit(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google", unit="ms")
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    @unittest.skipUnless(sys.platform == "linux", "Linux only")
    def test_ping_interface(self):
        if os.geteuid() != 0:
            print("Needs sudo, will cause an error.", end="")
            self.fail("Needs sudo.")

            
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
        dest_addr = "dns.google"
        delay = ping3.ping(dest_addr, interface=my_interface)
        self.assertIsInstance(delay, float)

    @unittest.skipUnless(sys.platform == "linux", "Linux only")
    def test_verbose_ping_interface(self):
        if os.geteuid() != 0:
            print("Needs sudo, will cause an error.", end="")
            self.fail("Needs sudo.")
            
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
            dest_addr = "dns.google"
            ping3.verbose_ping(dest_addr, interface=my_interface)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    def test_ping_src_addr(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        if my_ip in ("127.0.0.1", "127.0.1.1"):  # This may caused by /etc/hosts settings.
            dest_addr = my_ip  # only localhost can send and receive from 127.0.0.1 (or 127.0.1.1 on Ubuntu).
        else:
            dest_addr = "dns.google"
        delay = ping3.ping(dest_addr, src_addr=my_ip)
        self.assertIsInstance(delay, float)

    def test_verbose_ping_src_addr(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            my_ip = socket.gethostbyname(socket.gethostname())
            if my_ip in ("127.0.0.1", "127.0.1.1"):  # This may caused by /etc/hosts settings.
                dest_addr = my_ip  # only localhost can send and receive from 127.0.0.1 (or 127.0.1.1 on Ubuntu).
            else:
                dest_addr = "dns.google"
            ping3.verbose_ping(dest_addr, src_addr=my_ip)
            self.assertRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    @unittest.skipIf(sys.platform.startswith("win"), "Linux and macOS Only")
    def test_ping_ttl(self):
        delay = ping3.ping("dns.google", ttl=1)
        self.assertIn(delay, (None, False))  # When TTL expired, some routers report nothing.

    @unittest.skipIf(sys.platform.startswith("win"), "Linux and macOS Only")
    def test_ping_ttl_exception(self):
        with patch("ping3.EXCEPTIONS", True):
            with self.assertRaises((ping3.errors.TimeToLiveExpired, ping3.errors.Timeout)):  # When TTL expired, some routers report nothing.
                ping3.ping("dns.google", ttl=1)

    @unittest.skipIf(sys.platform.startswith("win"), "Linux and macOS Only")
    def test_verbose_ping_ttl(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google", ttl=1)
            self.assertNotRegex(fake_out.getvalue(), r".*[0-9]+ms.*")

    @unittest.skipIf(sys.platform.startswith("win"), "Linux and macOS Only")
    def test_verbose_ping_ttl_exception(self):
        with patch("sys.stdout", new=io.StringIO()), patch("ping3.EXCEPTIONS", True):
            with self.assertRaises((ping3.errors.TimeToLiveExpired, ping3.errors.Timeout)):  # When TTL expired, some routers report nothing.
                ping3.verbose_ping("dns.google", ttl=1)

    def test_verbose_ping_count(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            ping3.verbose_ping("dns.google", count=1)
            self.assertEqual(fake_out.getvalue().count("\n"), 1)

    def test_verbose_ping_interval(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            delay = ping3.ping("dns.google")
            self.assertTrue(0 < delay < 0.75)  # If interval does not work, the total delay should be < 3s (4 * 0.75s)
            start_time = time.time()
            ping3.verbose_ping("dns.google", interval=1)  # If interval does work, the total delay should be > 3s (3 * 1s)
            end_time = time.time()
            self.assertTrue((end_time - start_time) >= 3)  # time_expect = (count - 1) * interval
            self.assertNotIn("Timeout", fake_out.getvalue())  # Ensure no timeout

    def test_DEBUG(self):
        with patch("ping3.DEBUG", True), patch("sys.stderr", new=io.StringIO()):
            delay = ping3.ping("dns.google")
            self.assertIsNotNone(ping3.LOGGER)

    def test_EXTENDED(self):
        with patch("ping3.EXTENDED", True), patch("sys.stderr", new=io.StringIO()):
            obj = ping3.ping("dns.google")
            self.assertIsInstance(obj, ping3.myData, "Wrong type returned")

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
