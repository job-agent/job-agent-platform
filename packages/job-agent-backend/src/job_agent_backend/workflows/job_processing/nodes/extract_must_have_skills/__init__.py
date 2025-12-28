"""Extract skills node for the workflows workflow.

This node extracts must-have skills from a single job description using OpenAI.
"""

from .node import create_extract_must_have_skills_node

__all__ = ["create_extract_must_have_skills_node"]
