import os
import sqlite3

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models import Base, create_models


def init_db(path, channel_name):
    """
    Initialize the database and models.
    Args:
        path (str): Path to the folder where the database will be stored.
        channel_name (str): Name of the Telegram channel.
    Returns:
        tuple: (engine, Session, TelegramUser, PostModel, Discussion)
    """
    DB_NAME = os.path.join(os.path.abspath(path), "GhostlyGrabber.db")
    engine = create_engine(
        f"sqlite:///{DB_NAME}",
        connect_args={"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES},
    )
    telegram_user, post_model, discussion = create_models(channel_name)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return engine, session_factory, telegram_user, post_model, discussion


async def save_user(session, telegram_user, user):
    """
    Save or update a user in the database.
    Args:
        session: SQLAlchemy session object.
        telegram_user: SQLAlchemy user model.
        user: Telethon User object.
    Returns:
        str or None: Username if saved, otherwise None.
    """
    if not user.username:
        return None
    db_user = session.query(telegram_user).filter_by(username=user.username).first()
    if not db_user:
        db_user = telegram_user(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
        )
        session.add(db_user)
        session.commit()
    return db_user.username


def get_last_post_id(session, post_model):
    """
    Get the maximum post_id from the posts table.
    Args:
        session: SQLAlchemy session object.
        post_model: SQLAlchemy post model.
    Returns:
        int: Maximum post_id or 0 if none exists.
    """
    return session.query(func.max(post_model.post_id)).scalar() or 0


def get_existing_post(session, post_model, post_id):
    """
    Check if a post with the given post_id exists in the database.
    Args:
        session: SQLAlchemy session object.
        post_model: SQLAlchemy post model.
        post_id (int): ID of the post to check.
    Returns:
        post_model or None: The post if it exists, otherwise None.
    """
    return session.query(post_model).filter_by(post_id=post_id).first()


def add_post(session, post_model, **kwargs):
    """
    Add a new post to the database.
    Args:
        session: SQLAlchemy session object.
        post_model: SQLAlchemy post model.
        **kwargs: Fields for the post.
    Returns:
        post_model: The created post object.
    """
    post = post_model(**kwargs)
    session.add(post)
    session.commit()
    return post


def add_discussion(session, discussion_model, **kwargs):
    """
    Add a new discussion to the database.
    Args:
        session: SQLAlchemy session object.
        discussion_model: SQLAlchemy discussion model.
        **kwargs: Fields for the discussion.
    Returns:
        discussion_model: The created discussion object.
    """
    discussion = discussion_model(**kwargs)
    session.add(discussion)
    session.commit()
    return discussion
