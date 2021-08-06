import argparse

import ping3


def main(assigned_args: list = None):
    """
    Parse and execute the call from command-line.

    Args:
        assigned_args: List of strings to parse. The default is taken from sys.argv.

    Returns:
        Formatted ping results printed.
    """
    parser = argparse.ArgumentParser(prog="ping3", description="A pure python3 version of ICMP ping implementation using raw socket.", epilog="!!Note: ICMP messages can only be sent from processes running as root.")
    parser.add_argument("-v", "--version", action="version", version=ping3.__version__)
    parser.add_argument(dest="dest_addr", metavar="DEST_ADDR", nargs="*", default=("example.com", "8.8.8.8"), help="The destination address, can be an IP address or a domain name. Ex. 192.168.1.1/example.com.")
    parser.add_argument("-c", "--count", dest="count", metavar="COUNT", type=int, default=4, help="How many pings should be sent. Default is 4.")
    parser.add_argument("-t", "--timeout", dest="timeout", metavar="TIMEOUT", type=float, default=4, help="Time to wait for a response, in seconds. Default is 4.")
    parser.add_argument("-i", "--interval", dest="interval", metavar="INTERVAL", type=float, default=0, help="Time to wait between each packet, in seconds. Default is 0.")
    parser.add_argument("-I", "--interface", dest="interface", metavar="INTERFACE", default="", help="LINUX ONLY. The gateway network interface to ping from. Default is None.")
    parser.add_argument("-S", "--src", dest="src_addr", metavar="SRC_ADDR", default="", help="The IP address to ping from. This is for multiple network interfaces. Default is None")
    parser.add_argument("-T", "--ttl", dest="ttl", metavar="TTL", type=int, default=64, help="The Time-To-Live of the outgoing packet. Default is 64.")
    parser.add_argument("-s", "--size", dest="size", metavar="SIZE", type=int, default=56, help="The ICMP packet payload size in bytes. Default is 56.")
    parser.add_argument("-D", "--debug", action="store_true", dest="debug", help="Turn on DEBUG mode.")
    parser.add_argument("-E", "--exceptions", action="store_true", dest="exceptions", help="Turn on EXCEPTIONS mode.")
    args = parser.parse_args(assigned_args)
    ping3.DEBUG = args.debug
    ping3.EXCEPTIONS = args.exceptions

    for addr in args.dest_addr:
        ping3.verbose_ping(addr, count=args.count, ttl=args.ttl, timeout=args.timeout, size=args.size, interval=args.interval, interface=args.interface, src_addr=args.src_addr)


if __name__ == "__main__":
    main()
