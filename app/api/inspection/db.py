from datetime import datetime
from typing import Dict, List

from sqlalchemy import delete, func, select
from sqlalchemy.orm import joinedload

from app.api.inspection.schemas import GradeSchema, InspectionResultSchema, TopicResultSchema
from app.common.common_data import save_file
from app.common.models import (
    DirectionResult,
    Grade,
    GradeCriteriaDirection,
    GradeCriteriaTopic,
    InspectionResult,
    InspectionTarget,
    InspectionTargetType,
    InspectionTargetTypeDirectionRel,
    InspectionTargetTypeTopicRel,
    Scale,
    Topic,
    TopicResult,
)
from app.session import session_scope
from sqlalchemy.dialects.postgresql import array


class InspectionDB:
    """Класс для работы с инспекторскими проверками."""

    @staticmethod
    def get_inspections(
        limit: int,
        offset: int,
        name_filter: str,
        grade_filter: str,
        inspection_organ_id_filter: str,
        inspection_target_id_filter: str,
        date_unix_filter: int,
        start_date_unix_filter: int,
        end_date_unix_filter: int,
        direction_id_filter: str,
        description_filter: str,
    ) -> List[Dict]:
        """
        Получение инспекторских проверок.

        :param limit: Количество записей
        :param offset: Смещение
        :param name_filter: Параметр для поиска по названию
        :param grade_filter: Параметр для поиска по оценке
        :param inspection_organ_id_filter: Параметр для поиска по органу проверки
        :param inspection_target_id_filter: Параметр для поиска по объекту проверки
        :param date_unix_filter: Параметр для поиска по конкретной дате
        :param start_date_unix_filter: Параметр для поиска по диапазону от выбранной даты
        :param end_date_unix_filter: Параметр для поиска по диапазону до выбранной даты
        :param direction_id_filter: Параметр для поиска по направлению проверки
        :param description_filter: Параметр для поиска по описанию проверки
        :return: Информация об инспекторских проверках в формате List[Dict]
        """

        with session_scope() as session:
            query = (
                select(InspectionResult)
                .limit(limit)
                .offset(offset)
                .filter(InspectionResult.name.ilike(f"%{name_filter}%" if name_filter is not None else "%"))
                .filter(
                    InspectionResult.description.ilike(
                        f"%{description_filter}%" if description_filter is not None else "%"
                    )
                )
                .filter(InspectionResult.grade == grade_filter if grade_filter is not None else True)
                .filter(
                    InspectionResult.inspection_organ_id == inspection_organ_id_filter
                    if inspection_organ_id_filter is not None
                    else True
                )
                .filter(
                    InspectionResult.inspection_target_id == inspection_target_id_filter
                    if inspection_target_id_filter is not None
                    else True
                )
                .options(
                    joinedload(InspectionResult.direction_results)
                    .joinedload(DirectionResult.topic_results)
                    .joinedload(TopicResult.topic)
                )
                .order_by(InspectionResult.created_date.desc())
            )
            if direction_id_filter:
                query = query.filter(
                    InspectionResult.direction_results.any(DirectionResult.direction_id == direction_id_filter)
                )
            if date_unix_filter:
                date_filter = datetime.utcfromtimestamp(date_unix_filter).date()
                query = query.filter(func.date(InspectionResult.created_date) == date_filter)
            if start_date_unix_filter and end_date_unix_filter:
                start_date_filter = datetime.utcfromtimestamp(start_date_unix_filter).date()
                end_date_filter = datetime.utcfromtimestamp(end_date_unix_filter).date()
                query = query.filter(
                    func.date(InspectionResult.created_date).between(start_date_filter, end_date_filter)
                )
            elif start_date_unix_filter:
                start_date_filter = datetime.utcfromtimestamp(start_date_unix_filter).date()
                query = query.filter(func.date(InspectionResult.created_date) >= start_date_filter)
            elif end_date_unix_filter:
                end_date_filter = datetime.utcfromtimestamp(end_date_unix_filter).date()
                query = query.filter(func.date(InspectionResult.created_date) <= end_date_filter)
            result = session.execute(query).unique().scalars().all()
            return InspectionResultSchema(many=True).dump(result)

    @staticmethod
    def get_by_id(inspection_id: str) -> InspectionResult:
        """
        Получение информации об инспекторской проверке по ID.

        :param inspection_id: ID инспекторской проверки
        :return: Информация об инспекторской проверке в формате Dict
        """

        with session_scope() as session:
            query = (
                (
                    session.execute(
                        select(InspectionResult)
                        .filter_by(id=inspection_id)
                        .options(
                            joinedload(InspectionResult.direction_results)
                            .joinedload(DirectionResult.topic_results)
                            .joinedload(TopicResult.topic)
                        )
                    )
                )
                .unique()
                .scalar_one_or_none()
            )
            return InspectionResultSchema(many=False).dump(query)

    @staticmethod
    def delete_inspection_by_id(inspection_id: str) -> InspectionResult:
        """
        Удаление сущности из БД по ID.

        :param inspection_id: ID инспекторской проверки
        :return: Удаленная запись
        """

        with session_scope() as session:
            query = session.execute(
                select(InspectionResult).where(InspectionResult.id == inspection_id)
            ).scalar_one_or_none()
            if query is not None:
                session.execute(delete(InspectionResult).where(InspectionResult.id == inspection_id))
                return query

    @staticmethod
    def write_inspection_into_db(payload) -> InspectionResult:
        """
        Добавление записи об инспекторской проверке в БД.

        :param payload: Данные об инспекторской проверки
        :return: Информация о добавленной инспекторской проверке
        """

        with session_scope() as session:
            new_inspection = InspectionResult(
                name=payload.name,
                grade=payload.grade,
                description=payload.description,
                inspection_organ_id=payload.inspection_organ_id,
                inspection_target_id=payload.inspection_target_id,
                inspection_date=payload.inspection_date,
                operator_id=payload.operator_id,
            )
            if payload.files:
                new_inspection.files = [save_file(file) for file in payload.files]
            session.add(new_inspection)
            for direction_data in payload.direction_results:
                direction = DirectionResult(
                    grade=direction_data.grade,
                    description=direction_data.description,
                    direction_id=direction_data.id,
                    inspection_result=new_inspection,
                )
                for topic_data in direction_data.topic_results:
                    topic = TopicResult(
                        grade=topic_data.grade,
                        description=topic_data.description,
                        topic_id=topic_data.id,
                        direction_result=direction,
                    )
                    session.add(topic)
                session.add(direction)
        return new_inspection

    @staticmethod
    def update_inspection_in_db(inspection_id: str, payload: Dict) -> InspectionResult:
        """
        Обновление записи об инспекторской проверке в БД по ID.

        :param inspection_id: ID инспекторской проверки
        :param payload: Обновленные данные об инспекторской проверке
        :return: Обновленная информация об инспекторской проверке
        """

        with session_scope() as session:
            inspection = session.query(InspectionResult).filter_by(id=inspection_id).first()
            inspection.name = payload.get("name", inspection.name)
            inspection.grade = payload.get("grade", inspection.grade)
            inspection.description = payload.get("description", inspection.description)
            inspection.inspection_organ_id = payload.get("inspection_organ_id", inspection.inspection_organ_id)
            inspection.inspection_target_id = payload.get("inspection_target_id", inspection.inspection_target_id)
            inspection.operator_id = payload.get("operator_id", inspection.operator_id)

            new_dir_results = payload.get("direction_results", [])
            for dir_result in inspection.direction_results:
                session.delete(dir_result)

            for new_dir in new_dir_results:
                dir_result = DirectionResult(
                    grade=new_dir.get("grade"),
                    description=new_dir.get("description"),
                    direction_id=new_dir.get("direction_id"),
                    inspection_result=inspection,
                )

                for new_topic in new_dir.get("topic_results", []):
                    topic_result = TopicResult(
                        grade=new_topic.get("grade"),
                        description=new_topic.get("description"),
                        topic_id=new_topic.get("topic_id"),
                        direction_result=dir_result,
                    )
                    dir_result.topic_results.add(topic_result)
                inspection.direction_results.add(dir_result)
            inspection.updated_date = datetime.now()
            return inspection

    @staticmethod
    def get_overall_results_by_inspection_target_id(inspection_target_id: str):
        """
        Получить последний результат по каждому поднаправлению для inspection_target.

        :param inspection_target_id: ID inspection_target
        :return: Список результатов
        """

        with session_scope() as session:
            # Эта часть на случай если нужно будет возвращать все поднаправления (даже без оценки)
            inspection_target_type = (
                select(InspectionTargetType)
                .join(InspectionTarget)
                .where(InspectionTarget.id == inspection_target_id)
                .cte("inspection_target_type")
            )
            topics_for_target_type = (
                select(Topic)
                .join(InspectionTargetTypeTopicRel)
                .join(inspection_target_type)
                .cte("topics_for_target_type")
            )
            # Основные запросы
            topic_results_with_date = (
                select(TopicResult, InspectionResult.created_date)
                .join(DirectionResult, TopicResult.direction_result)
                .join(InspectionResult)
                # .join(topics_for_target_type)
                .cte("topic_results_with_date")
            )
            latest_result_dates = (
                select(
                    topic_results_with_date.c.topic_id,
                    func.max(topic_results_with_date.c.created_date).label("created_date"),
                )
                .group_by(topic_results_with_date.c.topic_id)
                .cte("latest_result_dates")
            )
            latest_results = (
                select(TopicResult)
                .join(topic_results_with_date, TopicResult.id == topic_results_with_date.c.id)
                .join(
                    latest_result_dates,
                    (latest_result_dates.c.topic_id == topic_results_with_date.c.topic_id)
                    & (latest_result_dates.c.created_date == topic_results_with_date.c.created_date),
                )
            )
            res = session.execute(latest_results).scalars().all()
            return TopicResultSchema(many=True).dump(res)


