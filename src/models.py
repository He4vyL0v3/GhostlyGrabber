import sqlite3
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship

from utils import adapt_datetime, convert_datetime

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


class Base(DeclarativeBase):
    pass


def create_models(channel_name: str):
    table_name = f"posts_{channel_name.replace('@', '').replace('-', '_')}"
    discussion_table_name = (
        f"discussions_{channel_name.replace('@', '').replace('-', '_')}"
    )

    class TelegramUser(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, index=True)
        first_name = Column(String, nullable=True)
        last_name = Column(String, nullable=True)
        phone = Column(String, nullable=True)

    class TelegramPost(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True)
        post_id = Column(Integer, index=True)
        text = Column(Text)
        media_path = Column(String)
        date = Column(DateTime)
        views = Column(Integer, nullable=True)
        forwards = Column(Integer, nullable=True)
        username = Column(String, ForeignKey("users.username"), nullable=True)
        user = relationship("TelegramUser")

    class Discussion(Base):
        __tablename__ = discussion_table_name
        id = Column(Integer, primary_key=True)
        message_id = Column(Integer, index=True)
        post_id = Column(Integer, ForeignKey(f"{table_name}.post_id"))
        text = Column(Text)
        date = Column(DateTime)
        username = Column(String, ForeignKey("users.username"))
        user = relationship("TelegramUser")
        media_path = Column(String, nullable=True)

    return TelegramUser, TelegramPost, Discussion
