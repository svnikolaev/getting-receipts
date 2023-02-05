import datetime
from abc import ABC
from dataclasses import dataclass


@dataclass(slots=False)
class AbstractModel(ABC):
    pass


@dataclass(slots=False)
class SessionToken(AbstractModel):
    refresh_token: str
    session_id: str | None = None
    id: int | None = None
    time_created: datetime.datetime | None = datetime.datetime.now()
    obtained_using_code: bool = False
