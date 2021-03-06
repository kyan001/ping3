* 2.7.0:
    * Using `SOCK_DGRAM` instead of `SOCK_RAW` on macOS. According to [this](https://apple.stackexchange.com/questions/312857/how-does-macos-allow-standard-users-to-ping), `SOCK_DGRAM` can be sent by standard user on macOS.
