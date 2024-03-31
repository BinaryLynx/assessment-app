from flask import Flask

from app.config_object import DevConfig
from flask_cors import CORS


def get_app(config=DevConfig) -> Flask:
    """
    Get flask application.
    :param config:
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(config)
    app.config["RESTX_INCLUDE_ALL_MODELS"] = True
    CORS(app)

    from . import api

    api.init_app(app)

    return app
