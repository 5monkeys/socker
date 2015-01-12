# socker
Redis pub/sub websocket proxy server, built on asyncio.

## Installation

socker is not on PyPI, so you'll have to run
```bash
pip install -e 'git+http://github.com/5monkeys/socker.git#egg=socker'
```
in order to use it.

## Usage

```bash
$ socker -h
Start the socker websocket server

Usage:
  socker [options]
  socker -? | --help
  socker --version

Options:
  -i INTERFACE    Listening interface [default: localhost]
  -p PORT         Listening port [default: 8765]

  -v              Enable verbose output

  --redis-host=HOST             Redis host [default: localhost]
  --redis-port=PORT             Redis port [default: 6379]
  --redis-db=DB                 Redis database [default: 0]
  --redis-password=PASSWORD     Redis password

  --logto FILE    Log output to FILE instead of console

  --version       show version
  -? --help       Show this screen
```

## Thanks

Thanks to

- https://github.com/aaugustin/websockets
- https://github.com/jonathanslenders/asyncio-redis

for their brilliant asyncio packages.
