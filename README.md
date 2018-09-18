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

```py
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

```py
>>> ping('notexist.com')  # If timed out (no reply), returns None
None

>>> ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout=4 for 4 seconds.
0.215697261510079666

>>> ping('example.com', unit='ms')  # Returns delay in milliseconds. Default unit='s' for seconds.
215.9627876281738

>>> ping('example.com', src_addr='192.168.1.15')  # set source ip address for multiple interfaces. Default src_addr=None for no binding.
0.215697261510079666

>>> ping('example.com', ttl=5)  # set packet Time-To-Live to 5. The packet is discarded if it does not reach the target host after 5 jumps. Default ttl=64.
None

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
