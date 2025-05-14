import pytest
from unittest.mock import Mock, patch
from app.core.social_api import SocialAPI
from app.schemas.social import SocialMediaResponse

class TestSocialAPI:
    @pytest.fixture
    def mock_api(self):
        api = SocialAPI("test")
        api.base_url = "http://test.com"
        api.session = Mock()
        return api

    def test_make_request_success(self, mock_api):
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_api.session.request.return_value = mock_response

        result = mock_api._make_request("GET", "/test")
        assert result == {"key": "value"}

    def test_make_request_retry(self, mock_api):
        mock_api.session.request.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            Mock(json=Mock(return_value={"key": "value"}))
        ]

        result = mock_api._make_request("GET", "/test")
        assert result == {"key": "value"}
        assert mock_api.session.request.call_count == 3

    def test_validate_response_success(self, mock_api):
        test_data = {
            "platform": "twitter",
            "account_id": "123",
            "timestamp": "2023-01-01T00:00:00",
            "id": "abc",
            "metrics": {"likes": 10}
        }
        
        result = mock_api.validate_response(SocialMediaResponse, test_data)
        assert result.platform == "twitter"
        assert result.account_id == "123"

    def test_validate_response_failure(self, mock_api):
        with pytest.raises(ValueError):
            mock_api.validate_response(SocialMediaResponse, {"invalid": "data"})