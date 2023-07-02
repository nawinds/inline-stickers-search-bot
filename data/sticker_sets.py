import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class StickerSet(SqlAlchemyBase):
    __tablename__ = 'sticker_sets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer)
    default = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    search_data = relationship("SearchData", back_populates="set")
    user_sets = relationship("UserSet", back_populates="set")
    set_links = relationship("SetLink", back_populates="set")
