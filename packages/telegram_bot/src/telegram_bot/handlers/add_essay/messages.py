"""Message templates for add essay handler."""

INFO_INSTRUCTIONS = """To add an essay, use one of these formats:

With question:
/add_essay Question: Tell me about a time you led a team Answer: I led a team of 5 engineers to deliver a microservices migration on schedule.

Answer only:
/add_essay Answer: I have 5 years of experience with Python and cloud infrastructure.

The 'Answer:' field is required."""

INFO_PROCESSING = """Processing your essay..."""

SUCCESS_MESSAGE = """Essay saved successfully! (ID: {id})"""

ERROR_INVALID_FORMAT = """Invalid format.

Please include 'Answer:' followed by your text.

Examples:

/add_essay Question: Tell me about a time you led a team Answer: I led a team of 5 engineers to deliver a microservices migration on schedule.

/add_essay Answer: I have 5 years of experience with Python and cloud infrastructure."""

ERROR_ANSWER_EMPTY = """Answer cannot be empty.

Please provide content after 'Answer:'."""

ERROR_VALIDATION_FAILED = """Failed to validate essay.

{message}"""

ERROR_PROCESSING_FAILED = """Failed to save essay. Please try again."""
