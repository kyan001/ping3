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

>>> ping('example.com', timeout=10)  # Set timeout to 10 seconds. Default timeout=4
0.215697261510079666

>>> ping('example.com', unit="ms")  # Returns delay in milliseconds
215.9627876281738

>>> verbose_ping('example.com', timeout=10)  # set timeout to 10 second. Default timeout=4

>>> verbose_ping('example.com', count=10)  # ping 10 times. Default count=4
```
