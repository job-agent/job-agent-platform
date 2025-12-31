"""Message templates for essays listing handler.

This module contains all user-facing message templates for the
/essays command and pagination functionality.
"""

# Page header template
PAGE_HEADER = "Page {page} of {total_pages}"

# Empty state message
EMPTY_LIST = "No essays found. Use /add_essay to create your first essay."

# Error message
ERROR_LOADING = "Failed to load essays. Please try again."

# Navigation button labels
BTN_PREVIOUS = "Previous"
BTN_NEXT = "Next"

# Boundary messages for disabled buttons
MSG_FIRST_PAGE = "You are on the first page."
MSG_LAST_PAGE = "You are on the last page."

# Delete button label
BTN_DELETE = "Delete"

# Delete confirmation prompt
CONFIRM_DELETE_PROMPT = "Are you sure you want to delete this essay?\n\nID: {essay_id}"

# Confirmation buttons
BTN_CONFIRM_DELETE = "Yes, Delete"
BTN_CANCEL_DELETE = "Cancel"

# Success message
MSG_ESSAY_DELETED = "Essay deleted successfully."

# Error messages
MSG_ESSAY_NOT_FOUND = "Essay not found. It may have already been deleted."
MSG_DELETE_FAILED = "Failed to delete essay. Please try again."
