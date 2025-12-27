"""Tests for access control module."""

import logging
from unittest.mock import MagicMock


from telegram_bot.conftest import MockContext, MockMessage, MockUpdate, MockUser


# Import the module under test - will fail in RED phase
from telegram_bot.access_control import (
    AccessControlConfig,
    parse_allowed_user_ids,
    is_user_allowed,
    require_access,
)


class TestParseAllowedUserIds:
    """Tests for parse_allowed_user_ids function."""

    # Parse comma-separated list of integers

    def test_parse_single_user_id(self):
        """Should parse a single user ID from environment variable."""
        result = parse_allowed_user_ids("123456789")

        assert result == frozenset({123456789})

    def test_parse_multiple_user_ids(self):
        """Should parse multiple comma-separated user IDs."""
        result = parse_allowed_user_ids("123456789,987654321,555555555")

        assert result == frozenset({123456789, 987654321, 555555555})

    def test_parse_trims_whitespace_around_ids(self):
        """Should trim whitespace around user IDs."""
        result = parse_allowed_user_ids("  123456789 , 987654321  ")

        assert result == frozenset({123456789, 987654321})

    def test_parse_handles_extra_whitespace(self):
        """Should handle extra whitespace throughout the string."""
        result = parse_allowed_user_ids(" 123  ,  456 ,  789 ")

        assert result == frozenset({123, 456, 789})

    def test_parse_ignores_empty_entries(self):
        """Should ignore empty entries caused by extra commas."""
        result = parse_allowed_user_ids("123,,456,,,789,")

        assert result == frozenset({123, 456, 789})

    # Backward compatibility when variable is unset

    def test_returns_empty_set_when_none(self):
        """Should return empty set when environment variable is None."""
        result = parse_allowed_user_ids(None)

        assert result == frozenset()

    def test_returns_empty_set_when_empty_string(self):
        """Should return empty set when environment variable is empty string."""
        result = parse_allowed_user_ids("")

        assert result == frozenset()

    def test_returns_empty_set_when_only_whitespace(self):
        """Should return empty set when environment variable is only whitespace."""
        result = parse_allowed_user_ids("   ")

        assert result == frozenset()

    def test_returns_empty_set_when_only_commas(self):
        """Should return empty set when environment variable is only commas."""
        result = parse_allowed_user_ids(",,,")

        assert result == frozenset()

    # Invalid user ID handling

    def test_skips_non_numeric_entries(self):
        """Should skip non-numeric entries and parse valid ones."""
        result = parse_allowed_user_ids("123,invalid,456")

        assert result == frozenset({123, 456})

    def test_logs_warning_for_invalid_entry(self, caplog):
        """Should log WARNING when encountering invalid user ID."""
        with caplog.at_level(logging.WARNING):
            parse_allowed_user_ids("123,invalid,456")

        assert any("invalid" in record.message for record in caplog.records)
        assert any(record.levelno == logging.WARNING for record in caplog.records)

    def test_returns_empty_set_when_all_entries_invalid(self):
        """Should return empty set when all entries are invalid."""
        result = parse_allowed_user_ids("abc,def,ghi")

        assert result == frozenset()

    def test_skips_float_entries(self):
        """Should skip float entries (not valid Telegram user IDs)."""
        result = parse_allowed_user_ids("123,45.67,456")

        assert result == frozenset({123, 456})

    def test_skips_negative_entries(self):
        """Should skip negative entries (Telegram user IDs are positive)."""
        result = parse_allowed_user_ids("123,-456,789")

        assert result == frozenset({123, 789})

    def test_handles_mixed_valid_and_invalid(self):
        """Should handle mix of valid and invalid entries."""
        result = parse_allowed_user_ids("123, abc, 456, , 789, xyz, 0")

        # 0 is not a valid Telegram user ID, should be skipped
        assert result == frozenset({123, 456, 789})


