#!/usr/bin/env python3
"""Helper script to authenticate Telegram QA client for the first time."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def main():
    """Authenticate with Telegram and create session file."""
    import os

    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_path = os.getenv("TELEGRAM_QA_SESSION_PATH", "telegram_qa.session")

    print("Authenticating Telegram QA client...")
    print("You'll be prompted for your phone number and verification code.")
    print()

    client = TelegramClient(session_path, api_id, api_hash)

    # start() triggers interactive authentication if needed
    await client.start()

    print("\n✓ Authentication successful!")
    print(f"Session file created: {session_path}")
    print("You can now run E2E tests.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
