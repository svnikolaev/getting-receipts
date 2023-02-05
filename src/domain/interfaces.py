from dataclasses import dataclass

from src.adapters.gateways import AbstractGateway
from src.adapters.gateways import ReceiptBase as ReceiptGateway
from src.adapters.repositories import (AbstractRepository,
                                       SessionTokensRepository)


@dataclass(slots=False)
class AbstractContext():
    client: AbstractGateway
    repo: AbstractRepository


@dataclass(slots=False)
class ReceiptContext(AbstractContext):
    client: ReceiptGateway
    repo: SessionTokensRepository