class InspectionTargetsDB:
    """Класс для работы с проверяемыми субъектами."""

    @staticmethod
    def update_inspection_target(inspection_target_id: str, payload: Dict) -> InspectionTarget:
        """
        Обновление проверяемого субъекта в БД по ID.

        :param inspection_target_id: ID проверяемого субъекта
        :param payload: Обновленная информация о проверяемом субъекте
        :return: Обновленная информация о проверяемом субъекте
        """

        with session_scope() as session:
            inspection_target = session.get(InspectionTarget, inspection_target_id)
            inspection_target.name = payload.get("name", inspection_target.name)
            return inspection_target

    @staticmethod
    def write_inspection_target_into_db(payload: Dict) -> InspectionTarget:
        """
        Сохранение информации о проверяемом субъекте в БД.

        :param payload: Информация о проверяемом субъекте
        :return: Сохраненная информация о проверяемом субъекте
        """

        with session_scope() as session:
            new_inspection_target = InspectionTarget(name=payload.get("name"))
            session.add(new_inspection_target)
        return new_inspection_target

    @staticmethod
    def delete_inspection_target_from_db(inspection_target_id: str) -> InspectionTarget:
        """
        Удаление проверяемого субъекта из БД по ID.

        :param inspection_target_id: ID проверяемого субъекта
        :return: Удаленная информация о проверяемом субъекте
        """

        with session_scope() as session:
            query = session.get(InspectionTarget, inspection_target_id)
            if query is not None:
                session.execute(delete(InspectionTarget).where(InspectionTarget.id == inspection_target_id))
                return query


