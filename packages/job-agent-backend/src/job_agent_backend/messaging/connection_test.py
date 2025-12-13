"""Tests for RabbitMQConnection."""

from unittest.mock import MagicMock, patch

import pytest

from job_agent_backend.messaging.connection import RabbitMQConnection


class TestRabbitMQConnectionInit:
    """Tests for RabbitMQConnection initialization."""

    def test_init_with_url_parameter(self) -> None:
        """Uses URL from parameter when provided."""
        url = "amqp://user:pass@localhost:5672/"

        connection = RabbitMQConnection(rabbitmq_url=url)

        assert connection.rabbitmq_url == url

    def test_init_with_env_var(self) -> None:
        """Falls back to RABBITMQ_URL environment variable when no parameter provided."""
        env_url = "amqp://env:env@localhost:5672/"

        with patch.dict("os.environ", {"RABBITMQ_URL": env_url}):
            connection = RabbitMQConnection()

        assert connection.rabbitmq_url == env_url

    def test_init_parameter_takes_precedence_over_env(self) -> None:
        """URL parameter takes precedence over environment variable."""
        param_url = "amqp://param:param@localhost:5672/"
        env_url = "amqp://env:env@localhost:5672/"

        with patch.dict("os.environ", {"RABBITMQ_URL": env_url}):
            connection = RabbitMQConnection(rabbitmq_url=param_url)

        assert connection.rabbitmq_url == param_url

    def test_init_sets_connection_and_channel_to_none(self) -> None:
        """Connection and channel are None after initialization."""
        connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")

        assert connection.connection is None
        assert connection.channel is None


class TestRabbitMQConnectionConnect:
    """Tests for RabbitMQConnection.connect() method."""

    @patch("job_agent_backend.messaging.connection.pika")
    def test_connect_creates_connection_and_channel(self, mock_pika: MagicMock) -> None:
        """Creates new connection and channel when not connected."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection

        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")
        result = rabbitmq_connection.connect()

        mock_pika.URLParameters.assert_called_once_with("amqp://localhost")
        mock_pika.BlockingConnection.assert_called_once()
        mock_connection.channel.assert_called_once()
        assert result == mock_channel
        assert rabbitmq_connection.connection == mock_connection
        assert rabbitmq_connection.channel == mock_channel

    @patch("job_agent_backend.messaging.connection.pika")
    def test_connect_reuses_existing_connection(self, mock_pika: MagicMock) -> None:
        """Reuses existing connection when already connected."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection

        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")
        rabbitmq_connection.connect()
        rabbitmq_connection.connect()

        assert mock_pika.BlockingConnection.call_count == 1

    @patch("job_agent_backend.messaging.connection.pika")
    def test_connect_reconnects_when_connection_closed(self, mock_pika: MagicMock) -> None:
        """Creates new connection when existing connection is closed."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection

        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")
        rabbitmq_connection.connect()

        mock_connection.is_closed = True
        rabbitmq_connection.connect()

        assert mock_pika.BlockingConnection.call_count == 2


class TestRabbitMQConnectionClose:
    """Tests for RabbitMQConnection.close() method."""

    def test_close_closes_channel_and_connection(self) -> None:
        """Closes both channel and connection when open."""
        mock_channel = MagicMock()
        mock_channel.is_closed = False
        mock_connection = MagicMock()
        mock_connection.is_closed = False

        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")
        rabbitmq_connection.channel = mock_channel
        rabbitmq_connection.connection = mock_connection

        rabbitmq_connection.close()

        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_close_safe_when_already_closed(self) -> None:
        """Does not raise when channel and connection already closed."""
        mock_channel = MagicMock()
        mock_channel.is_closed = True
        mock_connection = MagicMock()
        mock_connection.is_closed = True

        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")
        rabbitmq_connection.channel = mock_channel
        rabbitmq_connection.connection = mock_connection

        rabbitmq_connection.close()

        mock_channel.close.assert_not_called()
        mock_connection.close.assert_not_called()

    def test_close_safe_when_never_connected(self) -> None:
        """Does not raise when never connected."""
        rabbitmq_connection = RabbitMQConnection(rabbitmq_url="amqp://localhost")

        rabbitmq_connection.close()


class TestRabbitMQConnectionContextManager:
    """Tests for RabbitMQConnection context manager."""

    @patch("job_agent_backend.messaging.connection.pika")
    def test_context_manager_connects_and_closes(self, mock_pika: MagicMock) -> None:
        """Context manager connects on entry and closes on exit."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection

        with RabbitMQConnection(rabbitmq_url="amqp://localhost") as conn:
            assert conn.channel == mock_channel

        mock_connection.close.assert_called_once()

    @patch("job_agent_backend.messaging.connection.pika")
    def test_context_manager_closes_on_exception(self, mock_pika: MagicMock) -> None:
        """Context manager closes connection even when exception occurs."""
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_pika.BlockingConnection.return_value = mock_connection

        with pytest.raises(ValueError):
            with RabbitMQConnection(rabbitmq_url="amqp://localhost"):
                raise ValueError("Test exception")

        mock_connection.close.assert_called_once()
