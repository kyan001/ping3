import sys
import os.path
import io
import unittest
from unittest.mock import patch
import socket

sys.path.insert(0, os.path.dirname(sys.path[0]))
import ping3


class test_ping3(unittest.TestCase):
    """ping3 unittest"""
    __version__ = '1.2.1'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertEqual(self.__version__, ping3.__version__)

    def test_ping_normal(self):
        delay = ping3.ping('example.com')
        self.assertIsInstance(delay, float)

    def test_ping_timeout(self):
        delay = ping3.ping('example.com', timeout=0.0001)
        self.assertIsNone(delay)

    def test_ping_unit(self):
        delay = ping3.ping('example.com', unit="ms")
        self.assertIsInstance(delay, float)
        self.assertTrue(delay > 1)

    def test_ping_bind(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        delay = ping3.ping('example.com', src_addr=my_ip)
        self.assertIsInstance(delay, float)

    def test_verbose_ping_normal(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            ping3.verbose_ping('example.com')
            self.assertRegex(fake_out.getvalue(), r'.*[0-9]+ms.*')

    def test_verbose_ping_timeout(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            ping3.verbose_ping('example.com', timeout=0.0001)
            self.assertRegex(fake_out.getvalue(), r'.*Timeout \> [0-9\.]+s.*')

    def test_verbose_ping_count(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            ping3.verbose_ping('example.com', count=1)
            self.assertRegex(fake_out.getvalue(), r'.*[0-9]+ms.*')

    def test_verbose_ping_bind(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            my_ip = socket.gethostbyname(socket.gethostname())
            ping3.verbose_ping('example.com', src_addr=my_ip)
            self.assertRegex(fake_out.getvalue(), r'.*[0-9]+ms.*')


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
