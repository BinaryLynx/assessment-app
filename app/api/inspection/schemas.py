from flask_restx import Model, fields
from marshmallow import fields as mfields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested

from app.common.common_data import TimeFormat
from app.common.models import DirectionResult, Grade, InspectionResult, TopicResult


user_schema_in = Model(
    "UserIn",
    {
        "first_name": fields.String(required=True, description="Имя."),
        "last_name": fields.String(required=True, description="Фамилия."),
        "middle_name": fields.String(required=True, description="Отчество."),
    },
)

topic_result_schema_in = Model(
    "TopicResultIn",
    {
        "grade": fields.Float(required=True, description="Оценка по проверке."),
        "topic_id": fields.String(required=True, description="ID поднаправления.", default="1"),
        "description": fields.String(required=False, description="Описание/результат проверки."),
    },
)

direction_result_schema_in = Model(
    "DirectionResultIn",
    {
        "grade": fields.Float(required=False, description="Оценка по направлению."),
        "direction_id": fields.String(required=True, description="ID направления.", default="1"),
        "description": fields.String(required=False, description="Описание"),
        "topic_results": fields.List(fields.Nested(topic_result_schema_in)),
    },
)

inspection_result_schema_in = Model(
    "InspectionResultIn",
    {
        "name": fields.String(required=True, description="Название проверки."),
        "grade": fields.Float(required=False, description="оценка по проверке."),
        "description": fields.String(required=False, description="Описание/результат проверки."),
        "direction_results": fields.List(fields.Nested(direction_result_schema_in)),
        "inspection_organ_id": fields.String(required=True, description="Проверяющий орган.", default="1"),
        "inspection_target_id": fields.String(required=True, description="Проверяемый субъект.", default="1"),
        "operator_id": fields.String(required=True, description="Оператор проверки.", default="1"),
        "inspection_date": TimeFormat(
            required=True, description="Дата и время проведения проверки.", default="2024-03-31T19:25:41.110084"
        ),
        "files": fields.List(fields.String, description="Список путей к файлам.", default="[]"),
    },
)

topic_result_schema_out = Model(
    "TopicResultOut",
    {
        "grade": fields.Float(required=False, description="Оценка по проверке."),
        "topic_name": fields.String(required=True, description="Название поднаправления."),
        "description": fields.String(required=False, description="Описание/результат проверки."),
    },
)

direction_result_schema_out = Model(
    "DirectionResultOut",
    {
        "grade": fields.Float(required=False, description="Оценка по направлению."),
        "direction_name": fields.String(required=True, description="Название направления."),
        "description": fields.String(required=False, description="Описание"),
        "topic_results": fields.List(fields.Nested(topic_result_schema_out)),
    },
)

inspection_result_schema_out = Model(
    "InspectionResultOut",
    {
        "id": fields.String(description="ID проверки."),
        "name": fields.String(description="Название проверки."),
        "grade": fields.Float(description="Оценка по проверке."),
        "description": fields.String(description="Описание/результат проверки."),
        "direction_results": fields.List(fields.Nested(direction_result_schema_out)),
        "inspection_organ_id": fields.String(description="Проверяющий орган."),
        "inspection_target_id": fields.String(description="Проверяемый субъект."),
        "operator_id": fields.String(description="Оператор проверки."),
        "created_date": TimeFormat(
            readonly=True, description="Дата и время проведения проверки.", example="2024/03/29 01:01"
        ),
        "updated_date": TimeFormat(
            readonly=True, description="Дата и время изменения внесенных данных.", example="2024/03/29 01:01"
        ),
        "inspection_date": TimeFormat(
            readonly=True, description="Дата и время проведения проверки.", example="2024/03/29 01:01"
        ),
        "files": fields.List(fields.String, description="Список путей к файлам."),
    },
)

grade_schema_out = Model(
    "GradeSchemaOut",
    {
        "id": fields.String,
        "name": fields.String,
    },
)

grade_schema_in = Model(
    "GradeSchemaIn",
    {
        "name": fields.String,
    },
)


class GradeSchema(SQLAlchemyAutoSchema):
    """Автосхема оценок."""

    class Meta:
        model = Grade
        include_fk = True


class TopicResultSchema(SQLAlchemyAutoSchema):
    """Автосхема результата проверки по поднаправлению."""

    # grade = mfields.String(dump_only=True, attribute="grade.name")
    topic_name = mfields.String(dump_only=True, attribute="topic.name")

    class Meta:
        model = TopicResult
        include_fk = True


class DirectionResultSchema(SQLAlchemyAutoSchema):
    """Автосхема результата проверки по направлению."""

    # grade = mfields.String(dump_only=True, attribute="grade.name")
    direction_name = mfields.String(dump_only=True, attribute="direction.name")
    topic_results = Nested(TopicResultSchema(), many=True)

    class Meta:
        model = DirectionResult
        include_fk = True


class InspectionResultSchema(SQLAlchemyAutoSchema):
    """Автосхема инспекторской проверки."""

    # grade = mfields.String(dump_only=True, attribute="grade.name")
    direction_results = Nested(DirectionResultSchema(), many=True, dump_only=True)

    class Meta:
        model = InspectionResult
        include_fk = True
