"""Access control module for Telegram bot.

This module provides functionality to restrict bot access to a configurable
list of allowed Telegram user IDs.
"""

import functools
import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class AccessControlConfig:
    """Configuration for access control.

    Attributes:
        allowed_ids: Set of Telegram user IDs that are allowed to use the bot.
                    If empty, access control is disabled and all users are allowed.
    """

    allowed_ids: frozenset[int]


def parse_allowed_user_ids(env_value: Optional[str]) -> frozenset[int]:
    """Parse allowed user IDs from environment variable value.

    The environment variable should contain a comma-separated list of
    Telegram user IDs. Whitespace is trimmed around each ID.
    Invalid (non-numeric, negative, or zero) entries are skipped with a warning.

    Args:
        env_value: The value of TELEGRAM_ALLOWED_USER_IDS environment variable,
                  or None if not set.

    Returns:
        A frozenset of valid Telegram user IDs. Returns an empty set if
        env_value is None, empty, or contains no valid IDs.
    """
    if not env_value:
        return frozenset()

    allowed_ids: set[int] = set()

    for entry in env_value.split(","):
        entry = entry.strip()
        if not entry:
            continue

        try:
            user_id = int(entry)
            if user_id <= 0:
                logger.warning("Invalid Telegram user ID (must be positive): %s", entry)
                continue
            allowed_ids.add(user_id)
        except ValueError:
            logger.warning("Invalid Telegram user ID (not a number): %s", entry)

    return frozenset(allowed_ids)


def is_user_allowed(user_id: int, config: AccessControlConfig) -> bool:
    """Check if a user is allowed to access the bot.

    Args:
        user_id: The Telegram user ID to check.
        config: The access control configuration.

    Returns:
        True if access control is disabled (allowed_ids is empty) or
        if the user ID is in the allowed set. False otherwise.
    """
    if not config.allowed_ids:
        # Access control disabled - allow all users (backward compatible)
        return True

    return user_id in config.allowed_ids


def require_access(handler: Callable) -> Callable:
    """Decorator to enforce access control on a handler.

    The decorator checks if the user is allowed to access the bot based on
    the AccessControlConfig stored in context.application.bot_data["access_control"].

    If access control is disabled (config not set or allowed_ids is empty),
    all users are allowed (backward compatible behavior).

    If the user is unauthorized:
    - The handler is NOT called
    - A WARNING is logged with user ID, username, and interaction type
    - No response is sent (silent ignore)

    Args:
        handler: The async handler function to wrap.

    Returns:
        Wrapped async handler function.
    """

    @functools.wraps(handler)
    async def wrapper(update, context):
        # Get access control config from bot_data
        config = context.application.bot_data.get("access_control")

        # If config is missing, allow all (backward compatible)
        if config is None:
            return await handler(update, context)

        # Check if user exists
        user = update.effective_user
        if user is None:
            # No user info available - skip silently
            logger.warning("Access control: No effective_user in update")
            return None

        user_id = user.id
        username = getattr(user, "username", None)

        # Check if user is allowed
        if is_user_allowed(user_id, config):
            return await handler(update, context)

        # User is unauthorized - determine interaction type for logging
        interaction_type = _get_interaction_type(update)

        # Log unauthorized access
        username_str = f" (@{username})" if username else ""
        logger.warning(
            "Unauthorized access attempt: user_id=%s%s, interaction=%s",
            user_id,
            username_str,
            interaction_type,
        )

        # Silent ignore - do not call handler, do not respond
        return None

    return wrapper


def _get_interaction_type(update) -> str:
    """Determine the type of interaction from an update.

    Args:
        update: The Telegram Update object.

    Returns:
        A string describing the interaction type (e.g., "/start", "document upload").
    """
    message = update.message

    if message is None:
        return "unknown"

    # Check for document upload
    if message.document is not None:
        return "document upload"

    # Check for command
    text = getattr(message, "text", None)
    if text and text.startswith("/"):
        # Extract command (first word)
        command = text.split()[0]
        return command

    return "message"
