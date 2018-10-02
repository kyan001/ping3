class DestinationUnreachableException(Exception):
    def __init__(self, message="Destination was reported unreachable."):
        super(Exception, self).__init__(message)


class TimeToLiveExceededException(Exception):
    def __init__(self, reporter_address, message=None):
        self.reporter_address = reporter_address
        m = message if message else \
            "Address %s reported that the packet time to live was exceeded." % reporter_address
        super(Exception, self).__init__(m)


class TimeoutException(Exception):
    def __init__(self, message="The timeout was exceeded."):
        super(Exception, self).__init__(message)
