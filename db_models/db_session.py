import os
from pathlib import Path

import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file: str) -> None:
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("DB file is not specified")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting to DB on {conn_str}")

    engine = sa.create_engine(conn_str, echo=False, pool_size=20, max_overflow=-1)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


def dictionary_init(path: str, file: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(path + "/" + file):
        open(path + "/" + file, "w", encoding="utf-8")
