import sqlalchemy
from .db_session import SqlAlchemyBase


class StickerSetsData(SqlAlchemyBase):
    __tablename__ = 'sticker_sets_data'

    set_id = sqlalchemy.Column(sqlalchemy.Integer,
                               primary_key=True, unique=True, index=True)
    sticker_id = sqlalchemy.Column(sqlalchemy.Integer)
