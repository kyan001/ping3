# Ping3
[![Build Status](https://travis-ci.org/kyan001/ping3.svg?branch=master)](https://travis-ci.org/kyan001/ping3)
![GitHub release](https://img.shields.io/github/release/kyan001/ping3.svg)
[![GitHub license](https://img.shields.io/github/license/kyan001/ping3.svg)](https://github.com/kyan001/ping3/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ping3.svg)

Ping3 — это реализация ICMP ping на чистом Python 3 с использованием сырых сокетов.\
(Обратите внимание: на некоторых платформах ICMP-сообщения могут отправляться только процессами с правами суперпользователя.)

> Версия для Python 2 изначально взята [отсюда](http://github.com/samuel/python-ping).\
> Данная версия поддерживается в [этом репозитории на GitHub](https://github.com/kyan001/ping3).

🌐 [English](README.md) | Русский

✨ [CHANGELOG](CHANGELOG.md)

## Начало работы

* Если вы получили ошибку «permission denied», возможно, потребуется запустить программу с правами суперпользователя. Также см. [это руководство](./TROUBLESHOOTING.md#permission-denied-on-linux) по устранению неполадок на Linux.

```sh
pip install ping3  # установить ping3
```

```python
>>> from ping3 import ping, verbose_ping
>>> ping('example.com')  # Возвращает задержку в секундах.
0.215697261510079666

>>> verbose_ping('example.com')  # Пинг 4 раза подряд.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

```sh
$ ping3 example.com  # Подробный пинг.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

## Установка

```sh
pip install ping3  # установить ping3
pip install --upgrade ping3 # обновить ping3
pip uninstall ping3  # удалить ping3
```

## Функции

```python
>>> from ping3 import ping, verbose_ping

>>> ping('example.com')  # Возвращает задержку в секундах.
0.215697261510079666  # `0.0` означает, что задержка ниже точности `time.time()`.

>>> ping('not.exist.com')  # Если хост неизвестен (не удалось разрешить), возвращает False.
False

>>> ping("224.0.0.0")  # Если истекло время ожидания (нет ответа), возвращает None.
None

>>> ping("2600:1406:bc00:53::b81e:94ce")  # Пинг IPv6-адреса.
0.215697261510079666  # Возвращает задержку в секундах.

>>> ping('example.com', version=6)  # Принудительный пинг по IPv6. 4 для IPv4, 6 для IPv6. По умолчанию None (автоопределение).
0.215697261510079666

>>> ping('example.com', timeout=10)  # Установить таймаут 10 секунд. По умолчанию 4 секунды.
0.215697261510079666

>>> ping('example.com', unit='ms')  # Возвращает задержку в миллисекундах. По умолчанию 's' (секунды).
215.9627876281738

>>> ping('example.com', src_addr='192.168.1.15')  # Задать исходный IP-адрес для множественных интерфейсов. По умолчанию None (без привязки).
0.215697261510079666

>>> ping('example.com', interface='eth0')  # ТОЛЬКО ДЛЯ LINUX. Задать исходный сетевой интерфейс. По умолчанию None (без привязки).
0.215697261510079666

>>> ping('example.com', ttl=5)  # Установить TTL пакета равным 5. Пакет отбрасывается, если не достигает цели за 5 прыжков. По умолчанию 64.
None

>>> ping('example.com', size=56)  # Установить полезную нагрузку ICMP-пакета 56 байт. Общий размер пакета: 8 (заголовок) + 56 (данные) = 64 байта. По умолчанию 56.
0.215697261510079666

>>> verbose_ping('example.com')  # Пинг 4 раза подряд.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', timeout=10)  # Установить таймаут 10 секунд. По умолчанию 4 секунды.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', count=6)  # Пинг 6 раз. По умолчанию 4.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms

>>> verbose_ping('example.com', count=0)  # Бесконечный пинг (0 — бесконечные повторения). Остановить вручную: `ctrl + c`.
ping 'example.com' ... 215ms
...

>>> verbose_ping('example.com', src_addr='192.168.1.15')  # Пинг с указанного исходного IP для множественных интерфейсов. По умолчанию None.
ping 'example.com' from '192.168.1.15' ... 215ms
ping 'example.com' from '192.168.1.15' ... 216ms
ping 'example.com' from '192.168.1.15' ... 219ms
ping 'example.com' from '192.168.1.15' ... 217ms

>>> verbose_ping('example.com', interface='wifi0')  # ТОЛЬКО LINUX. Пинг через сетевой интерфейс 'wifi0'. По умолчанию None.
ping 'example.com' from '192.168.1.15' ... 215ms
ping 'example.com' from '192.168.1.15' ... 216ms
ping 'example.com' from '192.168.1.15' ... 219ms
ping 'example.com' from '192.168.1.15' ... 217ms

>>> verbose_ping('example.com', unit='s')  # Отображать задержку в секундах. По умолчанию "ms" (миллисекунды).
ping 'example.com' ... 1s
ping 'example.com' ... 2s
ping 'example.com' ... 1s
ping 'example.com' ... 1s

>>> verbose_ping('example.com', ttl=5)  # Установить TTL равным 5. По умолчанию 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout

>>> verbose_ping('example.com', interval=5)  # Ждать 5 секунд между пакетами. По умолчанию 0.
ping 'example.com' ... 215ms  # ждать 5 сек
ping 'example.com' ... 216ms  # ждать 5 сек
ping 'example.com' ... 219ms  # ждать 5 сек
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', size=56)  # Установить полезную нагрузку ICMP 56 байт. По умолчанию 56.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

>>> verbose_ping('example.com', version=6)  # Принудительный пинг по IPv6. 4 для IPv4, 6 для IPv6. По умолчанию None (автоопределение).
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
```

### Режим DEBUG

Отображает дополнительную информацию для разработчиков.

```python
>>> import ping3
>>> ping3.DEBUG = True  # По умолчанию False.

>>> ping3.ping("example.com")  # "ping()" выводит полученный IP-заголовок и ICMP-заголовок.
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

### Режим EXCEPTIONS

Вызывает исключения при ошибках вместо возврата None.

```python
>>> import ping3
>>> ping3.EXCEPTIONS = True  # По умолчанию False.

>>> ping3.ping("example.com", timeout=0.0001)
[... Traceback ...]
ping3.errors.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

>>> ping3.ping("not.exist.com")
[... Traceback ...]
ping3.errors.HostUnknown: Cannot resolve: Unknown host. (Host = not.exist.com)

>>> ping3.ping("example.com", ttl=1)  # На Linux нужны права суперпользователя для получения TTL expired. На Windows TTL expired недоступен.
[... Traceback ...]
ping3.errors.TimeToLiveExpired: Time exceeded: Time To Live expired.

>>> try:
>>>     ping3.ping("example.com", ttl=1)
>>> except ping3.errors.TimeToLiveExpired as err:
>>>     print(err.ip_header["src_addr"])  # TimeToLiveExpired, DestinationUnreachable и DestinationHostUnreachable содержат ip_header и icmp_header.
1.2.3.4  # IP-адрес, на котором произошёл TTL expired.

>>> help(ping3.errors)  # Подробнее об исключениях.
```

```python
import ping3
ping3.EXCEPTIONS = True

try:
    ping3.ping("not.exist.com")
except ping3.errors.HostUnknown:  # Перехватывается конкретная ошибка.
    print("Host unknown error raised.")
except ping3.errors.PingError:  # Все ошибки ping3 являются подклассами `PingError`.
    print("A ping error raised.")
```

## Запуск из командной строки (terminal)

Запуск ping3 из командной строки.
Примечание: на некоторых платформах `ping3` требует прав суперпользователя для отправки/приёма пакетов. Используйте `sudo ping3`.

```sh
$ ping3 --help  # -h/--help. Справочное сообщение командной строки.
$ python -m ping3 --help  # То же, что `ping3`. `ping3` — псевдоним для `python -m ping3`.

$ ping3 --version  # -v/--version. Показать номер версии ping3.
3.0.0

$ ping3 example.com  # Подробный пинг.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 example.com 8.8.8.8  # Подробный пинг нескольких адресов.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms
ping '8.8.8.8' ... 5ms
ping '8.8.8.8' ... 2ms
ping '8.8.8.8' ... 6ms
ping '8.8.8.8' ... 5ms

$ ping3 --count 1 example.com  # -c/--count. Сколько пингов отправить. По умолчанию 4.
ping 'example.com' ... 215ms

$ ping3 --count 0 example.com  # Бесконечный пинг (0 — бесконечные повторения). Остановить вручную: `ctrl + c`.
ping 'example.com' ... 215ms
(*repeat*)

$ ping3 --timeout 10 example.com  # -t/--timeout. Установить таймаут 10 секунд. По умолчанию 4.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --ttl 5 example.com  # -T/--ttl. Установить TTL равным 5. По умолчанию 64.
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout
ping 'example.com' ... Timeout

$ ping3 --size 56 example.com  # -s/--size. Установить полезную нагрузку ICMP-пакета 56 байт. По умолчанию 56.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --interval 5 example.com  # -i/--interval. Ждать 5 секунд между пакетами. По умолчанию 0.
ping 'example.com' ... 215ms  # ждать 5 сек
ping 'example.com' ... 216ms  # ждать 5 сек
ping 'example.com' ... 219ms  # ждать 5 сек
ping 'example.com' ... 217ms

$ ping3 --interface eth0 example.com  # -I/--interface. ТОЛЬКО ДЛЯ LINUX. Сетевой интерфейс шлюза для пинга. По умолчанию None.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --src 192.168.1.15 example.com  # -S/--src. Пинг с указанного исходного IP для множественных сетевых интерфейсов. По умолчанию None.
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 -4 example.com  # -4/--ipv4. Принудительный пинг по IPv4. По умолчанию None (автоопределение).
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 -6 example.com  # -6/--ipv6. Принудительный пинг по IPv6. По умолчанию None (автоопределение).
ping 'example.com' ... 215ms
ping 'example.com' ... 216ms
ping 'example.com' ... 219ms
ping 'example.com' ... 217ms

$ ping3 --exceptions --timeout 0.001 example.com  # -E/--exceptions. Режим EXCEPTIONS включается при указании этого флага.
[... Traceback ...]
ping3.errors.Timeout: Request timeout for ICMP packet. (Timeout = 0.0001s)

$ ping3 --debug --timeout 0.001 example.com  # -D/--debug. Режим DEBUG включается при указании этого флага.
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
[DEBUG] Request timeout for ICMP packet. (Timeout = 0.001s)
ping 'example.com' ... Timeout > 0.001s
```
