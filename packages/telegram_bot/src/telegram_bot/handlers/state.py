"""Shared state for Telegram bot handlers.

This module contains shared state used across multiple handlers.
"""

from typing import Dict

active_searches: Dict[int, bool] = {}
