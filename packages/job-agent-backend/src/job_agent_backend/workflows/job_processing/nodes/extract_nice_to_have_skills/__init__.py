"""Extract nice-to-have skills node for the workflows workflow.

This node extracts nice-to-have skills from a single job description using OpenAI.
"""

from .node import create_extract_nice_to_have_skills_node

__all__ = ["create_extract_nice_to_have_skills_node"]
