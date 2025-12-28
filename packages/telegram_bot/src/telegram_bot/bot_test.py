"""Tests for JobAgentBot class."""

import os
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from telegram_bot.bot import JobAgentBot, create_bot


class TestJobAgentBot:
    """Tests for JobAgentBot class."""

    @patch("telegram_bot.bot.build_dependencies")
    def test_setup_handlers_raises_without_application(self, mock_build_deps):
        """setup_handlers should raise error if application not initialized."""
        mock_build_deps.return_value = MagicMock()
        bot = JobAgentBot("test_token")

        with pytest.raises(RuntimeError, match="Application not initialized"):
            bot.setup_handlers()

    @patch("telegram_bot.bot.build_dependencies")
    @patch("telegram_bot.bot.Application")
    def test_build_application_creates_application(self, mock_app_class, mock_build_deps):
        """build_application should create and return Application."""
        mock_build_deps.return_value = MagicMock()

        mock_app = MagicMock()
        mock_app.bot_data = {}
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.post_init.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_app_class.builder.return_value = mock_builder

        bot = JobAgentBot("test_token")
        result = bot.build_application()

        assert result == mock_app
        assert bot.application == mock_app

    @patch("telegram_bot.bot.build_dependencies")
    @patch("telegram_bot.bot.Application")
    def test_build_application_stores_dependencies_in_bot_data(
        self, mock_app_class, mock_build_deps
    ):
        """build_application should store dependencies in bot_data."""
        mock_deps = MagicMock()
        mock_build_deps.return_value = mock_deps

        mock_app = MagicMock()
        mock_app.bot_data = {}
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.post_init.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_app_class.builder.return_value = mock_builder

        bot = JobAgentBot("test_token")
        bot.build_application()

        assert mock_app.bot_data["dependencies"] == mock_deps

    @patch("telegram_bot.bot.build_dependencies")
    @patch("telegram_bot.bot.Application")
    def test_run_calls_run_polling(self, mock_app_class, mock_build_deps):
        """run should call run_polling on the application."""
        mock_build_deps.return_value = MagicMock()

        mock_app = MagicMock()
        mock_app.bot_data = {}
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.post_init.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_app_class.builder.return_value = mock_builder

        bot = JobAgentBot("test_token")
        bot.build_application()
        bot.run()

        mock_app.run_polling.assert_called_once()


class TestPostInit:
    """Tests for post_init method."""

    @patch("telegram_bot.bot.build_dependencies")
    async def test_post_init_sets_bot_commands(self, mock_build_deps):
        """post_init should set bot commands."""
        mock_build_deps.return_value = MagicMock()

        mock_app = MagicMock()
        mock_bot = AsyncMock()
        mock_app.bot = mock_bot

        bot = JobAgentBot("test_token")
        await bot.post_init(mock_app)

        mock_bot.set_my_commands.assert_called_once()

    @patch("telegram_bot.bot.build_dependencies")
    async def test_post_init_registers_all_commands(self, mock_build_deps):
        """post_init should register all expected commands."""
        mock_build_deps.return_value = MagicMock()

        mock_app = MagicMock()
        mock_bot = AsyncMock()
        mock_app.bot = mock_bot

        bot = JobAgentBot("test_token")
        await bot.post_init(mock_app)

        call_args = mock_bot.set_my_commands.call_args
        commands = call_args[0][0]
        command_names = [cmd[0] for cmd in commands]

        assert "start" in command_names
        assert "help" in command_names
        assert "search" in command_names
        assert "status" in command_names
        assert "cancel" in command_names
        assert "cv" in command_names


class TestCreateBot:
    """Tests for create_bot factory function."""

    @patch("telegram_bot.bot.build_dependencies")
    def test_create_bot_from_env_var(self, mock_build_deps):
        """create_bot should create bot from environment variable."""
        mock_build_deps.return_value = MagicMock()

        with patch.dict(os.environ, {"JOB_AGENT_BOT_TOKEN": "env_token_456"}):
            bot = create_bot()

        assert bot.token == "env_token_456"

    @patch("telegram_bot.bot.build_dependencies")
    def test_create_bot_raises_without_token(self, mock_build_deps):
        """create_bot should raise ValueError if token not set."""
        mock_build_deps.return_value = MagicMock()

        with patch.dict(os.environ, {}, clear=True):
            if "JOB_AGENT_BOT_TOKEN" in os.environ:
                del os.environ["JOB_AGENT_BOT_TOKEN"]

            with pytest.raises(ValueError, match="JOB_AGENT_BOT_TOKEN"):
                create_bot()

    @patch("telegram_bot.bot.build_dependencies")
    def test_create_bot_returns_job_agent_bot(self, mock_build_deps):
        """create_bot should return JobAgentBot instance."""
        mock_build_deps.return_value = MagicMock()

        with patch.dict(os.environ, {"JOB_AGENT_BOT_TOKEN": "test_token"}):
            bot = create_bot()

        assert isinstance(bot, JobAgentBot)
