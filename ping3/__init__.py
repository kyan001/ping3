#!/usr/bin/env python

import os
import socket
import struct
import select
import time
import platform
import zlib
import threading
import logging
import functools
import errno
import ipaddress

from . import errors
from .enums import ICMP_DEFAULT_CODE, IcmpV4Type, IcmpV4DestinationUnreachableCode, IcmpTimeExceededCode, IcmpV6Type, IcmpV6DestinationUnreachableCode

__version__ = "5.1.5"
DEBUG = False  # DEBUG: Show debug info for developers. (default False)
EXCEPTIONS = False  # EXCEPTIONS: Raise exception when delay is not available.
LOGGER = None  # LOGGER: Record logs into console or file. Logger object should have .debug() method.

# !=Network Byte Order(Big-Endian), B=Bytes (8), I=Integer (32), H=Unsigned short (16), B=Unsigned char (8)
IPV4_HEADER_FORMAT = "!BBHHHBBHII"  # B: Version (4) + IHL (4). B: TOS (8). H: Total Length (16). H: ID (16). B: Flags (3) + Fragment Offset (13). B: TTL (8). B: Protocol (8). H: Header Checksum (16). I: Source Address (32). I: Destination Address (32)
IPV6_HEADER_FORMAT = "!IHBB16s16s"  # I: Version (4) + Traffic Class (8) + Flow Label (20). H: Payload Length (16). B: Next Header (8). B: Hop Limit (8). 16s: Source Address (128). 16s: Destination Address (128).
ICMP_HEADER_FORMAT = "!BBHHH"  # According to netinet/ip_icmp.h. B: Type (8). B: Code (8). H: Checksum (16). H: ID (16). H: Sequence Number (16).
ICMP_TIME_FORMAT = "!d"  # d=double
ICMPV6_PSEUDO_HEADER_FORMAT = "!16s16sIBBBB"  # 16s: Source Address (128), 16s: Destination Address (128), I: ICMPv6 Length (32), B: Zeros (24), B: Next Header (8)
SOCKET_SO_BINDTODEVICE = 25  # socket.SO_BINDTODEVICE


def _debug(*args) -> None:
    """Print debug info to stdout if `ping3.DEBUG` is True.

    Args:
        *args (any): Usually are strings or objects that can be converted to str.
    """

    def get_logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        cout_handler = logging.StreamHandler()
        cout_handler.setLevel(logging.DEBUG)
        cout_handler.setFormatter(formatter)
        logger.addHandler(cout_handler)
        logger.debug("Ping3 Version: {}".format(__version__))
        logger.debug("LOGGER: {}".format(logger))
        return logger

    if not DEBUG:
        return None
    global LOGGER
    LOGGER = LOGGER or get_logger()
    message = " ".join(str(item) for item in args)
    LOGGER.debug(message)


def _raise(err: Exception) -> None:
    """Raise exception if `ping3.EXCEPTIONS` is True.

    Args:
        err (Exception): Exception to be raised.

    Raise:
        Exception: Exception passed in args will be raised if `ping3.EXCEPTIONS` is True.
    """
    if EXCEPTIONS:
        raise err


