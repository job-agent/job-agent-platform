"""Tests for ScrapperProducer."""

import json
from unittest.mock import MagicMock, patch

import pytest

from job_agent_backend.messaging.producer import ScrapperProducer


class TestScrapperProducerScrapeJobsStreaming:
    """Tests for ScrapperProducer.scrape_jobs_streaming() method."""

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_yields_responses(self, mock_connection_class: MagicMock) -> None:
        """Yields job responses as they arrive."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_responses(time_limit: int) -> None:
            response1 = {"jobs": [{"title": "Job 1"}], "success": True, "is_complete": False}
            response2 = {"jobs": [], "success": True, "is_complete": True}

            props = MagicMock()
            props.correlation_id = producer.correlation_id

            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response1).encode())
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response2).encode())

        mock_connection.process_data_events.side_effect = simulate_responses

        responses = list(producer.scrape_jobs_streaming())

        assert len(responses) == 2
        assert responses[0]["jobs"] == [{"title": "Job 1"}]
        assert responses[1]["is_complete"] is True

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_builds_filter_payload(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Builds correct filter payload from parameters."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_completion(time_limit: int) -> None:
            response = {"jobs": [], "success": True, "is_complete": True}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_completion

        list(
            producer.scrape_jobs_streaming(
                min_salary=5000,
                employment_location="on-site",
                posted_after="2024-01-15T10:30:00",
                existing_urls=["http://job1.com"],
                timeout=60,
            )
        )

        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args.kwargs
        body = json.loads(call_kwargs["body"])

        assert body["timeout"] == 60
        assert body["filters"]["min_salary"] == 5000
        assert body["filters"]["employment_location"] == "on-site"
        assert body["filters"]["posted_after"] == "2024-01-15T10:30:00"
        assert body["filters"]["existing_urls"] == ["http://job1.com"]

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_omits_none_filters(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Omits None values from filter payload."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_completion(time_limit: int) -> None:
            response = {"jobs": [], "success": True, "is_complete": True}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_completion

        list(
            producer.scrape_jobs_streaming(
                min_salary=None,
                employment_location=None,
                posted_after=None,
                existing_urls=None,
                timeout=30,
            )
        )

        call_kwargs = mock_channel.basic_publish.call_args.kwargs
        body = json.loads(call_kwargs["body"])

        assert body == {"timeout": 30}

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_raises_timeout_error(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Raises TimeoutError when no completion response within timeout."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        with patch.object(ScrapperProducer, "RESPONSE_TIMEOUT", 2):
            with pytest.raises(TimeoutError, match="No completion response received"):
                list(producer.scrape_jobs_streaming())

        mock_connection_instance.close.assert_called()

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_raises_on_error_response(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Raises Exception when response indicates error."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_error_response(time_limit: int) -> None:
            response = {"jobs": [], "success": False, "error": "Scraper failed"}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_error_response

        with pytest.raises(Exception, match="Scraper error: Scraper failed"):
            list(producer.scrape_jobs_streaming())

        mock_connection_instance.close.assert_called()

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_closes_connection_on_completion(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Closes connection after successful completion."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_completion(time_limit: int) -> None:
            response = {"jobs": [], "success": True, "is_complete": True}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_completion

        list(producer.scrape_jobs_streaming())

        mock_connection_instance.close.assert_called_once()

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_declares_request_queue(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Declares the request queue as durable."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_completion(time_limit: int) -> None:
            response = {"jobs": [], "success": True, "is_complete": True}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_completion

        list(producer.scrape_jobs_streaming())

        mock_channel.queue_declare.assert_any_call(queue="job.scrape.request", durable=True)

    @patch("job_agent_backend.messaging.producer.RabbitMQConnection")
    def test_scrape_jobs_streaming_publishes_with_correct_properties(
        self, mock_connection_class: MagicMock
    ) -> None:
        """Publishes request with correct message properties."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection_instance = MagicMock()
        mock_connection_instance.connect.return_value = mock_channel
        mock_connection_instance.connection = mock_connection
        mock_connection_class.return_value = mock_connection_instance

        queue_result = MagicMock()
        queue_result.method.queue = "reply_queue_123"
        mock_channel.queue_declare.side_effect = [MagicMock(), queue_result]

        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")

        def simulate_completion(time_limit: int) -> None:
            response = {"jobs": [], "success": True, "is_complete": True}
            props = MagicMock()
            props.correlation_id = producer.correlation_id
            producer._on_response(mock_channel, MagicMock(), props, json.dumps(response).encode())

        mock_connection.process_data_events.side_effect = simulate_completion

        list(producer.scrape_jobs_streaming())

        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args.kwargs

        assert call_kwargs["exchange"] == ""
        assert call_kwargs["routing_key"] == "job.scrape.request"
        props = call_kwargs["properties"]
        assert props.reply_to == "reply_queue_123"
        assert props.correlation_id == producer.correlation_id
        assert props.content_type == "application/json"
        assert props.delivery_mode == 2


class TestScrapperProducerOnResponse:
    """Tests for ScrapperProducer._on_response() callback."""

    def test_on_response_appends_response_when_correlation_id_matches(self) -> None:
        """Appends response to list when correlation_id matches."""
        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")
        producer.correlation_id = "test-correlation-id"
        producer.responses = []

        props = MagicMock()
        props.correlation_id = "test-correlation-id"
        body = json.dumps({"jobs": [{"title": "Job 1"}], "success": True}).encode()

        producer._on_response(MagicMock(), MagicMock(), props, body)

        assert len(producer.responses) == 1
        assert producer.responses[0]["jobs"] == [{"title": "Job 1"}]

    def test_on_response_ignores_wrong_correlation_id(self) -> None:
        """Ignores messages with wrong correlation_id."""
        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")
        producer.correlation_id = "expected-id"
        producer.responses = []

        props = MagicMock()
        props.correlation_id = "different-id"
        body = json.dumps({"jobs": [{"title": "Job 1"}], "success": True}).encode()

        producer._on_response(MagicMock(), MagicMock(), props, body)

        assert len(producer.responses) == 0

    def test_on_response_sets_is_complete_flag(self) -> None:
        """Sets is_complete flag when response has is_complete=True."""
        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")
        producer.correlation_id = "test-id"
        producer.responses = []
        producer.is_complete = False

        props = MagicMock()
        props.correlation_id = "test-id"
        body = json.dumps({"jobs": [], "success": True, "is_complete": True}).encode()

        producer._on_response(MagicMock(), MagicMock(), props, body)

        assert producer.is_complete is True

    def test_on_response_does_not_set_is_complete_for_batch(self) -> None:
        """Does not set is_complete flag for batch responses."""
        producer = ScrapperProducer(rabbitmq_url="amqp://localhost")
        producer.correlation_id = "test-id"
        producer.responses = []
        producer.is_complete = False

        props = MagicMock()
        props.correlation_id = "test-id"
        body = json.dumps({"jobs": [{"title": "Job 1"}], "success": True}).encode()

        producer._on_response(MagicMock(), MagicMock(), props, body)

        assert producer.is_complete is False
