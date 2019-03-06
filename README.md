# Ping3

Ping3 is a pure python3 version of ICMP ping implementation using raw socket.
Note that ICMP messages can only be sent from processes running as root.

> The Python2 version originally from [here](http://github.com/samuel/python-ping)
> This version maintained at [this github repo](https://github.com/kyan001/python3-ping)

## Installation

```shell
pip install ping3
```

## Get Started

```python
>>> from ping3 import ping, verbose_ping
>>> ping('example.com')  # Returns delay in seconds.
0.215697261510079666

>>> verbose_ping('example.com')  # ping 4 times in a row.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

## Functions

```python
>>> ping('not.exist.com')  # If timed out (no reply), returns None
Cannot resolve not.exist.com: Unknown host

>>> ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout=4 for 4 seconds.
0.215697261510079666

>>> ping('example.com', unit='ms')  # Returns delay in milliseconds. Default unit='s' for seconds.
215.9627876281738

>>> ping('example.com', src_addr='192.168.1.15')  # set source ip address for multiple interfaces. Default src_addr=None for no binding.
0.215697261510079666

>>> ping('example.com', ttl=5)  # set packet Time-To-Live to 5. The packet is discarded if it does not reach the target host after 5 jumps. Default ttl=64.
None

>>> ping('example.com', size=56)  # set ICMP packet payload to 56 bytes. The total ICMP packet size is 8 (header) + 56 (payload) = 64 bytes.
0.215697261510079666

>>> verbose_ping('example.com', timeout=10)  # set timeout to 10 second. Default timeout=4 for 4 seconds.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', count=6)  # ping 6 times. Default count=4
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms

>>> verbose_ping('example.com', src_addr='192.168.1.15')  # ping from source IP address. Default src_addr=None
ping 'example.com' from '192.168.1.15' ... 215ms
ping 'example.com' from '192.168.1.15' ... 216ms
ping 'example.com' from '192.168.1.15' ... 219ms
ping 'example.com' from '192.168.1.15' ... 217ms

>>> verbose_ping('example.com', unit='s')  # Displays delay in seconds. Default unit="ms" for milliseconds.
ping 'example.com' ... 1s
ping 'example.com' ... 2s
ping 'example.com' ... 1s
ping 'example.com' ... 1s

>>> verbose_ping('example.com', ttl=5)  # Set TTL to 5. Default is 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
```

### DEBUG mode

Show more info for developers.

```python
>>> import ping3
>>> ping3.DEBUG = True  # Default is False.

>>> ping3.ping("example.com")  # ping() prints received IP header and ICMP header.
[DEBUG] IP HEADER: {'version': 69, 'tos': 0, 'len': 14336, 'id': 8620, 'flags': 0, 'ttl': 51, 'protocol': 1, 'checksum': *, 'src_addr': *, 'dest_addr': *}
[DEBUG] ICMP HEADER: {'type': 0, 'code': 0, 'checksum': 8890, 'id': 21952, 'seq': 0}
0.215697261510079666

>>> ping3.ping("example.com", timeout=0.0001)
[DEBUG] Request timeout for ICMP packet. (0.0001s)

>>> ping3.ping("not.exist.com")
Cannot resolve not.exist.com: Unknown host
[DEBUG] Cannot resolve not.exist.com: Unknown host

>>> ping3.ping("example.com", ttl=1)
...
[DEBUG] Time exceeded: Time To Live expired
```

### EXCEPTIONS mode

Raise exceptions when there are errors instead of return None

```python
>>> import ping3
>>> ping3.EXCEPTIONS = True  # Default is False.

>>> ping3.ping("example.com", timeout=0.0001)  # All Exceptions are subclasses of PingError
...
pingerror.Timeout: Request timeout for ICMP packet. (0.0001s)

>>> ping3.ping("not.exist.com")
...
pingerror.HostUnknown: Cannot resolve not.exist.com: Unknown host

>>> ping3.ping("example.com", ttl=1)
...
pingerror.TimeToLiveExpired: Time exceeded: Time To Live expired
```