def _func_logger(func):
    """Decorator that log function calls for debug

    Args:
        func (callable): Function to be decorated.

    Returns:
        callable: Decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pargs = ", ".join(str(arg) for arg in args)
        kargs = str(kwargs) if kwargs else ""
        all_args = ", ".join((pargs, kargs)) if (pargs and kargs) else (pargs or kargs)
        _debug("Function called:", "{func.__name__}({})".format(all_args, func=func))
        func_return = func(*args, **kwargs)
        _debug("Function returned:", "{func.__name__} -> {rtrn}".format(func=func, rtrn=func_return))
        return func_return

    return wrapper


def is_ipv4(sock: socket.socket) -> bool:
    """Check if the socket is IPv4.

    Args:
        sock (socket.socket): The socket to be checked.

    Returns:
        bool: True if the socket is IPv4, False otherwise.
    """
    return sock.family == socket.AF_INET


def checksum(source: bytes) -> int:
    """Calculates the checksum of the input bytes.

    RFC1071: https://tools.ietf.org/html/rfc1071
    RFC792: https://tools.ietf.org/html/rfc792

    Args:
        source (Bytes): The input to be calculated.

    Returns:
        int: Calculated checksum.
    """
    BITS = 16  # 16-bit long
    carry = 1 << BITS  # 0x10000
    result = sum(source[::2]) + (sum(source[1::2]) << (BITS // 2))  # Even bytes (odd indexes) shift 1 byte to the left.
    while result >= carry:  # Ones' complement sum.
        result = sum(divmod(result, carry))  # Each carry add to right most bit.
    return ~result & ((1 << BITS) - 1)  # Ensure 16-bit


def read_icmp_header(raw: bytes) -> dict:
    """Get information from raw ICMP header data.

    Args:
        raw (Bytes): Raw data of ICMP header.

    Returns:
        dict: A map contains the infos from the raw header.
    """
    icmp_header_keys = ("type", "code", "checksum", "id", "seq")
    return dict(zip(icmp_header_keys, struct.unpack(ICMP_HEADER_FORMAT, raw)))


def read_ipv4_header(raw: bytes) -> dict:
    """Get information from raw IPv4 header data.

    Args:
        raw (Bytes): Raw data of IPv4 header.

    Returns:
        dict: A map contains the infos from the raw header.
    """

    def stringify_ip(ip: int) -> str:
        return ".".join(str(ip >> offset & 0xFF) for offset in (24, 16, 8, 0))  # str(ipaddress.ip_address(ip))

    ipv4_header_keys = ("version", "tos", "len", "id", "flags", "ttl", "protocol", "checksum", "src_addr", "dest_addr")
    ipv4_header = dict(zip(ipv4_header_keys, struct.unpack(IPV4_HEADER_FORMAT, raw)))
    ipv4_header["src_addr"] = stringify_ip(ipv4_header["src_addr"])
    ipv4_header["dest_addr"] = stringify_ip(ipv4_header["dest_addr"])
    return ipv4_header


def read_ipv6_header(raw: bytes) -> dict:
    """Get information from raw IPv6 header data.

    Args:
        raw (Bytes): Raw data of IPv6 header.

    Returns:
        dict: A map contains the infos from the raw header.
    """
    ipv6_header_keys = ("initial", "len", "next_header", "hop_limit", "src_addr", "dest_addr")
    ipv6_header_unpacked = dict(zip(ipv6_header_keys, struct.unpack(IPV6_HEADER_FORMAT, raw[:40])))
    ipv6_header = {
        "len": ipv6_header_unpacked["len"],
        "next_header": ipv6_header_unpacked["next_header"],
        "hop_limit": ipv6_header_unpacked["hop_limit"],
    }
    ipv6_header["version"] = (ipv6_header_unpacked["initial"] >> 28) & 0x0F  # First 32 bits is combined version (4), traffic class (8) and flow label (20).
    ipv6_header["traffic_class"] = (ipv6_header_unpacked["initial"] >> 20) & 0xFF
    ipv6_header["flow_label"] = ipv6_header_unpacked["initial"] & 0xFFFFF
    ipv6_header["src_addr"] = socket.inet_ntop(socket.AF_INET6, ipv6_header_unpacked["src_addr"])  # Convert source address to readable format.
    ipv6_header["dest_addr"] = socket.inet_ntop(socket.AF_INET6, ipv6_header_unpacked["dest_addr"])  # Convert destination address to readable format.
    return ipv6_header


@_func_logger
def send_one_ping(sock: socket.socket, dest_addr: str, icmp_id: int, seq: int, size: int) -> None:
    """Sends one ping to the given destination.

    ICMP Header (bits): type (8), code (8), checksum (16), id (16), sequence (16)
    ICMP Payload: time (double), data
    ICMP Wikipedia: https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol
    ICMPv6 Wikipedia: https://en.wikipedia.org/wiki/ICMPv6
    IPv4 Wikipedia: https://en.wikipedia.org/wiki/IPv4
    IPv6 Wikipedia: https://en.wikipedia.org/wiki/IPv6_packet

    Args:
        sock (socket.socket): Socket.
        dest_addr: The destination address, can be an IPv4 address or an IPv6 address or a domain name. Ex. "192.168.1.1"/"example.com"/"2001:db8::1"
            Socket address is (dest_addr, port) with IPv4 and (dest_addr, port, flowinfo, scopeid) with IPv6. Port is 0 respectively the OS default behavior will be used. With IPv6, Flowinfo is 0, Scope ID is the interface index if dest_addr is a link-local address.
        icmp_id (int): ICMP packet id. Calculated from Process ID and Thread ID.
        seq (int): ICMP packet sequence, usually increases from 0 in the same process.
        size (int): The ICMP packet payload size in bytes. Note this is only for the payload part.

    Raises:
        HostUnkown: If destination address is a domain name and cannot resolved.
    """
    _debug("Destination address:", dest_addr)
    try:  # Resolve domain name to IP address if needed.
        if is_ipv4(sock):
            dest_addr = socket.gethostbyname(dest_addr)  # Domain name will translated into IP address, and IP address leaves unchanged.
            sock_addr = (dest_addr, 0)  # For IPv4, sock_addr is (dest_addr, port). Port is 0 respectively the OS default behavior will be used.
        else:
            sock_addr = socket.getaddrinfo(dest_addr, None, socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)[0][4]  # For IPv6, sock_addr is (dest_addr, port, flowinfo, scopeid)
    except socket.gaierror as err:
        raise errors.HostUnknown(dest_addr=dest_addr) from err
    _debug("Resolved destination address:", sock_addr[0])

    pseudo_checksum = 0  # Pseudo checksum is used to calculate the real checksum.

    icmp_header = struct.pack(
        ICMP_HEADER_FORMAT,
        IcmpV4Type.ECHO_REQUEST if is_ipv4(sock) else IcmpV6Type.ECHO_REQUEST,
        ICMP_DEFAULT_CODE,
        pseudo_checksum,
        icmp_id,
        seq,
    )
    padding = (size - struct.calcsize(ICMP_TIME_FORMAT)) * "Q"  # Using double to store current time.
    icmp_payload = struct.pack(ICMP_TIME_FORMAT, time.time()) + padding.encode()
    if is_ipv4(sock):
        real_checksum = checksum(icmp_header + icmp_payload)  # Calculates the checksum on the dummy header and the icmp_payload.
    else:  # ICMPv6 requires a pseudo header for checksum calculation.
        with socket.socket(socket.AF_INET6, sock.type, sock.proto) as dummy_sock:  # Create a dummy socket to get the source address.
            dummy_sock.connect(sock_addr)  # Set default dest_addr so the OS can select the correct source address. No real data is sent.
            src_addr = dummy_sock.getsockname()[0]  # Get the source address.
        _debug("Source Address: {}".format(src_addr))
        pseudo_header = struct.pack(  # https://en.wikipedia.org/wiki/ICMPv6#Checksum
            ICMPV6_PSEUDO_HEADER_FORMAT,  # 16s: Source Address (128), 16s: Destination Address (128), B: Next Header (8), B: Payload Length (16)
            socket.inet_pton(socket.AF_INET6, src_addr),  # Source Address
            socket.inet_pton(socket.AF_INET6, sock_addr[0]),  # Destination Address
            len(icmp_header) + len(icmp_payload),  # ICMPv6 Length
            0, 0, 0,  # Zeros
            IcmpV6Type.ECHO_REQUEST,  # Next Header (ICMPv6 Type)
        )
        real_checksum = checksum(pseudo_header + icmp_header + icmp_payload)  # Calculates the checksum on the pseudo header + icmp_header + icmp_payload.
    icmp_header = struct.pack(
        ICMP_HEADER_FORMAT,
        IcmpV4Type.ECHO_REQUEST if is_ipv4(sock) else IcmpV6Type.ECHO_REQUEST,
        ICMP_DEFAULT_CODE,
        socket.htons(real_checksum),  # Don't know why I need socket.htons() on real_checksum since ICMP_HEADER_FORMAT already in Network Bytes Order (big-endian)
        icmp_id,
        seq,
    )  # Put real checksum into ICMP header.
    _debug("Sent ICMP header:", read_icmp_header(icmp_header))
    _debug("Sent ICMP payload:", icmp_payload)
    packet = icmp_header + icmp_payload
    sock.sendto(packet, sock_addr)  # sock_addr = (ip, port) or (ip, port, flowinfo, scopeid).


@_func_logger
def receive_one_ping(sock: socket.socket, icmp_id: int, seq: int, timeout: int):
    """Receives the ping from the socket.

    IP Header (bits): version (8), type of service (8), length (16), id (16), flags (16), time to live (8), protocol (8), checksum (16), source ip (32), destination ip (32).
    ICMP Packet (bytes): IP Header (20), ICMP Header (8), ICMP Payload (*).
    Ping Wikipedia: https://en.wikipedia.org/wiki/Ping_(networking_utility)
    ToS (Type of Service) in IP header for ICMP is 0. Protocol in IP header for ICMP is 1.

    Args:
        sock (socket.socket): The same socket used for send the ping.
        icmp_id (int): ICMP packet id. Sent packet id should be identical with received packet id.
        seq (int): ICMP packet sequence. Sent packet sequence should be identical with received packet sequence.
        timeout (int): Timeout in seconds.

    Returns:
        float | None: The delay in seconds or None on timeout.

    Raises:
        TimeToLiveExpired: If the Time-To-Live in IP Header is not large enough for destination.
        TimeExceeded: If time exceeded but Time-To-Live does not expired.
        DestinationHostUnreachable: If the destination host is unreachable.
        DestinationUnreachable: If the destination is unreachable.
    """
    def detect_ip_header(sock, recv_data):
        """Detect if the received data has an IP header.

        IPv4 header first 4 bits is 4 (0b0100). ICMPv4 Type starts with 4 (64~79) is unassigned. See https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages
        IPv6 header first 4 bits is 6 (0b0110). ICMPv6 Type starts with 6 (96~111) is unassigned. See https://en.wikipedia.org/wiki/ICMPv6#Types

        Args:
            sock (socket.socket): The socket used to receive the data.
            recv_data (bytes): The received data.

        Returns:
            bool: True if the received data has an IP header, False otherwise.
        """
        first_field = recv_data[0] >> 4  # The first 4 bits of the first byte is the version field of IP Header.
        _debug("Detecting if received data has IP header. First 4 bits: {}".format(first_field))
        return first_field == (4 if is_ipv4(sock) else 6)

    icmp_type = IcmpV4Type if is_ipv4(sock) else IcmpV6Type
    timeout_time = time.time() + timeout  # Exactly time when timeout.
    _debug("Timeout time: {} ({})".format(time.ctime(timeout_time), timeout_time))
    while True:
        timeout_left = timeout_time - time.time()  # How many seconds left until timeout.
        timeout_left = timeout_left if timeout_left > 0 else 0  # Timeout must be non-negative
        _debug("Timeout left: {:.2f}s".format(timeout_left))

        selected = select.select([sock], [], [], timeout_left)  # Wait until sock is ready to read or time is out.
        if selected[0] == []:  # Timeout
            raise errors.Timeout(timeout=timeout)
        time_recv = time.time()
        _debug("Received time: {} ({}))".format(time.ctime(time_recv), time_recv))
        recv_data, addr = sock.recvfrom(1500)  # Single packet size limit is 65535 bytes, but usually the network packet limit is 1500 bytes.

        if is_ipv4(sock):
            has_ip_header = (os.name != "posix") or (platform.system() == "Darwin") or (sock.type == socket.SOCK_RAW)  # No IP Header when unprivileged on Linux.
        else:
            has_ip_header = detect_ip_header(sock, recv_data)
        if has_ip_header:
            _debug("Has IP header: True")
            ip_header_slice = slice(0, struct.calcsize(IPV4_HEADER_FORMAT if is_ipv4(sock) else IPV6_HEADER_FORMAT))  # [0:20]
            icmp_header_slice = slice(ip_header_slice.stop, ip_header_slice.stop + struct.calcsize(ICMP_HEADER_FORMAT))  # [20:28]
            ip_header_raw = recv_data[ip_header_slice]
            ip_header = read_ipv4_header(ip_header_raw) if is_ipv4(sock) else read_ipv6_header(ip_header_raw)
            _debug("Received IP header:", ip_header)
        else:
            _debug("Has IP header: False")
            ip_header = None
            icmp_header_slice = slice(0, struct.calcsize(ICMP_HEADER_FORMAT))  # [0:8]
        icmp_header_raw, icmp_payload_raw = recv_data[icmp_header_slice], recv_data[icmp_header_slice.stop:]
        icmp_header = read_icmp_header(icmp_header_raw)
        _debug("Received ICMP header:", icmp_header)
        _debug("Received ICMP payload:", icmp_payload_raw)
        if icmp_header["type"] == icmp_type.TIME_EXCEEDED:  # TIME_EXCEEDED has no icmp_id and icmp_seq. Usually they are 0.
            if icmp_header["code"] == IcmpTimeExceededCode.TTL_EXPIRED:  # Windows raw socket cannot get TTL_EXPIRED. See https://stackoverflow.com/questions/43239862/socket-sock-raw-ipproto-icmp-cant-read-ttl-response.
                raise errors.TimeToLiveExpired(ip_header=ip_header, icmp_header=icmp_header)  # Some router does not report TTL expired and then timeout shows.
            raise errors.TimeExceeded()
        if icmp_header["type"] == icmp_type.DESTINATION_UNREACHABLE:  # DESTINATION_UNREACHABLE has no icmp_id and icmp_seq. Usually they are 0.
            if is_ipv4(sock):
                if icmp_header["code"] == IcmpV4DestinationUnreachableCode.DESTINATION_HOST_UNREACHABLE:
                    raise errors.DestinationHostUnreachable(ip_header=ip_header, icmp_header=icmp_header)
            else:
                if icmp_header["code"] == IcmpV6DestinationUnreachableCode.ADDRESS_UNREACHABLE:
                    raise errors.AddressUnreachable(ip_header=ip_header, icmp_header=icmp_header)
                elif icmp_header["code"] == IcmpV6DestinationUnreachableCode.PORT_UNREACHABLE:
                    raise errors.PortUnreachable(ip_header=ip_header, icmp_header=icmp_header)
            raise errors.DestinationUnreachable(
                ip_header=ip_header, icmp_header=icmp_header
            )
        if icmp_header["id"]:
            if icmp_header["type"] == icmp_type.ECHO_REQUEST:  # filters out the ECHO_REQUEST itself.
                _debug("ECHO_REQUEST received. Packet filtered out.")
                continue
            _debug("ICMP ID:", icmp_header["id"], ",", "Expected:", icmp_id)
            is_icmp_id_matched = icmp_header["id"] == icmp_id  # ECHO_REPLY should match the ICMP ID
            if not is_icmp_id_matched and not has_ip_header:  # When unprivileged on Linux, ICMP ID is rewrited by kernel.field.
                icmp_id = sock.getsockname()[1]  # According to https://stackoverflow.com/a/14023878/4528364, icmp_id is the port number of the socket.
                is_icmp_id_matched = icmp_header["id"] == icmp_id
                if is_icmp_id_matched:
                    _debug("ICMP ID rewrited by kernel: {}".format(icmp_id))
            if not is_icmp_id_matched:
                _debug("ICMP ID dismatch. Packet filtered out.")
                continue
            if icmp_header["seq"] != seq:  # ECHO_REPLY should match the ICMP SEQ field.
                _debug("IMCP SEQ dismatch. Packet filtered out.")
                continue
            if icmp_header["type"] == icmp_type.ECHO_REPLY:
                time_sent = struct.unpack(ICMP_TIME_FORMAT, icmp_payload_raw[0 : struct.calcsize(ICMP_TIME_FORMAT)])[0]
                _debug("Received sent time: {} ({})".format(time.ctime(time_sent), time_sent))
                return time_recv - time_sent
        _debug("Uncatched ICMP packet:", icmp_header)


@_func_logger
def ping(dest_addr: str, timeout: int = 4, unit: str = "s", src_addr: str = "", ttl=None, seq: int = 0, size: int = 56, interface: str = "", version=None):
    """
    Send one ping to destination address with the given timeout.

    Args:
        dest_addr (str): The destination address, can be an IP address or a domain name. Ex. "192.168.1.1"/"example.com"/“fd00::1“
        timeout (int): Time to wait for a response, in seconds. Default is 4s, same as Windows CMD. (default 4)
        unit (str): The unit of returned value. "s" for seconds, "ms" for milliseconds. (default "s")
        src_addr (str): The IP address to ping from. This is for multiple network interfaces. Ex. "192.168.1.20". (default "")
        ttl (int | None): The Time-To-Live of the outgoing packet. Default is None, which means using OS default ttl -- 64 onLinux and macOS, and 128 on Windows. (default None)
        seq (int): ICMP packet sequence, usually increases from 0 in the same process. (default 0)
        size (int): The ICMP packet payload size in bytes. If the input of this is less than the bytes of a double format (usually 8), the size of ICMP packet payload is 8 bytes to hold a time. The max should be the router_MTU(Usually 1480) - IP_Header(20) - ICMP_Header(8). Default is 56, same as in macOS. (default 56)
        interface (str): LINUX ONLY. The gateway network interface to ping from. Ex. "wlan0". (default "")
        ip_v (int | None): The IP version to use. 4 for IPv4, 6 for IPv6. If None, the function will try to determine the IP version from `dest_addr`. (default None)

    Returns:
        float | None | False: The delay in seconds/milliseconds, False on error and None on timeout.

    Raises:
        PingError: Any PingError will raise again if `ping3.EXCEPTIONS` is True.
    """
    if version is None:  # Auto detect IP version if not specified.
        try:
            ip = ipaddress.ip_address(dest_addr)
            version = ip.version
        except ValueError:
            version = 4  # Default to IPv4 if the address is not a valid IP address.
    _debug("Ping IPv{}:".format(version), dest_addr)
    if version == 4:
        socket_family = socket.AF_INET
        socket_protocol = socket.IPPROTO_ICMP
    elif version == 6:
        socket_family = socket.AF_INET6
        socket_protocol = socket.IPPROTO_ICMPV6
    else:
        raise ValueError("Unsupported IP version: {}".format(version))
    try:
        sock = socket.socket(socket_family, socket.SOCK_RAW, socket_protocol)
    except PermissionError as err:
        if err.errno == errno.EPERM:  # [Errno 1] Operation not permitted
            _debug("`{}` when create socket.SOCK_RAW, using socket.SOCK_DGRAM instead.".format(err))
            sock = socket.socket(socket_family, socket.SOCK_DGRAM, socket_protocol)  # TBC: On Linux, using SOCK_DGRAM with IPPROTO_ICMPV6 will not work as expected. It will not send ICMP packets, but will send UDP packets instead.
        else:
            raise err
    with sock:
        if ttl:
            if is_ipv4(sock):  # socket.IP_TTL and socket.SOL_IP are for IPv4.
                try:  # IPPROTO_IP is for Windows and BSD Linux.
                    if sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL):  # TTL is a IPPROTO_IP option, not IPPROTO_ICMP. See: https://datatracker.ietf.org/doc/html/rfc1122#page-34
                        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
                except OSError as err:
                    _debug("Set Socket Option `IP_TTL` in `IPPROTO_IP` Failed: {}".format(err))
                try:
                    if sock.getsockopt(socket.SOL_IP, socket.IP_TTL):
                        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                except OSError as err:
                    _debug("Set Socket Option `IP_TTL` in `SOL_IP` Failed: {}".format(err))
            else:  # IPv6
                try:  # socket.IPV6_UNICAST_HOPS is for IPv6.
                    if sock.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_UNICAST_HOPS):  # Unicast Hop Limit should be used at the IPPROTO_IPV6 Layer, not the IPPROTO_ICMPV6 Layer. See: https://datatracker.ietf.org/doc/html/rfc3493#section-5.1
                        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_UNICAST_HOPS, ttl)
                except OSError as err:
                    _debug("Set Socket Option `IPV6_UNICAST_HOPS` in `IPPROTO_IPV6` Failed: {}".format(err))
        if interface:  # Packets will be sent from specified interface.
            sock.setsockopt(socket.SOL_SOCKET, SOCKET_SO_BINDTODEVICE, interface.encode())  # Linux only. Requires root.
            _debug("Socket Interface Binded:", interface)
        if src_addr:
            if is_ipv4(sock):
                sock.bind((src_addr, 0))  # only packets send to src_addr are received.
                _debug("Socket Source Address Binded:", src_addr)
            # TODO: Support src_addr for IPv6. Currently, the source address is determined by the OS when sending packets.
        thread_id = (threading.get_native_id() if hasattr(threading, "get_native_id") else threading.current_thread().ident)  # threading.get_native_id() is supported >= python3.8.
        process_id = os.getpid()  # If ping() run under different process, thread_id may be identical.
        icmp_id = zlib.crc32("{}{}".format(process_id, thread_id).encode()) & 0xffff  # to avoid icmp_id collision.
        try:
            send_one_ping(sock=sock, dest_addr=dest_addr, icmp_id=icmp_id, seq=seq, size=size)
            delay = receive_one_ping(sock=sock, icmp_id=icmp_id, seq=seq, timeout=timeout)  # in seconds
        except errors.Timeout as err:
            _debug(err)
            _raise(err)
            return None
        except errors.PingError as err:
            _debug(err)
            _raise(err)
            return False
        if delay is None:
            return None
        if unit == "ms":
            delay *= 1000  # in milliseconds
        return delay


@_func_logger
def verbose_ping(dest_addr: str, count: int = 4, interval: float = 0, *args, **kwargs):
    """
    Send pings to destination address with the given timeout and display the result.

    Args:
        dest_addr (str): The destination address. Ex. "192.168.1.1"/"example.com"
        count (int): How many pings should be sent. 0 means infinite loops until manually stopped. Default is 4, same as Windows CMD. (default 4)
        interval (float): How many seconds between two packets. Default is 0, which means send the next packet as soon as the previous one responsed. (default 0)
        *args and **kwargs (any): And all the other arguments available in ping() except `seq`.

    Output:
        Formatted ping results printed.
    """
    timeout = kwargs.get("timeout")
    src = kwargs.get("src_addr")
    unit = kwargs.setdefault("unit", "ms")
    i = 0
    while i < count or count == 0:
        if interval > 0 and i > 0:
            time.sleep(interval)
        output_text = "ping '{}'".format(dest_addr)
        output_text += " from '{}'".format(src) if src else ""
        output_text += " ... "
        delay = ping(dest_addr, seq=i, *args, **kwargs)
        print(output_text, end="")
        if delay is None:
            print("Timeout > {}s".format(timeout) if timeout else "Timeout")
        elif delay is False:
            print("Error")
        else:
            print("{value}{unit}".format(value=int(delay), unit=unit))
        i += 1
