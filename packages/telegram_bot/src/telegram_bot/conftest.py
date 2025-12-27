"""Shared test fixtures for telegram_bot package."""

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Optional, Protocol
from unittest.mock import MagicMock

import pytest


# Protocol definitions for DI mocking (avoid importing production BotDependencies)
class OrchestratorFactory(Protocol):
    def __call__(self, *, logger: Optional[Callable[[str], None]] = None) -> MagicMock: ...


class CVRepositoryFactory(Protocol):
    def __call__(self, user_id: int) -> MagicMock: ...


class EssayServiceFactory(Protocol):
    def __call__(self) -> MagicMock: ...


@dataclass
class MockBotDependencies:
    """Mock BotDependencies for testing without importing production DI."""

    orchestrator_factory: OrchestratorFactory
    cv_repository_factory: CVRepositoryFactory
    essay_service_factory: Optional[EssayServiceFactory] = None


@dataclass(frozen=True)
class MockEssay:
    """Mock Essay object returned by essay service."""

    id: int
    question: Optional[str]
    answer: str
    keywords: Optional[list] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    """Mock Telegram Message with async methods and optional shared tracking.

    Supports two modes:
    1. Local tracking (default): Each message instance has its own tracking lists.
    2. Shared tracking: All chained messages share a tracker dict, so edits on
       child messages returned by reply_text are visible on the parent.

    To enable shared tracking, pass a tracker dict or use enable_shared_tracking=True.
    """

    def __init__(
        self,
        text: str = "",
        document: Optional[MockDocument] = None,
        user: Optional[MockUser] = None,
        tracker: Optional[dict] = None,
        enable_shared_tracking: bool = False,
    ):
        self.text = text
        self.document = document
        self._user = user or MockUser()

        # If tracker is provided, use shared tracking mode
        # If enable_shared_tracking is True, create a new shared tracker
        if tracker is not None:
            self._tracker = tracker
            self._shared_tracking = True
        elif enable_shared_tracking:
            self._tracker = {
                "reply_texts": [],
                "edited_texts": [],
                "reply_documents": [],
            }
            self._shared_tracking = True
        else:
            # Local tracking mode (backward compatible)
            self._tracker = None
            self._shared_tracking = False
            self._local_reply_texts: list[str] = []
            self._local_reply_documents: list[tuple[BytesIO, str, str]] = []
            self._local_edited_texts: list[str] = []

    @property
    def _reply_texts(self) -> list[str]:
        if self._shared_tracking:
            return self._tracker["reply_texts"]
        return self._local_reply_texts

    @property
    def _edited_texts(self) -> list[str]:
        if self._shared_tracking:
            return self._tracker["edited_texts"]
        return self._local_edited_texts

    @property
    def _reply_documents(self) -> list[tuple[BytesIO, str, str]]:
        if self._shared_tracking:
            return self._tracker["reply_documents"]
        return self._local_reply_documents

    async def reply_text(self, text: str, **kwargs) -> "MockMessage":
        """Mock reply_text that records what was sent."""
        self._reply_texts.append(text)
        if self._shared_tracking:
            return MockMessage(text=text, tracker=self._tracker)
        return MockMessage(text=text)

    async def reply_document(
        self, document: BytesIO, filename: str, caption: str = "", **kwargs
    ) -> "MockMessage":
        """Mock reply_document that records what was sent."""
        self._reply_documents.append((document, filename, caption))
        if self._shared_tracking:
            return MockMessage(tracker=self._tracker)
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
        enable_shared_tracking: bool = False,
    ):
        self._user = user or MockUser()
        if message is not None:
            self._message = message
        else:
            self._message = MockMessage(
                user=self._user,
                document=document,
                enable_shared_tracking=enable_shared_tracking,
            )

    @property
    def effective_user(self) -> MockUser:
        return self._user

    @property
    def message(self) -> MockMessage:
        return self._message


class MockFile:
    """Mock Telegram File with download capability."""

    def __init__(
        self,
        file_path: str = "/tmp/test_file.pdf",
        content: bytes = b"mock pdf content",
    ):
        self.file_path = file_path
        self.content = content

    async def download_to_drive(self, path: str) -> None:
        """Mock download that creates a file with content."""
        Path(path).write_bytes(self.content)


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

    def __init__(self, dependencies: Optional[MockBotDependencies] = None):
        self.bot_data: dict[str, Any] = {}
        if dependencies:
            self.bot_data["dependencies"] = dependencies
        self.bot = MockBot()


