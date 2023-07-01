import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Sticker(SqlAlchemyBase):
    __tablename__ = 'stickers'
    sticker_unique_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True,
                                          unique=True, index=True)
    sticker_file_id = sqlalchemy.Column(sqlalchemy.String)

    search_data = relationship("SearchData", back_populates="sticker")
