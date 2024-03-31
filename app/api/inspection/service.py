from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


from app.api.inspection.db import DirectionsDB, InspectionDB

from app.common.common_data import save_file


@dataclass
class Calculatable:
    is_ignored: bool = None
    grade: float = None
    is_critical: bool = None
    scale_max_value: float = None
    weight: float = None
    matched_result_grade: float = None


# @dataclass
# class CalculatableCritical(Calculatable):
#     grade: float
#     is_critical: bool


# @dataclass
# class CalculatableWeight(CalculatableCritical):
#     scale_max_value: float
#     weight: float


# @dataclass
# class CalculatableCriteria(Calculatable):
#     matched_result_grade: float


class GradeCalculationStrategy(ABC):
    @staticmethod
    @abstractmethod
    def calculate(items: List[Calculatable]):
        pass


class StrategyAVGCritical(GradeCalculationStrategy):
    @staticmethod
    def calculate(items: List[Calculatable]):
        if not items:
            # Ошибка - расчитать оценку нельзя
            return 0
        items = [item for item in items if not item.is_ignored]
        if not items:
            # Ошибка - расчитать оценку нельзя
            return 0

        avg = sum([item.grade for item in items]) / len(items)
        critical_items = [item.grade for item in items if item.is_critical]
        if not critical_items:
            result = avg
        else:
            result = min(avg, *critical_items)
        result = round(result, 2)
        return result


class StrategyWeights(GradeCalculationStrategy):
    @staticmethod
    def calculate(items: List[Calculatable]):
        if not items:
            # Ошибка - расчитать оценку нельзя
            return 0
        items = [item for item in items if not item.is_ignored]
        if not items:
            # Ошибка - расчитать оценку нельзя
            return 0

        max_possible_result = sum(
            [item.scale_max_value * item.weight for item in items]
        )  # максимальная оценка по пришедшим на проверку направлений
        actual_result = sum([item.grade * item.weight for item in items])  # оценка по пришедшим на проверку направлений
        actual_to_max_ratio = (
            actual_result / max_possible_result
        )  # процент от максимально возможной оценки по пришедшим на проверку направлениям
        result = actual_to_max_ratio * items[0].scale_max_value  # результат в требуемой шкале
        result = round(result, 2)
        return result


class StrategyCriteria(GradeCalculationStrategy):
    @staticmethod
    def calculate(items: List[Calculatable]):
        if not items:
            # Ошибка - расчитать оценку нельзя
            return 0
        res = min([item.matched_result_grade for item in items])
        return res


class TopicResult(Calculatable):
    def __init__(self, topic_result_payload):
        self.description = topic_result_payload.get("description")
        self.id = topic_result_payload.get("topic_id")
        self.grade = topic_result_payload.get("grade")
        # super().__init__(grade=topic_result_payload.get("grade"))

    def __repr__(self):
        return f"TopicResult({self.description}, {self.id}, {self.grade})"


class DirectionResult(Calculatable):
    def __init__(
        self,
        direction_result_payload,
        inspection_target_id,
        calculation_strategy=StrategyCriteria(),
    ):
        self.inspection_target_id = inspection_target_id
        self.description = direction_result_payload.get("description")
        self.id = direction_result_payload.get("direction_id")
        self.topic_results = [
            TopicResult(topic_result) for topic_result in direction_result_payload.get("topic_results")
        ]
        self.grade = direction_result_payload.get("grade")
        # super.__init__(grade=direction_result_payload.get("grade"))
        if (self.grade is None) and (type(calculation_strategy) != StrategyCriteria):
            self.grade = self.calculate_grade(calculation_strategy)

    def calculate_grade(self, calculation_strategy: GradeCalculationStrategy):
        # Получаем нужную информацию
        if type(calculation_strategy) in (StrategyWeights, StrategyAVGCritical):
            self.get_topics_calc_info()
        # Считаем результат
        grade = calculation_strategy.calculate(self.topic_results)
        return grade

    def get_topics_calc_info(self):
        """
        Получить веса и критичность поднаправлений, по которым пришли результаты
        """
        topic_ids = [topic_result.id for topic_result in self.topic_results]
        topics_info = DirectionsDB.get_topic_info_by_ids(topic_ids, self.inspection_target_id)
        topics_info = {topic_info.topic_id: topic_info for topic_info in topics_info}
        for topic_result in self.topic_results:
            topic_info = topics_info.get(topic_result.id)
            if topic_info is None:
                # Ошибка - не для всех поднаправлений получилось получить вес/критичность. (в бд нет записи по этому ид направления)
                continue
            topic_result.is_critical = topic_info.is_critical
            topic_result.weight = topic_info.weight
            topic_result.is_ignored = topic_info.is_ignored


