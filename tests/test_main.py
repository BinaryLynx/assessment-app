import pytest
from app.api.inspection.service import InspectionResultService, StrategyAVGCritical, StrategyCriteria, StrategyWeights
from payloads import payload_criteria_2, payload_criteria_1, payload_generic_5


class TestInspectionResultService:

    @pytest.mark.parametrize(
        "payload, result",
        [
            (payload_criteria_2, 2),
            (payload_criteria_1, 1),
        ],
    )
    def test_strategy_criteria(self, payload, result):
        inspection_result = InspectionResultService(payload, StrategyCriteria())
        assert inspection_result.grade == result

    @pytest.mark.parametrize("payload, result", [(payload_generic_5, 5)])
    def test_strategy_weights(self, payload, result):
        inspection_result = InspectionResultService(payload, StrategyWeights())
        assert inspection_result.grade == result
        for direction_result in inspection_result.direction_results:
            assert direction_result.grade == 5

    @pytest.mark.parametrize("payload, result", [(payload_generic_5, 5)])
    def test_strategy_avg_critical(self, payload, result):
        inspection_result = InspectionResultService(payload, StrategyAVGCritical())
        assert inspection_result.grade == result
        for direction_result in inspection_result.direction_results:
            assert direction_result.grade == 5
