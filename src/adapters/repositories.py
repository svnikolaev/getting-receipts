from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import src.domain.models as model


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, Entity):
        raise NotImplementedError

    @abstractmethod
    def get(self, EntityType, entity_id):
        raise NotImplementedError

    def get_last(self, EntityType):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, Entity: object):
        self.session.add(Entity)

    def get(self, EntityType, entity_id: int) -> object:
        return self.session.query(EntityType).get(entity_id)


class SessionTokensRepository(SQLAlchemyRepository):
    def get_last(self, EntityType=model.SessionToken) -> model.SessionToken:
        return self.session.query(EntityType)\
            .order_by(EntityType.id.desc()).first()
