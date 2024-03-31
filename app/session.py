import os
from contextlib import contextmanager

from flask import current_app, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionSQLA
from sqlalchemy.pool import NullPool

session_maker = sessionmaker()


@contextmanager
def session_scope(session: SessionSQLA = session_maker) -> SessionSQLA:
    """Provide a transactional scope around a series of operations."""

    if os.getenv("FLASK_DEBUG"):
        db_uri = current_app.config.get("DB_URI", "")
        echo = True
    else:
        db_uri = current_app.config.get("DB_URI", "").format(request.environ["REMOTE_USER"])
        echo = False
    session.configure(bind=create_engine(db_uri, client_encoding="utf8", poolclass=NullPool, echo=echo))
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


class Session:
    """Сессия с бд."""

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = sessionmaker()
        if "FLASK_DEBUG" in os.environ:
            db_uri = current_app.config.get("DB_URI", "")
            echo = True
        else:
            db_uri = current_app.config.get("DB_URI", "").format(request.environ["REMOTE_USER"])
            echo = False
        session.configure(
            bind=create_engine(db_uri, client_encoding="utf8", poolclass=NullPool, echo=echo)
        )
        # session.configure(bind=create_engine(db_uri, poolclass=NullPool, echo=echo)) # для sqlite
        sess = session()
        sess.begin()
        try:
            # sess.execute('pragma foreign_keys=on')
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()
