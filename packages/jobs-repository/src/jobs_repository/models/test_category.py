"""Tests for Category model."""

from jobs_repository.models import Job, Category


class TestCategoryModel:
    """Test suite for Category model."""

    def test_repr(self, db_session):
        """Test Category __repr__ method."""
        category = Category(name="Engineering")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        repr_str = repr(category)

        assert "Category" in repr_str
        assert "Engineering" in repr_str
        assert str(category.id) in repr_str

    def test_repr_without_id(self):
        """Test Category __repr__ before persistence."""
        category = Category(name="Design")

        repr_str = repr(category)

        assert "Category" in repr_str
        assert "Design" in repr_str

    def test_name_field(self, db_session):
        """Test Category name field."""
        category = Category(name="Data Science")
        db_session.add(category)
        db_session.commit()

        assert category.name == "Data Science"

    def test_jobs_relationship(self, db_session, sample_category):
        """Test Category jobs relationship."""
        job = Job(title="Test Job", category_id=sample_category.id)
        db_session.add(job)
        db_session.commit()

        assert len(sample_category.jobs) == 1
        assert sample_category.jobs[0].title == "Test Job"