class MockContext:
    """Mock Telegram Context."""

    def __init__(
        self,
        args: Optional[list[str]] = None,
        dependencies: Optional[MockBotDependencies] = None,
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
def mock_orchestrator_factory():
    """Factory fixture for creating mock orchestrators with specific configurations.

    Creates orchestrators with sensible defaults that can be overridden.
    Reduces repetitive configuration in tests.

    Usage:
        def test_with_defaults(mock_orchestrator_factory):
            orchestrator = mock_orchestrator_factory()  # has_cv=True, no jobs

        def test_without_cv(mock_orchestrator_factory):
            orchestrator = mock_orchestrator_factory(has_cv=False)

        def test_with_jobs(mock_orchestrator_factory):
            jobs = [{"id": 1, "title": "Developer"}]
            orchestrator = mock_orchestrator_factory(
                scraped_jobs=[(jobs, 1)],
                filtered_jobs=jobs
            )

        def test_with_error(mock_orchestrator_factory):
            orchestrator = mock_orchestrator_factory(load_cv_error=Exception("fail"))
    """

    def factory(
        has_cv: bool = True,
        cv_content: str = "Test CV content",
        cv_path: Optional[Path] = None,
        scraped_jobs: Optional[list[tuple[list[dict], int]]] = None,
        filtered_jobs: Optional[list[dict]] = None,
        processed_jobs: Optional[list[tuple[int, int, dict]]] = None,
        load_cv_error: Optional[Exception] = None,
        scrape_error: Optional[Exception] = None,
        upload_cv_error: Optional[Exception] = None,
    ) -> MagicMock:
        orchestrator = MagicMock()
        orchestrator.has_cv.return_value = has_cv
        orchestrator.get_cv_path.return_value = cv_path or Path("/tmp/test_cv")
        orchestrator.upload_cv.return_value = None

        # Configure load_cv
        if load_cv_error:
            orchestrator.load_cv.side_effect = load_cv_error
        else:
            orchestrator.load_cv.return_value = cv_content

        # Configure upload_cv error
        if upload_cv_error:
            orchestrator.upload_cv.side_effect = upload_cv_error

        # Configure scrape_jobs_streaming
        if scrape_error:
            orchestrator.scrape_jobs_streaming.side_effect = scrape_error
        else:
            orchestrator.scrape_jobs_streaming.return_value = iter(scraped_jobs or [])

        # Configure filter and process
        orchestrator.filter_jobs_list.return_value = filtered_jobs or []
        orchestrator.process_jobs_iterator.return_value = iter(processed_jobs or [])

        return orchestrator

    return factory


@pytest.fixture
def mock_orchestrator(mock_orchestrator_factory) -> MagicMock:
    """Create a mock orchestrator with default configuration.

    Uses mock_orchestrator_factory with defaults (has_cv=True, no jobs).
    For custom configurations, use mock_orchestrator_factory directly.
    """
    return mock_orchestrator_factory()


@pytest.fixture
def mock_cv_repository() -> MagicMock:
    """Create a mock CV repository."""
    repo = MagicMock()
    repo.find.return_value = "Test CV content from repository"
    repo.create.return_value = "created"
    repo.update.return_value = "updated"
    return repo


@pytest.fixture
def mock_essay_service() -> MagicMock:
    """Create a mock essay service with default behavior.

    Returns a MagicMock configured to return a MockEssay on create().
    Tests can override the return_value or side_effect as needed.
    """
    service = MagicMock()
    service.create.return_value = MockEssay(
        id=42,
        question="Test question",
        answer="Test answer",
    )
    return service


@pytest.fixture
def mock_dependencies(
    mock_orchestrator: MagicMock,
    mock_cv_repository: MagicMock,
) -> MockBotDependencies:
    """Create mock BotDependencies without essay service."""
    orchestrator_factory = MagicMock(return_value=mock_orchestrator)
    cv_repository_factory = MagicMock(return_value=mock_cv_repository)

    return MockBotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
    )


