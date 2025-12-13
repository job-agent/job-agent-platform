"""Tests for check_job_relevance routing logic."""

from ...node_names import JobProcessingNode
from .routing import route_after_relevance_check


class TestRouteAfterRelevanceCheck:
    """Tests for route_after_relevance_check function."""

    def test_returns_end_when_job_irrelevant(self):
        """Routing returns 'end' when is_relevant is False."""
        state = {
            "job": {"job_id": 1},
            "status": "started",
            "cv_context": "Some CV",
            "is_relevant": False,
        }

        result = route_after_relevance_check(state)

        assert result == "end"

    def test_returns_extract_nodes_when_job_relevant(self):
        """Routing returns both extract nodes when is_relevant is True."""
        state = {
            "job": {"job_id": 1},
            "status": "started",
            "cv_context": "Some CV",
            "is_relevant": True,
        }

        result = route_after_relevance_check(state)

        assert result == [
            JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
            JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
        ]

    def test_defaults_to_relevant_when_is_relevant_missing(self):
        """Routing defaults to relevant (extract nodes) when is_relevant not in state."""
        state = {
            "job": {"job_id": 1},
            "status": "started",
            "cv_context": "Some CV",
        }

        result = route_after_relevance_check(state)

        assert result == [
            JobProcessingNode.EXTRACT_MUST_HAVE_SKILLS,
            JobProcessingNode.EXTRACT_NICE_TO_HAVE_SKILLS,
        ]
