"""Tests for add essay handler."""

from unittest.mock import MagicMock


from telegram_bot.access_control import AccessControlConfig, require_access
from telegram_bot.conftest import MockUser, MockMessage, MockUpdate, MockContext
from telegram_bot.handlers.add_essay import add_essay_handler


def _get_create_call_essay_data(mock_service: MagicMock) -> dict:
    """Extract essay_data dict from create() call args."""
    call_args = mock_service.create.call_args
    return call_args[0][0] if call_args[0] else call_args[1].get("essay_data")


class TestAddEssayHandlerInstructions:
    """Tests for showing usage instructions."""

    async def test_shows_instructions_when_command_without_content(
        self, essay_handler_test_setup_factory
    ):
        """When /add_essay is sent without any content, show format instructions."""
        setup = essay_handler_test_setup_factory(message_text="/add_essay")

        await add_essay_handler(setup.update, setup.context)

        assert any(
            "Answer:" in text for text in setup.message._reply_texts
        ), f"Expected instructions mentioning 'Answer:' format, got: {setup.message._reply_texts}"


class TestAddEssayHandlerParsing:
    """Tests for message content parsing."""

    async def test_parses_question_and_answer_format(self, essay_handler_test_setup_factory):
        """When message has both Question: and Answer: markers, extract both fields."""
        content = "Question: What is your experience?\nAnswer: I have 5 years of experience."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert essay_data["question"] == "What is your experience?"
        assert essay_data["answer"] == "I have 5 years of experience."

    async def test_parses_answer_only_format(self, essay_handler_test_setup_factory):
        """When message has only Answer: marker, extract answer with empty question."""
        content = "Answer: I have extensive project management experience."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert essay_data.get("question") is None or essay_data.get("question") == ""
        assert essay_data["answer"] == "I have extensive project management experience."

    async def test_parses_case_insensitive_markers(self, essay_handler_test_setup_factory):
        """Markers should be case-insensitive (ANSWER:, answer:, Answer: all work)."""
        content = "question: My skill?\nanswer: Python programming."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert essay_data["answer"] == "Python programming."

    async def test_parses_multiline_answer_content(self, essay_handler_test_setup_factory):
        """Answer content can span multiple lines."""
        content = """Question: Describe your experience.
Answer: I have worked on many projects.
They include web development.
And mobile applications."""
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert "many projects" in essay_data["answer"]
        assert "web development" in essay_data["answer"]
        assert "mobile applications" in essay_data["answer"]

    async def test_trims_whitespace_from_parsed_fields(self, essay_handler_test_setup_factory):
        """Whitespace around parsed question and answer should be trimmed."""
        content = "Question:   Spaced question   \nAnswer:   Spaced answer   "
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert essay_data["question"] == "Spaced question"
        assert essay_data["answer"] == "Spaced answer"


class TestAddEssayHandlerValidation:
    """Tests for input validation."""

    async def test_returns_error_when_missing_answer_marker(self, essay_handler_test_setup_factory):
        """When message lacks Answer: marker, return format error."""
        content = "I have 10 years of experience in software development."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_not_called()

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "Answer:" in text or "Invalid format" in text or "format" in text.lower()
            for text in all_messages
        ), f"Expected format error message, got: {all_messages}"

    async def test_returns_error_when_answer_is_empty(self, essay_handler_test_setup_factory):
        """When Answer: is present but content is empty/whitespace, return error."""
        content = "Question: My question\nAnswer:   "
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_not_called()

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "empty" in text.lower() or "cannot be empty" in text.lower() for text in all_messages
        ), f"Expected empty answer error, got: {all_messages}"

    async def test_returns_error_when_only_question_marker_present(
        self, essay_handler_test_setup_factory
    ):
        """When only Question: marker is present without Answer:, return error."""
        content = "Question: What is your experience?"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_not_called()

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "Answer:" in text or "Invalid format" in text or "format" in text.lower()
            for text in all_messages
        ), f"Expected format error message, got: {all_messages}"


class TestAddEssayHandlerProcessing:
    """Tests for essay save processing."""

    async def test_sends_processing_message_before_save(self, essay_handler_test_setup_factory):
        """Processing indicator should be shown before calling essay service."""
        content = "Answer: My experience includes..."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        assert any(
            "processing" in text.lower() or "Processing" in text
            for text in setup.message._reply_texts
        ), f"Expected processing message, got: {setup.message._reply_texts}"

    async def test_calls_essay_service_create_with_essay_data(
        self, essay_handler_test_setup_factory
    ):
        """Handler should call essay service create with EssayCreate-compatible data."""
        content = "Question: What skills do you have?\nAnswer: Python, SQL, and AWS."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert "answer" in essay_data
        assert essay_data["answer"] == "Python, SQL, and AWS."


class TestAddEssayHandlerSuccess:
    """Tests for successful essay creation."""

    async def test_shows_success_message_with_essay_id(self, essay_handler_test_setup_factory):
        """On successful save, show success message containing the essay ID."""
        content = "Answer: My leadership experience..."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "42" in text and ("success" in text.lower() or "saved" in text.lower())
            for text in all_messages
        ), f"Expected success message with ID 42, got: {all_messages}"

    async def test_success_message_edits_processing_message(self, essay_handler_test_setup_factory):
        """Success message should edit the processing message, not send new reply."""
        content = "Answer: Test content"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        assert any(
            "success" in text.lower() or "saved" in text.lower()
            for text in setup.message._edited_texts
        ), f"Expected edited success message, got: {setup.message._edited_texts}"


