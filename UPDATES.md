# UPDATES
* 2.9.2:
    * Converted to a proper package
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
