import pytest
from datetime import datetime
from app.utils.data_processor import DataProcessor, NormalizedMetric

class TestDataProcessor:
    @pytest.fixture
    def processor(self):
        return DataProcessor()

    def test_facebook_transform(self, processor):
        fb_data = {
            "name": "page_impressions",
            "values": [{"value": "1000"}],
            "end_time": "2025-05-12T00:00:00+0000",
            "id": "12345",
            "page_name": "test_page",
            "impressions": 1000,
            "engagements": 50
        }

        result = processor.transform_facebook(fb_data)
        
        assert result.platform == "facebook"
        assert result.metric_type == "page_impressions"
        assert result.value == 1000.0
        assert result.engagement_rate == 5.0

    def test_twitter_transform(self, processor):
        twitter_data = {
            "metric_name": "tweets",
            "metric_value": "500",
            "date": "2025-05-12",
            "account_id": "67890",
            "username": "test_user",
            "impressions": 2000,
            "engagements": 100
        }

        result = processor.transform_twitter(twitter_data)
        
        assert result.platform == "twitter"
        assert result.metric_type == "tweets"
        assert result.value == 500.0
        assert result.engagement_rate == 5.0

    def test_normalized_metric_validation(self):
        with pytest.raises(ValueError):
            NormalizedMetric(
                platform="test",
                metric_type="invalid",
                value=-1,  # Valor negativo deve falhar
                date=datetime.now(),
                page_id="123",
                username="test"
            )