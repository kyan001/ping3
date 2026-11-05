"""Exercise the public ping path with ICMP packets over local socket pairs."""

import contextlib
import io
import os
import socket
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ping3


class EchoSocket:
    """Deliver serialized ICMP replies without requiring raw-socket privileges."""

    def __init__(self, family, sock_type, response="echo"):
        self.family = family
        self.type = sock_type
        self.proto = socket.IPPROTO_ICMP if family == socket.AF_INET else socket.IPPROTO_ICMPV6
        self.reader, self.writer = socket.socketpair(type=socket.SOCK_DGRAM)
        self.sent = []
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.reader.close()
        self.writer.close()

    def fileno(self):
        return self.reader.fileno()

    def recvfrom(self, size):
        return self.reader.recv(size), ("127.0.0.1", 0)

    def sendto(self, packet, address):
        self.sent.append(packet)
        header = ping3.read_icmp_header(packet[:8])
        icmp_type = ping3.IcmpV4Type if self.family == socket.AF_INET else ping3.IcmpV6Type
        # A different probe's reply must still be ignored after wrapping.
        wrong_seq = (header["seq"] + 1) % 65536
        for seq in (wrong_seq, header["seq"]):
            reply = struct.pack(ping3.ICMP_HEADER_FORMAT, icmp_type.ECHO_REPLY, 0, 0, header["id"], seq) + packet[8:]
            if self.response == "unreachable":
                original_ip = bytes(20 if self.family == socket.AF_INET else 40)
                reply = struct.pack(ping3.ICMP_HEADER_FORMAT, icmp_type.DESTINATION_UNREACHABLE, 0, 0, 0, 0) + original_ip + struct.pack(ping3.ICMP_HEADER_FORMAT, icmp_type.ECHO_REQUEST, 0, 0, header["id"], seq)
            if self.family == socket.AF_INET and self.type == socket.SOCK_RAW:
                reply = struct.pack(ping3.IPV4_HEADER_FORMAT, 0x45, 0, 20 + len(reply), 0, 0, 64, socket.IPPROTO_ICMP, 0, 0x7f000001, 0x7f000001) + reply
            self.writer.send(reply)
        return len(packet)


class SequenceTests(unittest.TestCase):
    def ping_with_socket(self, seq, family=socket.AF_INET, sock_type=socket.SOCK_RAW, response="echo", ping_func=ping3.ping):
        sock = EchoSocket(family, sock_type, response)
        # IPv6 checksum construction opens another socket to discover the source.
        class SourceSocket:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def connect(self, addr):
                pass
            def getsockname(self):
                return ("::1", 0, 0, 0)

        calls = [sock, SourceSocket()]
        def create_socket(*args):
            return calls.pop(0)

        with patch("ping3.socket.socket", side_effect=create_socket), patch("ping3.EXCEPTIONS", True):
            # Use an IPv4 literal or the actual IPv6 resolver, with no external DNS.
            result = ping_func("127.0.0.1" if family == socket.AF_INET else "::1", seq=seq, timeout=0.1)
        return result, ping3.read_icmp_header(sock.sent[0][:8])

    def test_sequence_wraps_in_send_and_reply_matching(self):
        for seq in (0, 65535, 65536, 65537, 2 ** 64 + 17):
            for family in (socket.AF_INET, socket.AF_INET6):
                for sock_type in (socket.SOCK_RAW, socket.SOCK_DGRAM):
                    with self.subTest(seq=seq, family=family, sock_type=sock_type):
                        result, header = self.ping_with_socket(seq, family, sock_type)
                        self.assertIsInstance(result, float)
                        self.assertEqual(header["seq"], seq % 65536)

    def test_negative_sequence_remains_invalid(self):
        with self.assertRaises(struct.error):
            self.ping_with_socket(-1)

    def test_wrapped_sequence_matches_quoted_errors(self):
        for family in (socket.AF_INET, socket.AF_INET6):
            for sock_type in (socket.SOCK_RAW, socket.SOCK_DGRAM):
                with self.subTest(family=family, sock_type=sock_type):
                    with self.assertRaises(ping3.errors.DestinationUnreachable):
                        self.ping_with_socket(65536, family, sock_type, "unreachable")

    def test_verbose_ping_continues_after_sequence_wrap(self):
        # Reach the boundary without emitting 65,536 preceding packets.
        original_ping = ping3.ping
        sequences = []
        def ping_at_boundary(dest_addr, seq, **kwargs):
            sequences.append(seq)
            if seq < 65535:
                return 0.001
            result, header = self.ping_with_socket(seq, ping_func=original_ping)
            self.assertEqual(header["seq"], seq % 65536)
            return result

        with patch("ping3.ping", side_effect=ping_at_boundary), contextlib.redirect_stdout(io.StringIO()):
            ping3.verbose_ping("127.0.0.1", count=65537)
        self.assertEqual(sequences[-2:], [65535, 65536])



if __name__ == "__main__":
    unittest.main()
