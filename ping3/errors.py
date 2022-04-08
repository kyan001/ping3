class PingError(Exception):
    pass


class TimeExceeded(PingError):
    pass


class TimeToLiveExpired(TimeExceeded):
    def __init__(self, message="Time exceeded: Time To Live expired.", ip_header=None, icmp_header=None):
        self.ip_header = ip_header
        self.icmp_header = icmp_header
        self.message = message
        super().__init__(self.message)


class DestinationUnreachable(PingError):
    def __init__(self, message="Destination unreachable.", ip_header=None, icmp_header=None):
        self.ip_header = ip_header
        self.icmp_header = icmp_header
        self.message = message if self.ip_header is None else message + " (Host='{}')".format(self.ip_header.get("src_addr"))
        super().__init__(self.message)


class DestinationHostUnreachable(DestinationUnreachable):
    def __init__(self, message="Destination unreachable: Host unreachable.", ip_header=None, icmp_header=None):
        self.ip_header = ip_header
        self.icmp_header = icmp_header
        self.message = message if self.ip_header is None else message + " (Host='{}')".format(self.ip_header.get("src_addr"))
        super().__init__(self.message)


class HostUnknown(PingError):
    def __init__(self, message="Cannot resolve: Unknown host.", dest_addr=None):
        self.dest_addr = dest_addr
        self.message = message if self.dest_addr is None else message + " (Host='{}')".format(self.dest_addr)
        super().__init__(self.message)


class Timeout(PingError):
    def __init__(self, message="Request timeout for ICMP packet.", timeout=None):
        self.timeout = timeout
        self.message = message if self.timeout is None else message + " (Timeout={}s)".format(self.timeout)
        super().__init__(self.message)
