"""Tests for dependency injection module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from telegram_bot.di import (
    BotDependencies,
    build_dependencies,
    get_dependencies,
    _create_cv_repository,
)


class TestBotDependencies:
    """Tests for BotDependencies dataclass."""

    def test_is_frozen(self):
        """BotDependencies should be immutable (frozen)."""
        orchestrator_factory = MagicMock()
        cv_repository_factory = MagicMock()

        deps = BotDependencies(
            orchestrator_factory=orchestrator_factory,
            cv_repository_factory=cv_repository_factory,
        )

        with pytest.raises(AttributeError):
            deps.orchestrator_factory = MagicMock()

    def test_stores_orchestrator_factory(self):
        """BotDependencies should store orchestrator factory."""
        orchestrator_factory = MagicMock()
        cv_repository_factory = MagicMock()

        deps = BotDependencies(
            orchestrator_factory=orchestrator_factory,
            cv_repository_factory=cv_repository_factory,
        )

        assert deps.orchestrator_factory == orchestrator_factory

    def test_stores_cv_repository_factory(self):
        """BotDependencies should store CV repository factory."""
        orchestrator_factory = MagicMock()
        cv_repository_factory = MagicMock()

        deps = BotDependencies(
            orchestrator_factory=orchestrator_factory,
            cv_repository_factory=cv_repository_factory,
        )

        assert deps.cv_repository_factory == cv_repository_factory


class TestBuildDependencies:
    """Tests for build_dependencies function."""

    @patch("telegram_bot.di.container")
    def test_returns_bot_dependencies(self, mock_container):
        """build_dependencies should return BotDependencies instance."""
        mock_container.orchestrator = MagicMock()
        mock_container.cv_repository = MagicMock()

        deps = build_dependencies()

        assert isinstance(deps, BotDependencies)

    @patch("telegram_bot.di.container")
    def test_uses_container_orchestrator(self, mock_container):
        """build_dependencies should use container's orchestrator."""
        mock_orchestrator = MagicMock()
        mock_container.orchestrator = mock_orchestrator
        mock_container.cv_repository = MagicMock()

        deps = build_dependencies()

        assert deps.orchestrator_factory == mock_orchestrator

    @patch("telegram_bot.di.container")
    def test_creates_cv_repository_factory(self, mock_container):
        """build_dependencies should create a CV repository factory."""
        mock_container.orchestrator = MagicMock()
        mock_container.cv_repository = MagicMock()

        deps = build_dependencies()

        assert deps.cv_repository_factory is not None
        assert callable(deps.cv_repository_factory)


class TestCreateCvRepository:
    """Tests for _create_cv_repository function."""

    @patch("telegram_bot.di.container")
    def test_creates_repository_for_user(self, mock_container):
        """_create_cv_repository should create repository for specific user."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_cv_path.return_value = Path("/tmp/cv/user_123")
        mock_container.orchestrator.return_value = mock_orchestrator

        mock_cv_repo_class = MagicMock()
        mock_cv_repo = MagicMock()
        mock_cv_repo_class.return_value = mock_cv_repo
        mock_container.cv_repository.return_value = mock_cv_repo_class

        _create_cv_repository(123)

        mock_orchestrator.get_cv_path.assert_called_once_with(123)

    @patch("telegram_bot.di.container")
    def test_returns_cv_repository_instance(self, mock_container):
        """_create_cv_repository should return CV repository instance."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_cv_path.return_value = Path("/tmp/cv/user_456")
        mock_container.orchestrator.return_value = mock_orchestrator

        mock_cv_repo = MagicMock()
        mock_cv_repo_class = MagicMock(return_value=mock_cv_repo)
        mock_container.cv_repository.return_value = mock_cv_repo_class

        result = _create_cv_repository(456)

        assert result == mock_cv_repo


class TestGetDependencies:
    """Tests for get_dependencies function."""

    def test_gets_dependencies_from_context(self):
        """get_dependencies should retrieve dependencies from context."""
        mock_deps = MagicMock()
        mock_context = MagicMock()
        mock_context.application.bot_data = {"dependencies": mock_deps}

        result = get_dependencies(mock_context)

        assert result == mock_deps

    def test_accesses_correct_key(self):
        """get_dependencies should access 'dependencies' key in bot_data."""
        mock_deps = BotDependencies(
            orchestrator_factory=MagicMock(),
            cv_repository_factory=MagicMock(),
        )
        mock_context = MagicMock()
        mock_context.application.bot_data = {"dependencies": mock_deps}

        result = get_dependencies(mock_context)

        assert result == mock_deps
        assert isinstance(result, BotDependencies)

    def test_raises_key_error_if_missing(self):
        """get_dependencies should raise KeyError if dependencies not set."""
        mock_context = MagicMock()
        mock_context.application.bot_data = {}

        with pytest.raises(KeyError):
            get_dependencies(mock_context)
