# Ping3
[![Build Status](https://travis-ci.org/kyan001/ping3.svg?branch=master)](https://travis-ci.org/kyan001/ping3)
![GitHub release](https://img.shields.io/github/release/kyan001/ping3.svg)
[![GitHub license](https://img.shields.io/github/license/kyan001/ping3.svg)](https://github.com/kyan001/ping3/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ping3.svg)

Ping3 is a pure python3 version of ICMP ping implementation using raw socket.\
(Note that ICMP messages can only be sent from processes running as root.)

> The Python2 version originally from [here](http://github.com/samuel/python-ping).\
> This version maintained at [this github repo](https://github.com/kyan001/ping3).

## Get Started

```shell
pip install ping3  # install ping
```

```python
>>> from ping3 import ping, verbose_ping
>>> ping('example.com')  # Returns delay in seconds.
0.215697261510079666

>>> verbose_ping('example.com')  # Ping 4 times in a row.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

```shell
$ ping3 example.com  # Verbose ping.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

## Installation

```shell
pip install ping3  # install ping3
pip install --upgrade ping3 # upgrade ping3
pip uninstall ping3  # uninstall ping3
```

## Functions

```python
>>> ping('example.com')  # Returns delay in seconds.
0.215697261510079666

>>> ping('not.exist.com')  # if host unknown (cannot resolve), returns False
False

>>> ping("224.0.0.0")  # If timed out (no reply), returns None
None

>>> ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout=4 for 4 seconds.
0.215697261510079666

>>> ping('example.com', unit='ms')  # Returns delay in milliseconds. Default unit='s' for seconds.
215.9627876281738

>>> ping('example.com', src_addr='192.168.1.15')  # Set source ip address for multiple interfaces. Default src_addr=None for no binding.
0.215697261510079666

>>> ping('example.com', ttl=5)  # Set packet Time-To-Live to 5. The packet is discarded if it does not reach the target host after 5 jumps. Default ttl=64.
None

>>> ping('example.com', size=56)  # Set ICMP packet payload to 56 bytes. The total ICMP packet size is 8 (header) + 56 (payload) = 64 bytes. Default size=56.
0.215697261510079666

>>> verbose_ping('example.com')  # Ping 4 times in a row.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout=4 for 4 seconds.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', count=6)  # Ping 6 times. Default count=4
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms

>>> verbose_ping('example.com', src_addr='192.168.1.15')  # Ping from source IP address. Default src_addr=None
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

>>> ping3.ping("example.com")  # "ping()" prints received IP header and ICMP header.
[DEBUG] IP HEADER: {'version': 69, 'tos': 0, 'len': 14336, 'id': 8620, 'flags': 0, 'ttl': 51, 'protocol': 1, 'checksum': *, 'src_addr': *, 'dest_addr': *}
[DEBUG] ICMP HEADER: {'type': 0, 'code': 0, 'checksum': 8890, 'id': 21952, 'seq': 0}
0.215697261510079666

>>> ping3.ping("example.com", timeout=0.0001)
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.0001s)
None

>>> ping3.ping("not.exist.com")
[DEBUG] Cannot resolve: Unknown host. (Host = not.exist.com)
False

>>> ping3.ping("example.com", ttl=1)
[DEBUG] Time exceeded: Time To Live expired.
None
```

### EXCEPTIONS mode

Raise exceptions when there are errors instead of return None

```python
>>> import ping3
>>> ping3.EXCEPTIONS = True  # Default is False.

>>> ping3.ping("example.com", timeout=0.0001)  # All Exceptions are subclasses of PingError
[... Traceback ...]
error.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

>>> ping3.ping("not.exist.com")
[... Traceback ...]
error.HostUnknown: Cannot resolve: Unknown host. (Host = not.exist.com)

>>> ping3.ping("example.com", ttl=1)
[... Traceback ...]
error.TimeToLiveExpired: Time exceeded: Time To Live expired.
```

## Command Line Exexcution

Execute ping3 from command-line.
Note: `ping3` needs `root` privilege to send/receive packets. You may want to use `sudo ping3`.

```shell
$ ping3 --help  # -h/--help. Command-line help message.
$ python -m ping3 --help  # Same as 'ping3'. 'ping3' is an alias for 'python -m ping3'

$ ping3 -v  # -v/--version. Show ping3 version number.
2.2.2

$ ping3 example.com  # Verbose ping.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 example.com 8.8.8.8  # Verbose ping all the addresses.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping '8.8.8.8' ... 5ms
ping '8.8.8.8' ... 2ms
ping '8.8.8.8' ... 6ms
ping '8.8.8.8' ... 5ms

$ ping3 -c 1 example.com  # -c/--count. How many pings should be sent. Default is 4.
ping 'example.com' ... 215ms

$ ping3 -w 10 example.com  # -w/--wait. Set timeout to 10 seconds. Default is 4.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 -t 5 example.com  # -t/--ttl. # Set TTL to 5. Default is 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout

$ ping3 -l 56 example.com  # -l/--load. Set ICMP packet payload to 56 bytes. Default is 56.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --exceptions --wait 0.001 example.com  # EXCPETIONS mode is on when --exceptions shows up.
[... Traceback ...]
error.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

$ ping3 --debug --wait 0.001 example.com  # DEBUG mode is on when --debug shows up.
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
```