class TestAddEssayHandlerErrors:
    """Tests for error handling."""

    async def test_handles_essay_validation_error(self, essay_handler_test_setup_factory):
        """When essay service raises EssayValidationError, show validation message."""
        from job_agent_platform_contracts.essay_repository import EssayValidationError

        content = "Answer: Some content"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")
        setup.essay_service.create.side_effect = EssayValidationError(
            field="answer", message="Answer too short"
        )

        await add_essay_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "validation" in text.lower() or "Answer too short" in text or "failed" in text.lower()
            for text in all_messages
        ), f"Expected validation error message, got: {all_messages}"

    async def test_handles_generic_exception(self, essay_handler_test_setup_factory):
        """When essay service raises generic exception, show generic error message."""
        content = "Answer: Some content"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")
        setup.essay_service.create.side_effect = Exception("Database connection failed")

        await add_essay_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert any(
            "failed" in text.lower() or "error" in text.lower() or "try again" in text.lower()
            for text in all_messages
        ), f"Expected error message, got: {all_messages}"

    async def test_does_not_expose_internal_error_details(self, essay_handler_test_setup_factory):
        """Internal error details should not be exposed to user."""
        content = "Answer: Some content"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")
        setup.essay_service.create.side_effect = Exception(
            "FATAL: connection refused to postgres:5432"
        )

        await add_essay_handler(setup.update, setup.context)

        all_messages = setup.message._reply_texts + setup.message._edited_texts
        assert not any(
            "postgres" in text.lower() or "5432" in text or "connection refused" in text.lower()
            for text in all_messages
        ), f"Internal error details leaked in: {all_messages}"


class TestAddEssayHandlerEdgeCases:
    """Tests for edge cases and boundary conditions."""

    async def test_returns_early_when_no_message(self, essay_handler_test_setup_factory):
        """Handler should return early when update has no message."""
        setup = essay_handler_test_setup_factory()
        update = MagicMock()
        update.message = None

        # Handler should not raise when update.message is None
        result = await add_essay_handler(update, setup.context)

        assert result is None
        setup.essay_service.create.assert_not_called()

    async def test_handles_empty_question_between_markers(self, essay_handler_test_setup_factory):
        """When Question: is present but empty, store as empty/null question."""
        content = "Question:\nAnswer: My answer here"
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert essay_data.get("question") in (None, "")
        assert essay_data["answer"] == "My answer here"

    async def test_handles_answer_marker_within_content(self, essay_handler_test_setup_factory):
        """Content containing 'Answer:' as text (not marker) should be handled."""
        content = "Question: How do you Answer: questions?\nAnswer: I think carefully."
        setup = essay_handler_test_setup_factory(message_text=f"/add_essay {content}")

        await add_essay_handler(setup.update, setup.context)

        setup.essay_service.create.assert_called_once()
        essay_data = _get_create_call_essay_data(setup.essay_service)

        assert "think carefully" in essay_data["answer"]


class TestAddEssayHandlerAccessControl:
    """Tests for access control integration."""

    async def test_unauthorized_user_cannot_access_handler(self):
        """Handler wrapped with require_access should block unauthorized users."""
        handler_called = False

        @require_access
        async def wrapped_add_essay_handler(update, context):
            nonlocal handler_called
            handler_called = True
            return await add_essay_handler(update, context)

        user = MockUser(id=99999)  # Not in allowed list
        message = MockMessage(
            text="/add_essay Answer: test content",
            user=user,
            enable_shared_tracking=True,
        )
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345, 67890})  # 99999 not included
        )

        await wrapped_add_essay_handler(update, context)

        assert handler_called is False, "Handler should NOT be called for unauthorized user"
        assert len(message._reply_texts) == 0, "No response should be sent to unauthorized user"

    async def test_authorized_user_can_access_handler(self):
        """Handler wrapped with require_access should allow authorized users."""
        handler_invoked = False

        @require_access
        async def wrapped_add_essay_handler(update, context):
            nonlocal handler_invoked
            handler_invoked = True
            # Original handler would be called here; for this test we just verify invocation

        user = MockUser(id=12345)  # In allowed list
        message = MockMessage(
            text="/add_essay Answer: test content",
            user=user,
            enable_shared_tracking=True,
        )
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345, 67890})
        )

        await wrapped_add_essay_handler(update, context)

        assert handler_invoked is True, "Handler should be called for authorized user"

    async def test_access_control_disabled_allows_all_users(self):
        """When access control is disabled (empty allowed_ids), all users allowed."""
        handler_invoked = False

        @require_access
        async def wrapped_add_essay_handler(update, context):
            nonlocal handler_invoked
            handler_invoked = True

        user = MockUser(id=99999)  # Any user
        message = MockMessage(
            text="/add_essay Answer: test",
            user=user,
            enable_shared_tracking=True,
        )
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset()  # Empty = disabled
        )

        await wrapped_add_essay_handler(update, context)

        assert handler_invoked is True, "Handler should be called when access control disabled"