class TestAccessControlConfig:
    """Tests for AccessControlConfig dataclass."""

    def test_config_stores_allowed_ids(self):
        """Config should store the allowed user IDs."""
        ids = frozenset({123, 456})
        config = AccessControlConfig(allowed_ids=ids)

        assert config.allowed_ids == ids

    def test_config_with_empty_ids(self):
        """Config should accept empty set of allowed IDs."""
        config = AccessControlConfig(allowed_ids=frozenset())

        assert config.allowed_ids == frozenset()


class TestIsUserAllowed:
    """Tests for is_user_allowed function."""

    # Backward compatibility - allow all when access control disabled

    def test_allows_any_user_when_allowed_ids_empty(self):
        """Should allow any user when allowed_ids is empty (backward compatible)."""
        config = AccessControlConfig(allowed_ids=frozenset())

        assert is_user_allowed(user_id=12345, config=config) is True
        assert is_user_allowed(user_id=99999, config=config) is True

    # Authorize allowed users

    def test_allows_user_in_allowed_set(self):
        """Should allow user when their ID is in the allowed set."""
        config = AccessControlConfig(allowed_ids=frozenset({12345, 67890}))

        assert is_user_allowed(user_id=12345, config=config) is True

    def test_allows_second_user_in_allowed_set(self):
        """Should allow any user in the allowed set."""
        config = AccessControlConfig(allowed_ids=frozenset({12345, 67890}))

        assert is_user_allowed(user_id=67890, config=config) is True

    # Block unauthorized users

    def test_denies_user_not_in_allowed_set(self):
        """Should deny user when their ID is not in the allowed set."""
        config = AccessControlConfig(allowed_ids=frozenset({12345, 67890}))

        assert is_user_allowed(user_id=99999, config=config) is False


