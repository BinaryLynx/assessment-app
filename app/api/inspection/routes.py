from flask_restx import Namespace, Resource, reqparse

from app.api.inspection.schemas import (
    direction_result_schema_in,
    direction_result_schema_out,
    grade_schema_in,
    grade_schema_out,
    inspection_result_schema_in,
    inspection_result_schema_out,
    topic_result_schema_in,
    topic_result_schema_out,
    user_schema_in,
)
from app.api.inspection.service import InspectionResultService, StrategyCriteria

inspection_api = Namespace("Результаты инспекционных проверок")
inspections_api = Namespace("Результаты инспекционных проверок")

inspection_api.models[inspection_result_schema_in.name] = inspection_result_schema_in
inspection_api.models[inspection_result_schema_out.name] = inspection_result_schema_out
inspection_api.models[user_schema_in.name] = user_schema_in
inspection_api.models[topic_result_schema_in.name] = topic_result_schema_in
inspection_api.models[direction_result_schema_in.name] = direction_result_schema_in
inspection_api.models[direction_result_schema_out.name] = direction_result_schema_out
inspection_api.models[topic_result_schema_out.name] = topic_result_schema_out
inspection_api.models[grade_schema_out.name] = grade_schema_out
inspection_api.models[grade_schema_in.name] = grade_schema_in


@inspection_api.route("/inspections/<inspection_id>/")
@inspection_api.param("inspection_id", "ID инспекторской проверки")
@inspection_api.response(500, "Не найдено")
class InspectionResultRoute(Resource):
    """Класс для работы с результатами инспекционных проверок по ID."""

    @inspection_api.marshal_with(inspection_result_schema_out)
    def get(self, inspection_id: str):
        """Получение информации об инспекторской проверке по ID."""

        result = InspectionResultService.get_info(inspection_id)
        return result

    @inspections_api.marshal_with(inspection_result_schema_out)
    def delete(self, inspection_id: str):
        """Удаление информации об инспекторской проверке из БД по ID."""

        result = InspectionResultService.delete_from_db(inspection_id)
        return result

    @inspection_api.expect(inspection_result_schema_in)
    @inspection_api.marshal_with(inspection_result_schema_out)
    def put(self, inspection_id: str):
        """Обновление информации об инспекторской проверке в БД по ID."""

        result = InspectionResultService.update_in_db(inspection_id, inspection_api.payload)
        return result


@inspections_api.route("/inspections/")
@inspections_api.response(500, "Не найдено")
class InspectionsResultRoute(Resource):
    """Класс для работы с результатами инспекционных проверок."""

    @inspections_api.expect(inspection_result_schema_in)
    @inspections_api.marshal_with(inspection_result_schema_out)
    def post(self):
        """Сохранение информации об инспекторской проверке в БД."""

        # Плейсхолдер для логики определения стратегии (взять информацию из запроса/из бд).
        strategy = StrategyCriteria()

        result = InspectionResultService(inspections_api.payload, strategy).write_to_db()
        return result

    @inspections_api.param("limit", "Количество записей", default=10, type=int)
    @inspections_api.param("offset", "Смещение", default=0, type=int)
    @inspections_api.param("name", "Поиск на названию проверки", type=str)
    @inspections_api.param("grade", "Поиск по оценке", type=str)
    @inspections_api.param("date", "Поиск по дате проверки", type=int)
    @inspections_api.param("start_date", "Поиск по диапазону от введенной даты включительно", type=int)
    @inspections_api.param("end_date", "Поиск по диапазону до введенной даты включительно", type=int)
    @inspections_api.param("inspection_organ_id", "Поиск по органу проверки", type=str)
    @inspections_api.param("inspection_target_id", "Поиск по объекту проверки", type=str)
    @inspections_api.param("direction_id", "Поиск по направлению проверки", type=str)
    @inspections_api.param("description", "Поиск по описанию проверки", type=str)
    @inspections_api.marshal_with(inspection_result_schema_out)
    def get(self):
        """Получение информации об инспекторских проверках."""

        parser = reqparse.RequestParser()
        parser.add_argument("limit", required=False, type=int)
        parser.add_argument("offset", required=False, type=int)
        parser.add_argument("name", required=False, type=str)
        parser.add_argument("grade", required=False, type=str)
        parser.add_argument("inspection_organ_id", required=False, type=str)
        parser.add_argument("inspection_target_id", required=False, type=str)
        parser.add_argument("date", required=False, type=int)
        parser.add_argument("start_date", required=False, type=int)
        parser.add_argument("end_date", required=False, type=int)
        parser.add_argument("direction_id", required=False, type=str)
        parser.add_argument("description", required=False, type=str)
        limit = parser.parse_args().get("limit")
        offset = parser.parse_args().get("offset")
        name_filter = parser.parse_args().get("name")
        grade_filter = parser.parse_args().get("grade")
        inspection_organ_id_filter = parser.parse_args().get("inspection_organ_id")
        inspection_target_id_filter = parser.parse_args().get("inspection_target_id")
        date_filter = parser.parse_args().get("date")
        start_date_filter = parser.parse_args().get("start_date")
        end_date_filter = parser.parse_args().get("end_date")
        direction_id_filter = parser.parse_args().get("direction_id")
        description_filter = parser.parse_args().get("description")
        result = InspectionResultService.get_inspections(
            limit,
            offset,
            name_filter,
            grade_filter,
            inspection_organ_id_filter,
            inspection_target_id_filter,
            date_filter,
            start_date_filter,
            end_date_filter,
            direction_id_filter,
            description_filter,
        )
        return result, 200 if result or result == [] else inspections_api.abort(500)


@inspections_api.route("/inspections/all/")
@inspections_api.response(500, "Не найдено")
class LatestResultRoute(Resource):
    @inspections_api.param("inspection_target_id", "Поиск по объекту проверки")
    @inspections_api.marshal_with(topic_result_schema_in)
    def get(self):
        """Вывод информации последних результатов по всем направлениям проверки для конкретного инспектируемого объекта."""

        parser = reqparse.RequestParser()
        parser.add_argument("inspection_target_id", required=True, type=str)
        inspection_target_id = parser.parse_args().get("inspection_target_id")
        result = InspectionResultService.get_overall_results_by_inspection_target_id(inspection_target_id)

        return result, 200 if result or result == [] else inspections_api.abort(500)
