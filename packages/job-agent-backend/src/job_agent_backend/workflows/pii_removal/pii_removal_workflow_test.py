"""Tests for PII removal workflow graph structure."""

from unittest.mock import MagicMock

import pytest
from langgraph.graph.state import CompiledStateGraph

from .node_names import PIIRemovalNode
from .pii_removal import create_pii_removal_workflow


@pytest.fixture
def mock_model_factory() -> MagicMock:
    """Create a mock model factory for testing workflow structure."""
    return MagicMock()


class TestCreatePiiRemovalWorkflow:
    """Test suite for create_pii_removal_workflow function."""

    def test_create_pii_removal_workflow_returns_compiled_state_graph(
        self, mock_model_factory
    ):
        """Test that create_pii_removal_workflow returns a CompiledStateGraph."""
        workflow = create_pii_removal_workflow(mock_model_factory)

        assert isinstance(workflow, CompiledStateGraph)

    def test_create_pii_removal_workflow_has_correct_name(self, mock_model_factory):
        """Test that workflow has the expected name."""
        workflow = create_pii_removal_workflow(mock_model_factory)

        assert workflow.name == "PIIRemovalWorkflow"

    def test_create_pii_removal_workflow_has_remove_pii_node(self, mock_model_factory):
        """Test that workflow contains the remove_pii node."""
        workflow = create_pii_removal_workflow(mock_model_factory)
        nodes = workflow.get_graph().nodes

        assert PIIRemovalNode.REMOVE_PII in nodes

    def test_create_pii_removal_workflow_has_correct_entry_point(
        self, mock_model_factory
    ):
        """Test that workflow entry point is remove_pii node."""
        workflow = create_pii_removal_workflow(mock_model_factory)
        graph = workflow.get_graph()

        start_edges = [edge for edge in graph.edges if edge[0] == "__start__"]
        assert len(start_edges) == 1
        assert start_edges[0][1] == PIIRemovalNode.REMOVE_PII

    def test_create_pii_removal_workflow_remove_pii_leads_to_end(
        self, mock_model_factory
    ):
        """Test that remove_pii node transitions to END."""
        workflow = create_pii_removal_workflow(mock_model_factory)
        graph = workflow.get_graph()

        remove_pii_edges = [
            edge for edge in graph.edges if edge[0] == PIIRemovalNode.REMOVE_PII
        ]
        assert len(remove_pii_edges) == 1
        assert remove_pii_edges[0][1] == "__end__"
