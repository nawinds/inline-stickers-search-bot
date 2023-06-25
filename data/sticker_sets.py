import sqlalchemy
from .db_session import SqlAlchemyBase


class StickerSet(SqlAlchemyBase):
    __tablename__ = 'sticker_sets'

    set_id = sqlalchemy.Column(sqlalchemy.Integer,
                               primary_key=True, unique=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer)
