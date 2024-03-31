import os
from pathlib import Path

from flask_restx import Api

from app.api.inspection.routes import inspection_api, inspections_api

from app.app_factory import get_app

api = Api(
    title="Доступные маршруты",
    doc="/swagger/",
)

api.add_namespace(inspection_api, path="/api")
api.add_namespace(inspections_api, path="/api")
