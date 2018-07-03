#!/usr/bin/env python

import sys
import socket
import struct
import select
import time
import threading

__version__ = '1.1.0'

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.


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
        if whatReady[0] == []:  # Timeout
            return

        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        # Filters out the echo request itself.
        # This can be tested by pinging 127.0.0.1
        # You'll see your own request
        if type != 8 and packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

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
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", default_timer()) + data.encode()

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))  # Don't know about the 1


def ping(dest_addr, timeout=4, unit="s"):
    """
    Send one ping to destination address with the given timeout.

    Args:
        dest_addr: Str. The destination address. Ex. "192.168.1.1"/"example.com"
        timeout: Int. Timeout in seconds. Default is 4s, same as Windows CMD.
        unit: Str. The unit of returned value. Default is "s" for seconds, "ms" for milliseconds.

    Returns:
        The delay in seconds/milliseconds or None on timeout.
    """
    icmp_protocol = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
    my_ID = threading.current_thread().ident & 0xFFFF
    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)  # in seconds
    my_socket.close()
    if delay is None:
        return None
    if unit == "ms":
        delay *= 1000  # in milliseconds
    return delay


def verbose_ping(dest_addr, timeout=4, count=4):
    """
    Send pings to destination address with the given timeout and display the result.

    Args:
        dest_addr: Str. The destination address. Ex. "192.168.1.1"/"example.com"
        timeout: Int. Timeout in seconds. Default is 4s, same as Windows CMD.
        count: Int. How many pings should be sent. Default is 4, same as Windows CMD.

    Returns:
        Formatted ping results printed.
    """
    for i in range(count):
        print("ping '{}' ... ".format(dest_addr), end='')
        try:
            delay = ping(dest_addr, timeout)
        except socket.gaierror as e:
            print("Failed. (socket error: '{}')".format(e))
            break
        if delay is None:
            print("Timeout > {}s".format(timeout))
        else:
            delay = delay * 1000
            print("{}ms".format(int(delay)))
    print


if __name__ == '__main__':
    verbose_ping("example.com")
    verbose_ping("192.168.1.1")
