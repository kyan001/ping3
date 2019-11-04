class PingError(Exception):
    pass


class TimeExceeded(PingError):
    pass


class TimeToLiveExpired(TimeExceeded):
    def __init__(self, message="Time exceeded: Time To Live expired."):
        super().__init__(message)


class HostUnknown(PingError):
    def __init__(self, dest_addr=None):
        message = "Cannot resolve: Unknown host."
        if dest_addr:
            message += " (Host = {})".format(dest_addr)
        super().__init__(message)


class Timeout(PingError):
    def __init__(self, timeout=None):
        message = "Request timeout for ICMP packet."
        if timeout is not None:
            message += " (Timeout = {}s)".format(timeout)
        super().__init__(message)
