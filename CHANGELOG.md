# Change Log
* 5.1.0：
    * Feature: Support TTL (Hop Limit) for IPv6 on Linux.
* 5.0.0:
    * Feature: Support IPv6 ping. ( #85 )
* 4.0.8:
    * Bug Fix: Command does not respect options with `-v/--version` and `-h/--help`. ( #80 )
* 4.0.7:
    * Bug Fix: Remove unsupported type hints in lower version of Python. ( #79 )
* 4.0.6:
    * Bug Fix: Type hint and comments refines. ( #78 )
* 4.0.5:
    * Bug Fix: Type hint refines. ( #78 )
* 4.0.4:
    * Improvement: Replace setup.py by pyproject.toml
* 4.0.2:
    * Bug Fix: Arg `src` in `verbose_ping` should be `src_addr`. ( #57 )
* 4.0.1:
    * Bug Fix: `message` should be the first argument in ping3.errors. ( #55 )
* 4.0.0:
    * Feature: Now errors `TimeToLiveExpired`, `DestinationUnreachable` and `DestinationHostUnreachable` have `ip_header` and `icmp_header` attached. ( #48 )
* 3.0.1:
    * Bug Fix: `verbose_ping` prints proper message on error.
* 3.0.0:
    * Backward Compatibility: Only Command-line options changed, now the options is more like `ping` on macOS and Linux.
        * `-w`/`--wait` -> `-t`/`--timeout`.
        * `-t`/`--ttl` -> `-T`/`--ttl`.
        * `-l`/`--load` -> `-s`/`--size`.
    * Improvement: 2 command-line options now have short forms.
        * `-D` is added as the short form of `--debug`.
        * `-E` is added as the short form of `--exceptions`.
    * Feature: Use new command-line option `-S`/`--src` to set source address `src_addr`.
* 2.9.3:
    * Bug Fix: Set packet receive buffer size to 1500. ( #40 )
* 2.9.2:
    * Improvement: Converted to a proper package. ( #38 #39 )
* 2.9.1:
    * Bug Fix: macOS is not treated as Linux now.
* 2.9.0:
    * Feature: Support root-less ICMP pings on Linux. ( #10 )
* 2.8.1:
    * Improvement: Checksum calculation is faster.
* 2.8.0:
    * Feature: Now support endless ping, using `ping3 -c 0 example.com` with a count of 0 or `ping3.verbose_ping('example.com', count=0)` to start, using `ctrl + c` to stop.
* 2.7.0:
    * Feature: Using `SOCK_DGRAM` instead of `SOCK_RAW` on macOS. According to [this](https://apple.stackexchange.com/questions/312857/how-does-macos-allow-standard-users-to-ping), `SOCK_DGRAM` can be sent by standard user on macOS.
* 2.6.6:
    * Bug Fix: `setsockopt` error for `SOL_IP.IP_TTL` on windows. ( #28 )
* 2.6.5:
    * Bug Fix: When multi-processing or multi-threading, icmp_id will no longer collision. ( #23 )
* 2.6.1:
    * Feature: Add network interface binding support for Linux. ( #22 )
* 2.5.1:
    * Features:
        * Add interval support to `ping3.verbose_ping()`. ( #17 )
        * Add `-i/--interval` argument for interval support in command-line.
* 2.4.7:
    * Bug Fix: Input parameter `size` in `ping()` should not include ICMP_Header size. ( #21 )
* 2.4.4:
    * Bug Fix: When there are a lot of incoming packets, and the destination address has no response, `ping()` never return. ( #14 )
* 2.4.0:
    * Feature: Return False if HostUnknown error raised (instead of print info to screen).
    * Improvement: Increase usability of errors and provide a more precisely text.
* 2.3.1:
    * Features:
        * Add `--debug` argument for DEBUG mode in command-line.
        * Add `--exceptions` argument for EXCEPTIONS mode in command-line.
* 2.2.3:
    * Feature: Add command-line mode.
* 2.0.1:
    * Features:
        * Add support of ICMP Payload size.
        * Add support of EXCEPTIONS mode.
        * Add support of DEBUG mode.
* 1.2.1:
    * Feature: Add support for multiple interfaces. Use `ping(..., src_addr="INTERFACE IP")`
* 1.1.0:
    * Improvement: Update tests and PyPI info.
