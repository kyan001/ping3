# Ping3
[![Build Status](https://travis-ci.org/kyan001/ping3.svg?branch=master)](https://travis-ci.org/kyan001/ping3)
![GitHub release](https://img.shields.io/github/release/kyan001/ping3.svg)
[![GitHub license](https://img.shields.io/github/license/kyan001/ping3.svg)](https://github.com/kyan001/ping3/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ping3.svg)

Ping3 is a pure python3 version of ICMP ping implementation using raw socket.\
(Note that on some platforms, ICMP messages can only be sent from processes running as root.)

> The Python2 version originally from [here](http://github.com/samuel/python-ping).\
> This version maintained at [this github repo](https://github.com/kyan001/ping3).

[Update Log](UPDATES.md)

## Get Started

* If you met "permission denied", you may need to run this as root.

```sh
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

```sh
$ ping3 example.com  # Verbose ping.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

## Installation

```sh
pip install ping3  # install ping3
pip install --upgrade ping3 # upgrade ping3
pip uninstall ping3  # uninstall ping3
```

## Functions

```python
>>> from ping3 import ping, verbose_ping

>>> ping('example.com')  # Returns delay in seconds.
0.215697261510079666

>>> ping('not.exist.com')  # If host unknown (cannot resolve), returns False.
False

>>> ping("224.0.0.0")  # If timed out (no reply), returns None.
None

>>> ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout is 4 for 4 seconds.
0.215697261510079666

>>> ping('example.com', unit='ms')  # Returns delay in milliseconds. Default unit is 's' for seconds.
215.9627876281738

>>> ping('example.com', src_addr='192.168.1.15')  # Set source ip address for multiple interfaces. Default src_addr is None for no binding.
0.215697261510079666

>>> ping('example.com', interface='eth0')  # LINUX ONLY. Set source interface for multiple network interfaces. Default interface is None for no binding.
0.215697261510079666

>>> ping('example.com', ttl=5)  # Set packet Time-To-Live to 5. The packet is discarded if it does not reach the target host after 5 jumps. Default ttl is 64.
None

>>> ping('example.com', size=56)  # Set ICMP packet payload to 56 bytes. The total ICMP packet size is 8 (header) + 56 (payload) = 64 bytes. Default size is 56.
0.215697261510079666

>>> verbose_ping('example.com')  # Ping 4 times in a row.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout is 4 for 4 seconds.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', count=6)  # Ping 6 times. Default count is 4.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms

>>> verbose_ping('example.com', count=0)  # Ping endlessly (0 means infinite loops). Using `ctrl + c` to stop manully.
ping 'example.com' ... 215ms
...

>>> verbose_ping('example.com', src_addr='192.168.1.15')  # Ping from source IP address for multiple interfaces. Default src_addr is None.
ping 'example.com' from '192.168.1.15' ... 215ms
ping 'example.com' from '192.168.1.15' ... 216ms
ping 'example.com' from '192.168.1.15' ... 219ms
ping 'example.com' from '192.168.1.15' ... 217ms

>>> verbose_ping('example.com', interface='wifi0')  # LINUX ONLY. Ping from network interface 'wifi0'. Default interface is None.
ping 'example.com' from '192.168.1.15' ... 215ms
ping 'example.com' from '192.168.1.15' ... 216ms
ping 'example.com' from '192.168.1.15' ... 219ms
ping 'example.com' from '192.168.1.15' ... 217ms

>>> verbose_ping('example.com', unit='s')  # Displays delay in seconds. Default unit is "ms" for milliseconds.
ping 'example.com' ... 1s
ping 'example.com' ... 2s
ping 'example.com' ... 1s
ping 'example.com' ... 1s

>>> verbose_ping('example.com', ttl=5)  # Set TTL to 5. Default is 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout

>>> verbose_ping('example.com', interval=5)  # Wait 5 seconds between each packet. Default is 0.
ping 'example.com' ... 215ms  # wait 5 secs
ping 'example.com' ... 216ms  # wait 5 secs
ping 'example.com' ... 219ms  # wait 5 secs
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', size=56)  # Set ICMP payload to 56 bytes. Default size is 56.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
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

>>> ping3.ping("example.com", timeout=0.0001)
[... Traceback ...]
ping3.errors.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

>>> ping3.ping("not.exist.com")
[... Traceback ...]
ping3.errors.HostUnknown: Cannot resolve: Unknown host. (Host = not.exist.com)

>>> ping3.ping("example.com", ttl=1)
[... Traceback ...]
ping3.errors.TimeToLiveExpired: Time exceeded: Time To Live expired.

>>> help(ping3.errors)  # More info about exceptions.
```

```python
import ping3
ping3.EXCEPTIONS = True

try:
    ping3.ping("not.exist.com")
except ping3.errors.HostUnknown:  # Specific error is catched.
    print("Host unknown error raised.")
except ping3.errors.PingError:  # All ping3 errors are subclasses of `PingError`.
    print("A ping error raised.")
```

## Command Line Execution

Execute ping3 from command-line.
Note: On some platforms, `ping3` needs root privilege to send/receive packets. You may want to use `sudo ping3`.

```sh
$ ping3 --help  # -h/--help. Command-line help message.
$ python -m ping3 --help  # Same as `ping3`. `ping3` is an alias for `python -m ping3`.

$ ping3 --version  # -v/--version. Show ping3 version number.
3.0.0

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

$ ping3 --count 1 example.com  # -c/--count. How many pings should be sent. Default is 4.
ping 'example.com' ... 215ms

$ ping3 --count 0 example.com  # Ping endlessly (0 means infinite loops). Using `ctrl + c` to stop manully.
ping 'example.com' ... 215ms
...

$ ping3 --timeout 10 example.com  # -t/--timeout. Set timeout to 10 seconds. Default is 4.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --ttl 5 example.com  # -T/--ttl. # Set TTL to 5. Default is 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout

$ ping3 --size 56 example.com  # -s/--size. Set ICMP packet payload to 56 bytes. Default is 56.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --interval 5 example.com  # -i/--interval. Wait 5 seconds between each packet. Default is 0.
ping 'example.com' ... 215ms  # wait 5 secs
ping 'example.com' ... 216ms  # wait 5 secs
ping 'example.com' ... 219ms  # wait 5 secs
ping 'example.com' ... 217ms

$ ping3 --interface eth0 example.com  # -I/--interface. LINUX ONLY. The gateway network interface to ping from. Default is None.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --src 192.168.1.15 example.com  # -S/--src. Ping from source IP address for multiple network interfaces. Default is None.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --exceptions --timeout 0.001 example.com  # -E/--exceptions. EXCPETIONS mode is on when this shows up.
[... Traceback ...]
ping3.errors.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

$ ping3 --debug --timeout 0.001 example.com  # -D/--debug. DEBUG mode is on when this shows up.
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
```