@pytest.fixture
def mock_dependencies_with_essay(
    mock_orchestrator: MagicMock,
    mock_cv_repository: MagicMock,
    mock_essay_service: MagicMock,
) -> MockBotDependencies:
    """Create mock BotDependencies including essay service factory."""
    orchestrator_factory = MagicMock(return_value=mock_orchestrator)
    cv_repository_factory = MagicMock(return_value=mock_cv_repository)
    essay_service_factory = MagicMock(return_value=mock_essay_service)

    return MockBotDependencies(
        orchestrator_factory=orchestrator_factory,
        cv_repository_factory=cv_repository_factory,
        essay_service_factory=essay_service_factory,
    )


@pytest.fixture
def mock_context_with_deps(mock_dependencies: MockBotDependencies) -> MockContext:
    """Create a mock context with dependencies injected."""
    return MockContext(dependencies=mock_dependencies)


@dataclass
class HandlerTestSetup:
    """Container for standard handler test setup objects.

    Provides convenient access to all mock objects needed for handler tests.
    The message has shared tracking enabled, so edits on child messages
    (returned by reply_text) are visible via message._reply_texts and
    message._edited_texts.
    """

    user: MockUser
    message: MockMessage
    update: MockUpdate
    context: MockContext
    essay_service: Optional[MagicMock] = None


@pytest.fixture
def handler_test_setup_factory(mock_dependencies: MockBotDependencies):
    """Factory fixture for creating standard handler test setup.

    Creates user, message (with shared tracking), update, and context
    in one call. Reduces repetitive setup code in handler tests.

    Usage:
        def test_example(handler_test_setup_factory):
            setup = handler_test_setup_factory(user_id=1001)
            await some_handler(setup.update, setup.context)
            assert "expected" in setup.message._reply_texts

        # With document:
        def test_upload(handler_test_setup_factory):
            doc = MockDocument(file_name="test.pdf")
            setup = handler_test_setup_factory(user_id=1002, document=doc)
            await upload_handler(setup.update, setup.context)

        # With custom args:
        def test_search(handler_test_setup_factory):
            setup = handler_test_setup_factory(user_id=1003, args=["min_salary=5000"])
            await search_handler(setup.update, setup.context)
    """

    def factory(
        user_id: int = 12345,
        document: Optional[MockDocument] = None,
        args: Optional[list[str]] = None,
        enable_shared_tracking: bool = True,
        message_text: str = "",
    ) -> HandlerTestSetup:
        user = MockUser(id=user_id)
        message = MockMessage(
            text=message_text,
            user=user,
            document=document,
            enable_shared_tracking=enable_shared_tracking,
        )
        update = MockUpdate(user=user, message=message, document=document)
        context = MockContext(args=args, dependencies=mock_dependencies)

        return HandlerTestSetup(
            user=user,
            message=message,
            update=update,
            context=context,
        )

    return factory


@pytest.fixture
def essay_handler_test_setup_factory(
    mock_dependencies_with_essay: MockBotDependencies,
    mock_essay_service: MagicMock,
):
    """Factory fixture for creating handler test setup with essay service.

    Similar to handler_test_setup_factory but includes essay service mocking.
    The setup includes essay_service attribute for test assertions.

    Usage:
        def test_essay_handler(essay_handler_test_setup_factory):
            setup = essay_handler_test_setup_factory(
                message_text="/add_essay Answer: test"
            )
            await add_essay_handler(setup.update, setup.context)
            setup.essay_service.create.assert_called_once()
    """

    def factory(
        user_id: int = 12345,
        args: Optional[list[str]] = None,
        enable_shared_tracking: bool = True,
        message_text: str = "",
    ) -> HandlerTestSetup:
        user = MockUser(id=user_id)
        message = MockMessage(
            text=message_text,
            user=user,
            enable_shared_tracking=enable_shared_tracking,
        )
        update = MockUpdate(user=user, message=message)
        context = MockContext(args=args, dependencies=mock_dependencies_with_essay)

        return HandlerTestSetup(
            user=user,
            message=message,
            update=update,
            context=context,
            essay_service=mock_essay_service,
        )

    return factory
