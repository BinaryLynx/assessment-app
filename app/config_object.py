from app.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class DevConfig:
    """Development configuration."""

    DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