class DirectionsDB:
    """Класс для работы с направлениями и поднаправлениями проверок."""

    @staticmethod
    def get_criteria_result_directions(direction_grades, inspection_target_id):
        direction_grades = [direction_grade for direction_grade in direction_grades if direction_grade[1] is not None]
        if not direction_grades:
            return []
        with session_scope() as session:

            subq = session.query(
                func.unnest(array([grade[0] for grade in direction_grades])).label("direction_id"),
                func.unnest(array([grade[1] for grade in direction_grades])).label("direction_grade"),
            ).subquery("arr")

            query = (
                select(GradeCriteriaDirection.direction_id, GradeCriteriaDirection.result_grade)
                .join(InspectionTargetTypeDirectionRel)
                .join(InspectionTargetType)
                .join(InspectionTarget)
                .join(
                    subq,
                    (subq.c.direction_id == GradeCriteriaDirection.direction_id)
                    & (subq.c.direction_grade == GradeCriteriaDirection.direction_grade),
                )
                .where((InspectionTarget.id == inspection_target_id))
            )
            res = session.execute(query).all()
            return res

    @staticmethod
    def get_criteria_result_topics(topic_grades, inspection_target_id):
        topic_grades = [topic_grade for topic_grade in topic_grades if topic_grade[1] is not None]
        if not topic_grades:
            return []
        with session_scope() as session:

            subq = session.query(
                func.unnest(array([grade[0] for grade in topic_grades])).label("topic_id"),
                func.unnest(array([grade[1] for grade in topic_grades])).label("topic_grade"),
            ).subquery("arr")

            query = (
                select(GradeCriteriaTopic.topic_id, GradeCriteriaTopic.result_grade)
                .join(InspectionTargetTypeTopicRel)
                .join(InspectionTargetType)
                .join(InspectionTarget)
                .join(
                    subq,
                    (subq.c.topic_id == GradeCriteriaTopic.topic_id)
                    & (subq.c.topic_grade == GradeCriteriaTopic.topic_grade),
                )
                .where((InspectionTarget.id == inspection_target_id))
            )
            res = session.execute(query).all()
            return res

    @staticmethod
    def get_topic_info_by_ids(topic_ids, inspection_target_id):

        with session_scope() as session:
            inspection_target_type = (
                select(InspectionTargetType)
                .join(InspectionTarget)
                .where(InspectionTarget.id == inspection_target_id)
                .cte()
            )
            query = select(InspectionTargetTypeTopicRel).join(
                inspection_target_type,
                (InspectionTargetTypeTopicRel.inspection_target_type_id == inspection_target_type.c.id)
                & (InspectionTargetTypeTopicRel.topic_id.in_(topic_ids)),
            )
            res = session.execute(query).scalars().all()
            return res

    @staticmethod
    def get_direction_info_by_ids(direction_ids, inspection_target_id):

        with session_scope() as session:
            inspection_target_type = (
                select(InspectionTargetType)
                .join(InspectionTarget)
                .where(InspectionTarget.id == inspection_target_id)
                .cte()
            )
            query = select(InspectionTargetTypeDirectionRel).join(
                inspection_target_type,
                (InspectionTargetTypeDirectionRel.inspection_target_type_id == inspection_target_type.c.id)
                & (InspectionTargetTypeDirectionRel.direction_id.in_(direction_ids)),
            )
            res = session.execute(query).scalars().all()
            return res
