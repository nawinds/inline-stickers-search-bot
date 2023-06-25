import sqlalchemy
from .db_session import SqlAlchemyBase


class SearchData(SqlAlchemyBase):
    __tablename__ = 'search_data'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sticker_id = sqlalchemy.Column(sqlalchemy.Integer)
    keyword = sqlalchemy.Column(sqlalchemy.String, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    use = sqlalchemy.Column(sqlalchemy.Float)
    sticker_count = sqlalchemy.Column(sqlalchemy.Integer)
