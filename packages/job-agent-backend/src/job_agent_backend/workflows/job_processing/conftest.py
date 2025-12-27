"""Test fixtures for job processing workflow tests."""

from unittest.mock import MagicMock

import numpy as np
import pytest


@pytest.fixture
def sample_cv_content():
    """Sample CV content for testing."""
    return """
    Professional Experience:
    - 5+ years of Python development
    - Expertise in Django, Flask, FastAPI
    - Experience with PostgreSQL and MongoDB
    - Strong background in RESTful API design
    - Proficient in Docker and Kubernetes

    Skills:
    - Languages: Python, JavaScript, SQL
    - Frameworks: Django, React
    - Tools: Git, Docker, Jenkins
    """


@pytest.fixture
def sample_job_dict():
    """Sample JobDict for testing."""
    return {
        "job_id": 12345,
        "title": "Senior Python Developer",
        "url": "https://example.com/jobs/12345",
        "description": """
        We are looking for a Senior Python Developer with strong experience in:
        - Python (5+ years required)
        - Django or Flask
        - PostgreSQL
        - Docker and Kubernetes (nice to have)
        - RESTful API design

        Responsibilities:
        - Design and implement backend services
        - Mentor junior developers
        - Participate in code reviews
        """,
        "company": {"name": "Example Corp", "website": "https://example.com"},
        "category": "Software Development",
        "date_posted": "2024-01-15T10:00:00Z",
        "valid_through": "2024-02-15T10:00:00Z",
        "employment_type": "FULL_TIME",
        "salary": {"currency": "USD", "min_value": 120000.0, "max_value": 160000.0},
        "experience_months": 36.0,
        "location": {"region": "New York, NY", "is_remote": True, "can_apply": True},
        "industry": "Information Technology",
    }


@pytest.fixture
def sample_irrelevant_job_dict():
    """Sample irrelevant JobDict for testing."""
    return {
        "job_id": 67890,
        "title": "Senior Java Architect",
        "url": "https://example.com/jobs/67890",
        "description": """
        We are looking for a Senior Java Architect with:
        - 10+ years of Java/J2EE experience (required)
        - Spring Boot, Hibernate
        - Microservices architecture
        - AWS or Azure cloud experience

        No Python experience needed.
        """,
        "company": {"name": "Java Corp", "website": "https://javacorp.com"},
        "category": "Software Architecture",
        "date_posted": "2024-01-16T10:00:00Z",
        "valid_through": "2024-02-16T10:00:00Z",
        "employment_type": "FULL_TIME",
        "salary": {"currency": "USD", "min_value": 150000.0, "max_value": 200000.0},
        "experience_months": 120.0,
        "location": {"region": "Seattle, WA", "is_remote": False, "can_apply": True},
        "industry": "Enterprise Software",
    }


@pytest.fixture
def job_repository_factory_stub():
    """Provide a stub job repository factory."""

    def factory():
        repository = MagicMock()
        repository.create.return_value = MagicMock(id=1)
        return repository

    return factory


@pytest.fixture
def mock_embedding_model_factory():
    """Factory fixture for creating mock embedding models with controlled similarity scores.

    Creates embedding models that produce embeddings with a desired cosine similarity.
    This is useful for testing relevance checks where similarity >= 0.4 means relevant
    and similarity < 0.4 means irrelevant.

    Usage:
        def test_relevant_job(mock_embedding_model_factory):
            mock_model = mock_embedding_model_factory(similarity_score=0.8)
            # mock_model.embed_query will return embeddings with 0.8 similarity

        def test_irrelevant_job(mock_embedding_model_factory):
            mock_model = mock_embedding_model_factory(similarity_score=0.3)
            # mock_model.embed_query will return embeddings with 0.3 similarity

    Note: The factory uses simple unit vectors to produce predictable cosine similarity.
    The first call to embed_query returns the CV embedding, the second returns the job embedding.
    """

    def factory(similarity_score: float) -> MagicMock:
        mock_model = MagicMock()

        # Create two embeddings that will produce the desired similarity score
        # Using simple vectors for predictable cosine similarity
        cv_embedding = np.array([1.0, 0.0, 0.0])
        job_embedding = np.array([similarity_score, np.sqrt(1 - similarity_score**2), 0.0])

        # Normalize to unit vectors for consistent cosine similarity
        cv_embedding = cv_embedding / np.linalg.norm(cv_embedding)
        job_embedding = job_embedding / np.linalg.norm(job_embedding)

        # Set up the mock to return these embeddings
        # First call returns CV embedding, second call returns job embedding
        mock_model.embed_query.side_effect = [cv_embedding.tolist(), job_embedding.tolist()]

        return mock_model

    return factory
