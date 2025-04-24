import datetime
import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey('users.id'),
                                nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    test_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    criteria = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    questions = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    owner = relationship('User', back_populates='questions')

    def to_dict(self, only=None):
        result = {}
        if only:
            for key in only:
                value = getattr(self, key)
                if isinstance(value, datetime.datetime):
                    result[key] = value.strftime(
                        '%d.%m.%Y %H:%M')  # например: "24.04.2025 13:30"
                else:
                    result[key] = value
        else:
            for column in self.__table__.columns:
                value = getattr(self, column.name)
                if isinstance(value, datetime.datetime):
                    result[column.name] = value.strftime('%d.%m.%Y %H:%M')
                else:
                    result[column.name] = value
        return result
