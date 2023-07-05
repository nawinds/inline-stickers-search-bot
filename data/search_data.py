import sqlalchemy
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class SearchData(SqlAlchemyBase):
    __tablename__ = 'search_data'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sticker_unique_id = sqlalchemy.Column(sqlalchemy.ForeignKey('stickers.sticker_unique_id'))
    keyword = sqlalchemy.Column(sqlalchemy.String, index=True)
    set_id = sqlalchemy.Column(sqlalchemy.ForeignKey('sticker_sets.id'))

    sticker = relationship("Sticker", back_populates="search_data")
    set = relationship("StickerSet", back_populates="search_data")
