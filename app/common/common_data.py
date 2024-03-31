import base64
import datetime
import os
import uuid

from flask_restx import fields


class TimeFormat(fields.Raw):
    """Класс для форматирования даты и времени."""

    __schema_type__ = ["string"]

    def format(self, value):
        if type(value) is not str:
            return datetime.datetime.strftime(value, "%Y/%m/%d %H:%M")
        dt_obj = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        return datetime.datetime.strftime(dt_obj, "%Y/%m/%d %H:%M")


def save_file(file_data) -> str:  # file path
    save_dir = "G:/media/"
    with open(file_data, "rb") as file:
        file_name = os.path.basename(file_data)
        new_file_name = uuid.uuid4().hex + "_" + file_name
        save_path = os.path.join(save_dir, new_file_name)
        with open(save_path, "wb") as save_file:
            save_file.write(file.read())
        return save_path
