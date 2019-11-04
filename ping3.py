#!/usr/bin/env python

import sys
import socket
import struct
import select
import time
import threading

import errors
from enums import ICMP_DEFAULT_CODE, IcmpType, IcmpTimeExceededCode, IcmpDestinationUnreachableCode

__version__ = "2.4.0"
DEBUG = False  # DEBUG: Show debug info for developers. (default False)
EXCEPTIONS = False  # EXCEPTIONS: Raise exception when delay is not available.

IP_HEADER_FORMAT = "!BBHHHBBHII"
ICMP_HEADER_FORMAT = "!BBHHH"  # According to netinet/ip_icmp.h. !=network byte order(big-endian), B=unsigned char, H=unsigned short
ICMP_TIME_FORMAT = "!d"  # d=double


def _debug(*args):
    """Print debug info to stdout if `ping3.DEBUG` is True.

    Args:
        *args: Any. Usually are strings or objects that can be converted to str.
    """
    if DEBUG:
        message = "[DEBUG]"
        print(message, *args)


def _raise(err):
    """Raise exception if `ping3.EXCEPTIONS` is True.

    Args:
        err: Exception.

    Raise:
        Exception: Exception passed in args will be raised if `ping3.EXCEPTIONS` is True.
    """
    if EXCEPTIONS:
        raise err


def ones_comp_sum16(num1: int, num2: int) -> int:
    """Calculates the 1's complement sum for 16-bit numbers.

    Args:
        num1: 16-bit number.
        num2: 16-bit number.

    Returns:
        The calculated result.
    """

    carry = 1 << 16
    result = num1 + num2
    return result if result < carry else result + 1 - carry


def checksum(source: bytes) -> int:
    """Calculates the checksum of the input bytes.

    RFC1071: https://tools.ietf.org/html/rfc1071
    RFC792: https://tools.ietf.org/html/rfc792

    Args:
        source: The input to be calculated.

    Returns:
        Calculated checksum.
    """
    if len(source) % 2:  # if the total length is odd, padding with one octet of zeros for computing the checksum
        source += b'\x00'
    sum = 0
    for i in range(0, len(source), 2):
        sum = ones_comp_sum16(sum, (source[i + 1] << 8) + source[i])
    return ~sum & 0xffff


def send_one_ping(sock: socket, dest_addr: str, icmp_id: int, seq: int, size: int):
    """Sends one ping to the given destination.

    ICMP Header (bits): type (8), code (8), checksum (16), id (16), sequence (16)
    ICMP Payload: time (double), data
    ICMP Wikipedia: https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol

    Args:
        sock: Socket.
        dest_addr: The destination address, can be an IP address or a domain name. Ex. "192.168.1.1"/"example.com"
        icmp_id: ICMP packet id, usually is same as pid.
        seq: ICMP packet sequence, usually increases from 0 in the same process.
        size: The ICMP packet payload size in bytes. Note this is only for the payload part.

    Raises:
        HostUnkown: If destination address is a domain name and cannot resolved.
    """
    try:
        dest_addr = socket.gethostbyname(dest_addr)  # Domain name will translated into IP address, and IP address leaves unchanged.
    except socket.gaierror as e:
        raise errors.HostUnknown(dest_addr) from e
    pseudo_checksum = 0  # Pseudo checksum is used to calculate the real checksum.
    icmp_header = struct.pack(ICMP_HEADER_FORMAT, IcmpType.ECHO_REQUEST, ICMP_DEFAULT_CODE, pseudo_checksum, icmp_id, seq)
    padding = (size - struct.calcsize(ICMP_TIME_FORMAT) - struct.calcsize(ICMP_HEADER_FORMAT)) * "Q"  # Using double to store current time.
    icmp_payload = struct.pack(ICMP_TIME_FORMAT, time.time()) + padding.encode()
    real_checksum = checksum(icmp_header + icmp_payload)  # Calculates the checksum on the dummy header and the icmp_payload.
    # Don't know why I need socket.htons() on real_checksum since ICMP_HEADER_FORMAT already in Network Bytes Order (big-endian)
    icmp_header = struct.pack(ICMP_HEADER_FORMAT, IcmpType.ECHO_REQUEST, ICMP_DEFAULT_CODE, socket.htons(real_checksum), icmp_id, seq)  # Put real checksum into ICMP header.
    packet = icmp_header + icmp_payload
    sock.sendto(packet, (dest_addr, 0))  # addr = (ip, port). Port is 0 respectively the OS default behavior will be used.


