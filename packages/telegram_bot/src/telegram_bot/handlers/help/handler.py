"""Help command handler for Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command.

    Args:
        update: Telegram update object
        context: Callback context
    """
    help_text = """
📚 Available Commands:

/start - Start the bot and see welcome message
/help - Show this help message
/search - Search for jobs with optional parameters
/status - Check if a search is currently running
/cancel - Cancel the current job search

🔍 Search Examples:

/search
  → Search with default parameters (salary=4000, remote)

/search salary=5000
  → Search for jobs with minimum salary of 5000

/search salary=6000 employment=remote page=1
  → Custom search with multiple parameters

⚙️ Available Parameters:
- salary: Minimum salary (default: 4000)
- employment: Employment type (default: "remote")
- page: Page number (default: 1)
- timeout: Request timeout in seconds (default: 30)

📝 Note: Job results are processed using your CV and sent back to you automatically.
"""
    await update.message.reply_text(help_text)
