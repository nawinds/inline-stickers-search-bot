import sqlalchemy
from .db_session import SqlAlchemyBase


class StickerSetsData(SqlAlchemyBase):
    __tablename__ = 'sticker_sets_data'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    set_id = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    sticker_id = sqlalchemy.Column(sqlalchemy.Integer)
