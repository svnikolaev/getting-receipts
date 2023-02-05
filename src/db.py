from sqlalchemy import (Boolean, Column, DateTime, Integer, String, Table,
                        create_engine, func)
from sqlalchemy.orm import registry, sessionmaker

import src.domain.models as model
from src.utils import get_settings

S = get_settings()
DATABASE_URL = S.DATABASE_URL

VERBOSE = S.VERBOSE

# for SQLite
if 'sqlite' in DATABASE_URL:
    engine = create_engine(DATABASE_URL,
                           connect_args={'check_same_thread': False},
                           echo=VERBOSE)
else:
    engine = create_engine(DATABASE_URL,
                           echo=VERBOSE)
Session = sessionmaker(engine, autoflush=False)

mapper_registry = registry()

session_tokens = Table(
    'session_tokens',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, index=True),
    Column('time_created', DateTime(timezone=True), server_default=func.now()),
    Column('obtained_using_code', Boolean, default=False),
    Column('session_id', String),
    Column('refresh_token', String),
)


def start_mappers():
    mapper_registry.map_imperatively(model.SessionToken, session_tokens)


if __name__ == '__main__':
    mapper_registry.metadata.create_all(engine)
