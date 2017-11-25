# python3-ping
A pure python3 version of ICMP ping implementation using raw socket.
Note that ICMP messages can only be sent from processes running as root.

> The Python2 version originally from http://github.com/samuel/python-ping
> This version maintained at https://github.com/kyan001/python3-ping

Usage:
```py
>>> import ping
>>> ping.do_one('example.com')  # Ping once. Returns delay in seconds.
0.030867429659792833

>>> ping.do_one('not-exist.com', timeout=4)  # Set timeout in seconds. Default is 4.
# If timed out, returns None

>>> ping.verbose('example.com')  # ping 4 times in a row. Default timeout=4, count=4
ping 'example.com' ... 6ms
ping 'example.com' ... 7ms
ping 'example.com' ... 5ms
ping 'example.com' ... 5ms
```
