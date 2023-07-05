import sqlalchemy
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class UserSet(SqlAlchemyBase):
    __tablename__ = 'user_sets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True, autoincrement=True, index=True)
    set_id = sqlalchemy.Column(sqlalchemy.ForeignKey('sticker_sets.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

    set = relationship("StickerSet", back_populates="user_sets")
