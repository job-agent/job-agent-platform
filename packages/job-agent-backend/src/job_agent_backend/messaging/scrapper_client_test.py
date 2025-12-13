"""Tests for ScrapperClient."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from job_agent_backend.messaging.scrapper_client import ScrapperClient


class TestScrapperClientScrapeJobsStreaming:
    """Tests for ScrapperClient.scrape_jobs_streaming() method."""

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_yields_batches_from_producer(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Yields job batches received from producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter(
            [
                {"jobs": [{"title": "Job 1"}], "success": True},
                {"jobs": [{"title": "Job 2"}, {"title": "Job 3"}], "success": True},
            ]
        )
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        batches = list(client.scrape_jobs_streaming())

        assert len(batches) == 2
        assert batches[0] == [{"title": "Job 1"}]
        assert batches[1] == [{"title": "Job 2"}, {"title": "Job 3"}]

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_passes_default_parameters(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Passes default parameter values to producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        list(client.scrape_jobs_streaming())

        mock_producer.scrape_jobs_streaming.assert_called_once_with(
            min_salary=4000,
            employment_location="remote",
            posted_after=None,
            existing_urls=None,
            timeout=30,
        )

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_passes_custom_parameters(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Passes custom parameter values to producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        list(
            client.scrape_jobs_streaming(
                min_salary=5000,
                employment_location="on-site",
                timeout=60,
            )
        )

        mock_producer.scrape_jobs_streaming.assert_called_once_with(
            min_salary=5000,
            employment_location="on-site",
            posted_after=None,
            existing_urls=None,
            timeout=60,
        )

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_converts_datetime_to_iso_string(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Converts posted_after datetime to ISO format string."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        posted_after = datetime(2024, 1, 15, 10, 30, 0)
        list(client.scrape_jobs_streaming(posted_after=posted_after))

        mock_producer.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_producer.scrape_jobs_streaming.call_args.kwargs
        assert call_kwargs["posted_after"] == "2024-01-15T10:30:00"

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_handles_empty_response(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Handles empty jobs list in response."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([{"jobs": [], "success": True}])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        batches = list(client.scrape_jobs_streaming())

        assert len(batches) == 1
        assert batches[0] == []

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_handles_missing_jobs_key(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Returns empty list when jobs key is missing from response."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([{"success": True}])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        batches = list(client.scrape_jobs_streaming())

        assert len(batches) == 1
        assert batches[0] == []

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_propagates_timeout_error(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Propagates TimeoutError from producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.side_effect = TimeoutError("Timeout")
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")

        with pytest.raises(TimeoutError, match="Timeout"):
            list(client.scrape_jobs_streaming())

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_scrape_jobs_streaming_propagates_exception(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Propagates generic Exception from producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.side_effect = Exception("Scraper error")
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")

        with pytest.raises(Exception, match="Scraper error"):
            list(client.scrape_jobs_streaming())


class TestScrapperClientGetExistingUrls:
    """Tests for ScrapperClient._get_existing_urls() method."""

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_get_existing_urls_queries_repository(self, mock_producer_class: MagicMock) -> None:
        """Queries repository for existing URLs and passes them to producer."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        mock_repository = MagicMock()
        mock_repository.get_existing_urls_by_source.return_value = [
            "http://job1.com",
            "http://job2.com",
        ]
        mock_repository_factory = MagicMock(return_value=mock_repository)

        client = ScrapperClient(
            rabbitmq_url="amqp://localhost",
            job_repository_factory=mock_repository_factory,
            source="djinni",
            url_lookback_days=60,
        )
        list(client.scrape_jobs_streaming())

        mock_repository_factory.assert_called_once()
        mock_repository.get_existing_urls_by_source.assert_called_once_with("djinni", days=60)
        mock_producer.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_producer.scrape_jobs_streaming.call_args.kwargs
        assert call_kwargs["existing_urls"] == ["http://job1.com", "http://job2.com"]

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_get_existing_urls_uses_custom_source_and_lookback(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Uses custom source and lookback days when querying repository."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        mock_repository = MagicMock()
        mock_repository.get_existing_urls_by_source.return_value = []
        mock_repository_factory = MagicMock(return_value=mock_repository)

        client = ScrapperClient(
            rabbitmq_url="amqp://localhost",
            job_repository_factory=mock_repository_factory,
            source="linkedin",
            url_lookback_days=90,
        )
        list(client.scrape_jobs_streaming())

        mock_repository.get_existing_urls_by_source.assert_called_once_with("linkedin", days=90)

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_get_existing_urls_returns_none_when_no_factory(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Returns None when no repository factory is configured."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        client = ScrapperClient(rabbitmq_url="amqp://localhost")
        list(client.scrape_jobs_streaming())

        mock_producer.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_producer.scrape_jobs_streaming.call_args.kwargs
        assert call_kwargs["existing_urls"] is None

    @patch("job_agent_backend.messaging.scrapper_client.ScrapperProducer")
    def test_get_existing_urls_returns_none_on_repository_error(
        self, mock_producer_class: MagicMock
    ) -> None:
        """Returns None and logs warning when repository raises exception."""
        mock_producer = MagicMock()
        mock_producer.scrape_jobs_streaming.return_value = iter([])
        mock_producer_class.return_value = mock_producer

        mock_repository = MagicMock()
        mock_repository.get_existing_urls_by_source.side_effect = Exception("DB error")
        mock_repository_factory = MagicMock(return_value=mock_repository)

        client = ScrapperClient(
            rabbitmq_url="amqp://localhost",
            job_repository_factory=mock_repository_factory,
        )
        list(client.scrape_jobs_streaming())

        mock_producer.scrape_jobs_streaming.assert_called_once()
        call_kwargs = mock_producer.scrape_jobs_streaming.call_args.kwargs
        assert call_kwargs["existing_urls"] is None
