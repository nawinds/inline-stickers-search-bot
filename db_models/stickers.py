import sqlalchemy
from sqlalchemy.orm import relationship

from db_models.db_session import SqlAlchemyBase


class Sticker(SqlAlchemyBase):
    __tablename__ = 'stickers'
    sticker_unique_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True,
                                          unique=True, index=True)
    sticker_file_id = sqlalchemy.Column(sqlalchemy.String)

    search_data = relationship("SearchData", back_populates="sticker")