def receive_one_ping(sock: socket, icmp_id: int, seq: int, timeout: int) -> float or None:
    """Receives the ping from the socket.

    IP Header (bits): version (8), type of service (8), length (16), id (16), flags (16), time to live (8), protocol (8), checksum (16), source ip (32), destination ip (32).
    ICMP Packet (bytes): IP Header (20), ICMP Header (8), ICMP Payload (*).
    Ping Wikipedia: https://en.wikipedia.org/wiki/Ping_(networking_utility)
    ToS (Type of Service) in IP header for ICMP is 0. Protocol in IP header for ICMP is 1.

    Args:
        sock: The same socket used for send the ping.
        icmp_id: ICMP packet id. Sent packet id should be identical with received packet id.
        seq: ICMP packet sequence. Sent packet sequence should be identical with received packet sequence.
        timeout: Timeout in seconds.

    Returns:
        The delay in seconds or None on timeout.

    Raises:
        TimeToLiveExpired: If the Time-To-Live in IP Header is not large enough for destination.
        TimeExceeded: If time exceeded but Time-To-Live does not expired.
    """
    ip_header_slice = slice(0, struct.calcsize(IP_HEADER_FORMAT))  # [0:20]
    icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))  # [20:28]
    ip_header_keys = ('version', 'tos', 'len', 'id', 'flags', 'ttl', 'protocol', 'checksum', 'src_addr', 'dest_addr')
    icmp_header_keys = ('type', 'code', 'checksum', 'id', 'seq')
    while True:
        selected = select.select([sock], [], [], timeout)
        if selected[0] == []:  # Timeout
            raise errors.Timeout(timeout)
        time_recv = time.time()
        recv_data, addr = sock.recvfrom(1024)
        ip_header_raw, icmp_header_raw, icmp_payload_raw = recv_data[ip_header_slice], recv_data[icmp_header_slice], recv_data[icmp_header_slice.stop:]
        ip_header = dict(zip(ip_header_keys, struct.unpack(IP_HEADER_FORMAT, ip_header_raw)))
        _debug("IP HEADER:", ip_header)
        icmp_header = dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, icmp_header_raw)))
        _debug("ICMP HEADER:", icmp_header)
        if icmp_header['type'] == IcmpType.TIME_EXCEEDED:  # TIME_EXCEEDED has no icmp_id and icmp_seq. Usually they are 0.
            if icmp_header['code'] == IcmpTimeExceededCode.TTL_EXPIRED:
                raise errors.TimeToLiveExpired()  # Some router does not report TTL expired and then timeout shows.
            raise errors.TimeExceeded()
        if icmp_header['id'] == icmp_id and icmp_header['seq'] == seq:  # ECHO_REPLY should match the
            if icmp_header['type'] == IcmpType.ECHO_REQUEST:  # filters out the ECHO_REQUEST itself.
                _debug("ECHO_REQUEST filtered out.")
                continue
            if icmp_header['type'] == IcmpType.ECHO_REPLY:
                time_sent = struct.unpack(ICMP_TIME_FORMAT, icmp_payload_raw[0:struct.calcsize(ICMP_TIME_FORMAT)])[0]
                return time_recv - time_sent


def ping(dest_addr: str, timeout: int = 4, unit: str = "s", src_addr: str = None, ttl: int = 64, seq: int = 0, size: int = 56) -> float or None:
    """
    Send one ping to destination address with the given timeout.

    Args:
        dest_addr: The destination address, can be an IP address or a domain name. Ex. "192.168.1.1"/"example.com"
        timeout: Time to wait for a response, in seconds. Default is 4s, same as Windows CMD. (default 4)
        unit: The unit of returned value. "s" for seconds, "ms" for milliseconds. (default "s")
        src_addr: The IP address to ping from. This is for multi-interface clients. Ex. "192.168.1.20". (default None)
        ttl: The Time-To-Live of the outgoing packet. Default is 64, same as in Linux and macOS. (default 64)
        seq: ICMP packet sequence, usually increases from 0 in the same process. (default 0)
        size: The ICMP packet payload size in bytes. Default is 56, same as in macOS. (default 56)

    Returns:
        The delay in seconds/milliseconds or None on timeout.

    Raises:
        PingError: Any PingError will raise again if `ping3.EXCEPTIONS` is True.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        if src_addr:
            sock.bind((src_addr, 0))  # only packets send to src_addr are received.
        icmp_id = threading.current_thread().ident % 0xFFFF
        try:
            send_one_ping(sock=sock, dest_addr=dest_addr, icmp_id=icmp_id, seq=seq, size=size)
            delay = receive_one_ping(sock=sock, icmp_id=icmp_id, seq=seq, timeout=timeout)  # in seconds
        except errors.HostUnknown as e:  # Unsolved
            _debug(e)
            _raise(e)
            return False
        except errors.PingError as e:
            _debug(e)
            _raise(e)
            return None
        if delay is None:
            return None
        if unit == "ms":
            delay *= 1000  # in milliseconds
    return delay


def verbose_ping(dest_addr: str, count: int = 4, *args, **kwargs):
    """
    Send pings to destination address with the given timeout and display the result.

    Args:
        dest_addr: The destination address. Ex. "192.168.1.1"/"example.com"
        count: How many pings should be sent. Default is 4, same as Windows CMD. (default 4)
        *args and **kwargs: And all the other arguments available in ping() except `seq`.

    Returns:
        Formatted ping results printed.
    """
    timeout = kwargs.get("timeout")
    src = kwargs.get("src")
    unit = kwargs.setdefault("unit", "ms")
    for i in range(count):
        output_text = "ping '{}'".format(dest_addr)
        output_text += " from '{}'".format(src) if src else ""
        output_text += " ... "
        delay = ping(dest_addr, seq=i, *args, **kwargs)
        print(output_text, end="")
        if delay is None:
            print("Timeout > {}s".format(timeout) if timeout else "Timeout")
        else:
            print("{value}{unit}".format(value=int(delay), unit=unit))


if __name__ == "__main__":
    import command_line_ping3
    command_line_ping3.main()
