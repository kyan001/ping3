#!/usr/bin/env python

import sys
import socket
import struct
import select
import time
import threading

import icmp
import exception

__version__ = "1.4.1"

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time


def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = len(source_string)
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        count = count + 2

    if countTo < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = default_timer()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if not whatReady[0]:  # Timeout
            raise exception.TimeoutException

        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        # Filters out the echo request itself.
        # This can be tested by pinging 127.0.0.1
        # You'll see your own request
        if type != icmp.ECHO_REQUEST and packetID == ID:
            if type == icmp.ECHO_REPLY:
                bytesInDouble = struct.calcsize("d")
                timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
                return timeReceived - timeSent
            elif type == icmp.TIME_EXCEEDED:
                raise exception.ExceededTimeToLiveException
            elif type == icmp.DESTINATION_UNREACHABLE:
                raise exception.DestinationUnreachableException

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest_addr, ID):
    """
    Send one ping to the given >dest_addr<.
    """
    dest_addr = socket.gethostbyname(dest_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy header with a 0 checksum.
    # ID: Low-endian identifier, bbHHh: network byte order
    header = struct.pack("bbHHh", icmp.ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", default_timer()) + data.encode()

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack("bbHHh", icmp.ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))  # Don't know about the 1


def ping(dest_addr, timeout=4, unit="s", src_addr=None, ttl=64):
    """
    Send one ping to destination address with the given timeout.

    Args:
        dest_addr: Str. The destination address. Ex. "192.168.1.1"/"example.com"
        timeout: Int. Timeout in seconds. Default is 4s, same as Windows CMD.
        unit: Str. The unit of returned value. Default is "s" for seconds, "ms" for milliseconds.
        src_addr: Str. The IP address to ping from. Ex. "192.168.1.20"
        ttl: Int. The Time-To-Live of the outgoing packet. Default is 64, same as in Linux and macOS.

    Returns:
        The delay in seconds/milliseconds or None on timeout.
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    my_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    if src_addr:
        my_socket.bind((src_addr, 0))
    my_ID = threading.current_thread().ident & 0xFFFF
    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)  # in seconds
    my_socket.close()
    if delay is None:
        return None
    if unit == "ms":
        delay *= 1000  # in milliseconds
    return delay


def verbose_ping(dest_addr, count=4, *args, **kwargs):
    """
    Send pings to destination address with the given timeout and display the result.

    Args:
        dest_addr: Str. The destination address. Ex. "192.168.1.1"/"example.com"
        count: Int. How many pings should be sent. Default is 4, same as Windows CMD.
        *: And all the other arguments available in ping().

    Returns:
        Formatted ping results printed.
    """
    timeout = kwargs.get("timeout")
    src_addr = kwargs.get("src_addr")
    unit = kwargs.setdefault("unit", "ms")
    for i in range(count):
        output_text = "ping '{}'".format(dest_addr)
        output_text += " from '{}'".format(src_addr) if src_addr else ""
        output_text += " ... "
        print(output_text, end="")
        try:
            delay = ping(dest_addr, *args, **kwargs)
        except socket.gaierror as e:
            print("Failed. (socket error: '{}')".format(e))
            break
        if delay is None:
            print("Timeout > {}s".format(timeout) if timeout else "Timeout")
        else:
            print("{value}{unit}".format(value=int(delay), unit=unit))
    print()


if __name__ == "__main__":
    verbose_ping("example.com")
    verbose_ping("8.8.8.8")
