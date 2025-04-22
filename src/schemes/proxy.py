from pydantic import BaseModel

from constants.prox_type import ProxyType


class Proxy(BaseModel):
    type: ProxyType
    link: str
    user: str | None = None
    pwd: str | None = None