class InspectionResultService:
    def __init__(
        self,
        payload,
        calculation_strategy=StrategyCriteria(),
    ):
        self.name = payload.get("name")
        self.description = payload.get("description")
        self.inspection_organ_id = payload.get("inspection_organ_id")
        self.inspection_target_id = payload.get("inspection_target_id")
        self.operator_id = payload.get("operator_id")
        self.inspection_date = payload.get("inspection_date")
        self.files = None
        if "files" in payload and len(payload.get("files")) > 0:
            self.files = [save_file(file) for file in payload.files]

        self.direction_results = [
            DirectionResult(direction_result, self.inspection_target_id, calculation_strategy)
            for direction_result in payload.get("direction_results")
        ]
        self.grade = payload.get("grade")
        if self.grade is None:
            self.grade = self.calculate_grade(calculation_strategy)

    def calculate_grade(self, calculation_strategy: GradeCalculationStrategy):
        calculatable_items = []  # что будет использовано для расчета оценки
        # Получаем нужную информацию
        if type(calculation_strategy) in (StrategyWeights, StrategyAVGCritical):
            self.get_directions_calc_info()
            calculatable_items = self.direction_results
        elif type(calculation_strategy) == StrategyCriteria:
            self.get_criteria_info()
            for direction in self.direction_results:
                if direction.matched_result_grade is not None:
                    calculatable_items.append(direction)
                for topic in direction.topic_results:
                    if topic.matched_result_grade is not None:
                        calculatable_items.append(topic)
        # Считаем результат
        grade = calculation_strategy.calculate(calculatable_items)
        return grade

    def get_directions_calc_info(self):
        """
        Получить веса и критичность направлений, по которым пришли результаты
        """
        direction_ids = [direction_result.id for direction_result in self.direction_results]
        directions_info = DirectionsDB.get_direction_info_by_ids(direction_ids, self.inspection_target_id)
        directions_info = {direction_info.direction_id: direction_info for direction_info in directions_info}
        for direction_result in self.direction_results:
            direction_info = directions_info.get(direction_result.id)
            if direction_info is None:
                # Ошибка - не для всех направлений получилось получить вес/критичность. (в бд нет записи по этому ид направления)
                continue
            direction_result.is_critical = direction_info.is_critical
            direction_result.weight = direction_info.weight
            direction_result.is_ignored = direction_info.is_ignored

    def get_criteria_info(self):
        direction_grades = [
            (direction_result.id, direction_result.grade) for direction_result in self.direction_results
        ]
        topic_grades = [
            (topic.id, topic.grade)
            for direction_result in self.direction_results
            for topic in direction_result.topic_results
        ]
        criteria_info_directions = DirectionsDB.get_criteria_result_directions(
            direction_grades, self.inspection_target_id
        )
        criteria_info_topics = DirectionsDB.get_criteria_result_topics(topic_grades, self.inspection_target_id)
        criteria_info_directions = {
            direction_info.direction_id: direction_info for direction_info in criteria_info_directions
        }
        criteria_info_topics = {topic_info.topic_id: topic_info for topic_info in criteria_info_topics}
        for direction_result in self.direction_results:
            direction_info = criteria_info_directions.get(direction_result.id)
            if direction_info is not None:
                direction_result.matched_result_grade = direction_info.result_grade

            for topic_result in direction_result.topic_results:
                topic_info = criteria_info_topics.get(topic_result.id)
                if topic_info is not None:
                    topic_result.matched_result_grade = topic_info.result_grade

    def write_to_db(self):
        res = InspectionDB.write_inspection_into_db(self)
        return res

    @staticmethod
    def get_info(inspection_id: str):
        return InspectionDB.get_by_id(inspection_id)

    @staticmethod
    def delete_from_db(inspection_id: str):
        res = InspectionDB.delete_inspection_by_id(inspection_id)
        return res

    @staticmethod
    def get_inspections(
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
    ):
        return InspectionDB.get_inspections(
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

    @staticmethod
    def update_in_db(inspection_id: str, payload: Dict):
        res = InspectionDB.update_inspection_in_db(inspection_id, payload)
        return res

    @staticmethod
    def get_overall_results_by_inspection_target_id(inspection_target_id):
        return InspectionDB.get_overall_results_by_inspection_target_id(inspection_target_id)
