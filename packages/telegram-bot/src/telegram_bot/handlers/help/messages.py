"""Messages for help handler."""

HELP_TEXT = """
📚 Available Commands:

/start - Start the bot and see welcome message
/help - Show this help message
/search - Search for jobs with optional parameters
/status - Check if a search is currently running
/cancel - Cancel the current job search

📄 CV Upload:

Before you can search for jobs, you need to upload your CV:
1. Send your CV as a PDF document to this bot
2. Wait for confirmation that your CV was uploaded successfully
3. Use /search to find relevant jobs

Your CV will be stored securely and used to match you with relevant job opportunities.

🔍 Search Examples:

/search
  → Search with default parameters (salary=4000, remote)

/search salary=5000
  → Search for jobs with minimum salary of 5000

/search salary=6000 employment=remote days=7
  → Custom search with multiple parameters

⚙️ Available Parameters:
- salary: Minimum salary (default: 4000)
- employment: Employment type (default: "remote")
- days: Number of days to look back (default: 1)
- timeout: Request timeout in seconds (default: 30)

📝 Note: Job results are processed using your CV and sent back to you automatically.
"""
