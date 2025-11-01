from typing import TypedDict


class PIIRemovalState(TypedDict):
    """State schema for PII removal workflow.

    Attributes:
        cv_context: CV/resume content to process
    """
    cv_context: str