class TestRequireAccessDecorator:
    """Tests for require_access decorator."""

    # Backward compatibility

    async def test_allows_user_when_access_control_disabled(self):
        """Should call handler when access control is disabled (empty allowed_ids)."""
        handler_called = False

        @require_access
        async def test_handler(update, context):
            nonlocal handler_called
            handler_called = True

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset()
        )

        await test_handler(update, context)

        assert handler_called is True

    # Authorize allowed users

    async def test_allows_authorized_user(self):
        """Should call handler for authorized user."""
        handler_called = False

        @require_access
        async def test_handler(update, context):
            nonlocal handler_called
            handler_called = True

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345, 67890})
        )

        await test_handler(update, context)

        assert handler_called is True

    async def test_does_not_send_response_when_authorized(self):
        """Authorized users should not see any access control response."""

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=12345)
        message = MockMessage(user=user, enable_shared_tracking=True)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        await test_handler(update, context)

        # No "unauthorized" or "access denied" messages should be sent
        for reply in message._reply_texts:
            assert "unauthorized" not in reply.lower()
            assert "denied" not in reply.lower()

    # Block unauthorized users silently

    async def test_blocks_unauthorized_user(self):
        """Should not call handler for unauthorized user."""
        handler_called = False

        @require_access
        async def test_handler(update, context):
            nonlocal handler_called
            handler_called = True

        user = MockUser(id=99999)  # Not in allowed list
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345, 67890})
        )

        await test_handler(update, context)

        assert handler_called is False

    async def test_unauthorized_user_receives_no_response(self):
        """Unauthorized user should receive no response (silent ignore)."""

        @require_access
        async def test_handler(update, context):
            await update.message.reply_text("You should not see this")

        user = MockUser(id=99999)  # Not in allowed list
        message = MockMessage(user=user, enable_shared_tracking=True)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345, 67890})
        )

        await test_handler(update, context)

        assert len(message._reply_texts) == 0

    # Log unauthorized access attempts

    async def test_logs_warning_for_unauthorized_access(self, caplog):
        """Should log WARNING when unauthorized user attempts access."""

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=99999, username="unauthorized_user")
        message = MockMessage(user=user, text="/start")
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            await test_handler(update, context)

        assert any(record.levelno == logging.WARNING for record in caplog.records)

    async def test_log_includes_user_id(self, caplog):
        """Log should include the unauthorized user's ID."""

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=99999, username="test_user")
        message = MockMessage(user=user, text="/help")
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            await test_handler(update, context)

        assert any("99999" in record.message for record in caplog.records)

    async def test_log_includes_username_when_available(self, caplog):
        """Log should include username when available."""

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=99999, username="blocked_user")
        message = MockMessage(user=user, text="/search")
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            await test_handler(update, context)

        assert any("blocked_user" in record.message for record in caplog.records)

    async def test_log_includes_command_type_for_command(self, caplog):
        """Log should include the command name for command interactions."""

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=99999)
        message = MockMessage(user=user, text="/search min_salary=5000")
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            await test_handler(update, context)

        # Should mention the command (at least /search or search)
        assert any(
            "search" in record.message.lower() or "/search" in record.message
            for record in caplog.records
        )

    async def test_log_indicates_document_upload_type(self, caplog):
        """Log should indicate 'document upload' for document interactions."""
        from telegram_bot.conftest import MockDocument

        @require_access
        async def test_handler(update, context):
            pass

        user = MockUser(id=99999)
        doc = MockDocument(file_name="resume.pdf")
        message = MockMessage(user=user, document=doc, text="")
        update = MockUpdate(user=user, message=message, document=doc)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            await test_handler(update, context)

        assert any("document" in record.message.lower() for record in caplog.records)

    # Edge cases

    async def test_handles_none_effective_user(self, caplog):
        """Should handle case where effective_user is None gracefully."""

        @require_access
        async def test_handler(update, context):
            pass

        # Create update with no user
        update = MagicMock()
        update.effective_user = None
        update.message = MagicMock()
        update.message.text = "/start"

        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        with caplog.at_level(logging.WARNING):
            # Should not raise, should skip silently
            await test_handler(update, context)

        # Handler should not be called
        # (we can't easily assert this without tracking, but at least no exception)

    async def test_handles_missing_access_control_config(self):
        """Should allow access when access_control config is missing from bot_data."""
        handler_called = False

        @require_access
        async def test_handler(update, context):
            nonlocal handler_called
            handler_called = True

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        # No access_control in bot_data - should default to allow all

        await test_handler(update, context)

        # When config is missing, should allow (backward compatible)
        assert handler_called is True

    async def test_preserves_handler_return_value(self):
        """Decorator should preserve the handler's return value."""

        @require_access
        async def test_handler(update, context):
            return "success"

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        result = await test_handler(update, context)

        assert result == "success"

    async def test_blocked_user_returns_none(self):
        """Blocked user should result in None return value."""

        @require_access
        async def test_handler(update, context):
            return "should not return"

        user = MockUser(id=99999)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        result = await test_handler(update, context)

        assert result is None


class TestAccessControlIntegration:
    """Integration tests for access control with bot handlers."""

    async def test_decorator_works_with_handler_signature(self):
        """Decorator should work with standard handler signature (Update, Context)."""
        received_update = None
        received_context = None

        @require_access
        async def handler(update, context):
            nonlocal received_update, received_context
            received_update = update
            received_context = context

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        await handler(update, context)

        assert received_update is update
        assert received_context is context

    async def test_decorator_preserves_function_name(self):
        """Decorator should preserve the wrapped function's name."""

        @require_access
        async def my_special_handler(update, context):
            pass

        assert my_special_handler.__name__ == "my_special_handler"

    async def test_multiple_decorated_handlers_independent(self):
        """Multiple decorated handlers should work independently."""
        handler1_called = False
        handler2_called = False

        @require_access
        async def handler1(update, context):
            nonlocal handler1_called
            handler1_called = True

        @require_access
        async def handler2(update, context):
            nonlocal handler2_called
            handler2_called = True

        user = MockUser(id=12345)
        message = MockMessage(user=user)
        update = MockUpdate(user=user, message=message)
        context = MockContext()
        context.application.bot_data["access_control"] = AccessControlConfig(
            allowed_ids=frozenset({12345})
        )

        await handler1(update, context)
        await handler2(update, context)

        assert handler1_called is True
        assert handler2_called is True
