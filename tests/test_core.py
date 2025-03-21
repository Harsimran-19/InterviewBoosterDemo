import pytest
from src.core.booster import InterviewBooster

class TestInterviewBooster:
    @pytest.fixture
    def booster(self):
        return InterviewBooster()

    def test_get_responses(self, booster):
        result = booster.get_all_responses("test@example.com")
        assert isinstance(result.email, str)
        assert isinstance(result.sheet_data, dict)
