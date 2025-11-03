"""Messages for start handler."""


def get_welcome_message(first_name: str) -> str:
    """Get welcome message for user.

    Args:
        first_name: User's first name

    Returns:
        Formatted welcome message
    """
    return (
        f"👋 Hello {first_name}!\n\n"
        "I'm the Job Agent Bot. I help you find and analyze job opportunities "
        "that match your profile.\n\n"
        "To get started:\n"
        "1. Upload your CV as a PDF document\n"
        "2. Use /search to find relevant jobs\n\n"
        "Use /help to see all available commands."
    )
