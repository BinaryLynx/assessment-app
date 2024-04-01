import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionSQLA
from sqlalchemy.pool import NullPool

from app.config_object import DevConfig


session_maker = sessionmaker()


@contextmanager
def session_scope(session: SessionSQLA = session_maker) -> SessionSQLA:
    """Provide a transactional scope around a series of operations."""
    session.configure(bind=create_engine(DevConfig.DB_URI, client_encoding="utf8", poolclass=NullPool))
    sess = session()
    sess.begin()
    sess.expire_on_commit = False
    try:
        yield sess
    except Exception:
        sess.rollback()
        raise
    else:
        sess.commit()
    finally:
        sess.close()
