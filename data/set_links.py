import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class SetLink(SqlAlchemyBase):
    __tablename__ = 'set_links'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True, autoincrement=True, index=True)
    set_id = sqlalchemy.Column(sqlalchemy.ForeignKey('sticker_sets.id'))
    code = sqlalchemy.Column(sqlalchemy.String)
    notifications = sqlalchemy.Column(sqlalchemy.Boolean)

    set = relationship("StickerSet", back_populates="set_links")
