import os
import random

from loguru import logger as _logger
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
from constants.prox_type import ProxyType
import socks
from schemes.proxy import Proxy

load_dotenv()


class Settings(BaseSettings):
    TG_TOKEN: str
    USE_PROXY: bool = False
    PROXY_LIST_FILE: str = "../proxies.txt"
    TEMP_DIR: str = "../temp"
    LOGS_FOLDER: str = "../logs"
    SESSION_DIR: str = '../sessions'
    LOGURU_LEVEL: str = "INFO"


settings = Settings()  # type: ignore


def PROXY_LIST() -> None | list[Proxy]:
    if settings.USE_PROXY:
        proxies: list[Proxy] = []

        with open(settings.PROXY_LIST_FILE, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                scheme, rest = line.split("://")
                host, port, pwd, user = rest.split(":")
                link = f"{host}:{port}"
                try:
                    proxy_type = ProxyType[scheme.upper()]
                except KeyError:
                    continue
                proxy = Proxy(type=proxy_type, link=link, user=user, pwd=pwd)
                proxies.append(proxy)
        return proxies
    return None


proxies = PROXY_LIST()


def GET_RANDOM_PROXY():
    if PROXY_LIST:
        _data = random.choice(proxies)
        host, port = _data.link.split(":")
        return socks.SOCKS5, host, int(port), True, _data.user, _data.pwd
    else:
        return None


os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.SESSION_DIR, exist_ok=True)

_logger.add(
    os.path.join(settings.LOGS_FOLDER, 'app-{time:YYYY-MM-DD-HH}.log'),
    filter=lambda record: record['extra'].get('name') == 'app',
    level=settings.LOGURU_LEVEL,
    rotation='10 MB',
    retention=50,
    colorize=True,
    backtrace=True
)

logger = _logger.bind(name='app')

print(f"SETTINGS PROXY USE {settings.USE_PROXY}")
