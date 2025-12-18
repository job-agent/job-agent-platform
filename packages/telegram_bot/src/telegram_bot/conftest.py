"""Shared test fixtures for telegram_bot package."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from telegram_bot.di import BotDependencies


@dataclass
class MockUser:
    """Mock Telegram User."""

    id: int = 12345
    first_name: str = "TestUser"
    last_name: str = "LastName"
    username: str = "testuser"
    is_bot: bool = False


@dataclass
class MockDocument:
    """Mock Telegram Document."""

    file_id: str = "test_file_id_123"
    file_name: str = "test_cv.pdf"
    mime_type: str = "application/pdf"
    file_size: int = 1024


class MockMessage:
    """Mock Telegram Message with async methods."""

    def __init__(
        self,
        text: str = "",
        document: Optional[MockDocument] = None,
        user: Optional[MockUser] = None,
    ):
        self.text = text
        self.document = document
        self._reply_texts: list[str] = []
        self._reply_documents: list[tuple[BytesIO, str, str]] = []
        self._edited_texts: list[str] = []
        self._user = user or MockUser()

    async def reply_text(self, text: str, **kwargs) -> "MockMessage":
        """Mock reply_text that records what was sent."""
        self._reply_texts.append(text)
        return MockMessage(text=text)

    async def reply_document(
        self, document: BytesIO, filename: str, caption: str = "", **kwargs
    ) -> "MockMessage":
        """Mock reply_document that records what was sent."""
        self._reply_documents.append((document, filename, caption))
        return MockMessage()

    async def edit_text(self, text: str, **kwargs) -> "MockMessage":
        """Mock edit_text that records what was edited."""
        self._edited_texts.append(text)
        return self


class MockUpdate:
    """Mock Telegram Update."""

    def __init__(
        self,
        user: Optional[MockUser] = None,
        message: Optional[MockMessage] = None,
        document: Optional[MockDocument] = None,
    ):
        self._user = user or MockUser()
        self._message = message or MockMessage(user=self._user, document=document)

    @property
    def effective_user(self) -> MockUser:
        return self._user

    @property
    def message(self) -> MockMessage:
        return self._message


class MockFile:
    """Mock Telegram File."""

    def __init__(self, file_path: str = "/tmp/test_file.pdf"):
        self.file_path = file_path

    async def download_to_drive(self, path: str) -> None:
        """Mock download that creates an empty file."""
        Path(path).write_text("mock pdf content")


class MockBot:
    """Mock Telegram Bot."""

    def __init__(self):
        self._files: dict[str, MockFile] = {}

    async def get_file(self, file_id: str) -> MockFile:
        """Mock get_file."""
        return self._files.get(file_id, MockFile())

    async def set_my_commands(self, commands: list) -> None:
        """Mock set_my_commands."""
        pass


class MockApplication:
    """Mock Telegram Application."""

    def __init__(self, dependencies: Optional[BotDependencies] = None):
        self.bot_data: dict[str, Any] = {}
        if dependencies:
            self.bot_data["dependencies"] = dependencies
        self.bot = MockBot()


class MockContext:
    """Mock Telegram Context."""

    def __init__(
        self,
        args: Optional[list[str]] = None,
        dependencies: Optional[BotDependencies] = None,
    ):
        self.args = args or []
        self.application = MockApplication(dependencies)
        self.bot = self.application.bot


@pytest.fixture
def mock_user() -> MockUser:
    """Create a mock Telegram user."""
    return MockUser()


@pytest.fixture
def mock_message(mock_user: MockUser) -> MockMessage:
    """Create a mock Telegram message."""
    return MockMessage(user=mock_user)


@pytest.fixture
def mock_update(mock_user: MockUser, mock_message: MockMessage) -> MockUpdate:
    """Create a mock Telegram update."""
    return MockUpdate(user=mock_user, message=mock_message)


@pytest.fixture
def mock_context() -> MockContext:
    """Create a mock Telegram context without dependencies."""
    return MockContext()


@pytest.fixture
def mock_orchestrator() -> MagicMock:
    """Create a mock orchestrator."""
    orchestrator = MagicMock()
    orchestrator.has_cv.return_value = True
    orchestrator.load_cv.return_value = "Test CV content"
    orchestrator.get_cv_path.return_value = Path("/tmp/test_cv")
    orchestrator.upload_cv.return_value = None
    orchestrator.filter_jobs_list.return_value = []
    orchestrator.scrape_jobs_streaming.return_value = iter([])
    orchestrator.process_jobs_iterator.return_value = iter([])
    return orchestrator


@pytest.fixture
def mock_cv_repository() -> MagicMock:
    """Create a mock CV repository."""
    repo = MagicMock()
    repo.find.return_value = "Test CV content from repository"
    repo.create.return_value = "created"
    repo.update.return_value = "updated"
    return repo


@pytest.fixture
def mock_job_repository() -> MagicMock:
    """Create a mock job repository."""
    repo = MagicMock()
    repo.get_latest_updated_at.return_value = None
    return repo


@pytest.fixture
def mock_dependencies(
    mock_orchestrator: MagicMock,
    mock_cv_repository: MagicMock,
    mock_job_repository: MagicMock,
) -> BotDependencies:
    """Create mock BotDependencies."""
    orchestrator_factory = MagicMock(return_value=mock_orchestrator)
    cv_repository_factory = MagicMock(return_value=mock_cv_repository)
    job_repository_factory = MagicMock(return_value=mock_job_repository)

    return BotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
        job_repository_factory=job_repository_factory,
    )


@pytest.fixture
def mock_context_with_deps(mock_dependencies: BotDependencies) -> MockContext:
    """Create a mock context with dependencies injected."""
    return MockContext(dependencies=mock_dependencies)
