"""Extract skills node for the multiagent workflow.

This node extracts must-have skills from a single job description using OpenAI.
"""

from .node import extract_must_have_skills_node

__all__ = ["extract_must_have_skills_node"]
