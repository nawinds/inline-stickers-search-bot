import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship
from string import ascii_uppercase, ascii_lowercase
from random import choice


def generate_code():
    alphabet = ascii_lowercase + ascii_uppercase + "0123456789"
    return "".join([choice(alphabet) for i in range(10)])


class SetLink(SqlAlchemyBase):
    __tablename__ = 'set_links'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, unique=True, autoincrement=True, index=True)
    set_id = sqlalchemy.Column(sqlalchemy.ForeignKey('sticker_sets.id'))
    code = sqlalchemy.Column(sqlalchemy.String, default=generate_code())
    notifications = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    set = relationship("StickerSet", back_populates="set_links")
