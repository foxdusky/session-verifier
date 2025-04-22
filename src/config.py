from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

from constants.prox_type import ProxyType
from schemes.proxy import Proxy

load_dotenv()


class Settings(BaseSettings):
    TG_TOKEN: str
    USE_PROXY: bool = False
    PROXY_LIST_FILE: str = "./proxies.txt"

    @property
    def PROXY_LIST(self) -> None | list[Proxy]:
        if self.USE_PROXY:
            proxies: list[Proxy] = []

            with open(self.PROXY_LIST_FILE, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    scheme, rest = line.split("://")
                    host, port, user, pwd = rest.split(":")
                    link = f"{host}:{port}"
                    try:
                        proxy_type = ProxyType[scheme.upper()]
                    except KeyError:
                        continue
                    proxy = Proxy(type=proxy_type, link=link, user=user, pwd=pwd)
                    proxies.append(proxy)
            return proxies
        return None


settings = Settings()  # type: ignore
