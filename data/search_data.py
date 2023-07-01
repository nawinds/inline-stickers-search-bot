import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class SearchData(SqlAlchemyBase):
    __tablename__ = 'search_data'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sticker_unique_id = sqlalchemy.Column(sqlalchemy.ForeignKey('stickers.sticker_unique_id'))
    keyword = sqlalchemy.Column(sqlalchemy.String, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    sticker = relationship("Sticker", back_populates="search_data")
