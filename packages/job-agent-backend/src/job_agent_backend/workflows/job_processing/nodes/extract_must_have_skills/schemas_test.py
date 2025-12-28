"""Tests for SkillsExtraction schema with 2D skill structure.

These tests verify the new 2D list format where:
- Outer list represents AND relationships (all groups required)
- Inner lists represent OR relationships (alternatives within a group)

Example: [["JavaScript", "Python"], ["React"]] means "(JavaScript OR Python) AND React"
"""

import pytest
from pydantic import ValidationError

from .schemas import SkillsExtraction


class TestSkillsExtractionSchema:
    """Tests for SkillsExtraction Pydantic schema with 2D skill structure."""

    def test_accepts_empty_outer_list(self):
        """Schema accepts empty outer list for no skills extracted."""
        extraction = SkillsExtraction(skills=[])

        assert extraction.skills == []

    def test_accepts_single_skill_as_single_item_inner_list(self):
        """Schema accepts a solo skill wrapped in single-item inner list."""
        extraction = SkillsExtraction(skills=[["React"]])

        assert extraction.skills == [["React"]]

    def test_accepts_multiple_solo_skill_groups(self):
        """Schema accepts multiple single-skill groups (all AND relationships)."""
        extraction = SkillsExtraction(skills=[["Python"], ["Django"], ["PostgreSQL"]])

        assert extraction.skills == [["Python"], ["Django"], ["PostgreSQL"]]

    def test_accepts_or_group_with_two_alternatives(self):
        """Schema accepts inner list with two alternatives (OR relationship)."""
        extraction = SkillsExtraction(skills=[["JavaScript", "Python"]])

        assert extraction.skills == [["JavaScript", "Python"]]

    def test_accepts_or_group_with_multiple_alternatives(self):
        """Schema accepts inner list with more than two alternatives."""
        extraction = SkillsExtraction(skills=[["React", "Vue", "Angular"]])

        assert extraction.skills == [["React", "Vue", "Angular"]]

    def test_accepts_mixed_solo_and_or_groups(self):
        """Schema accepts combination of solo skills and OR groups."""
        extraction = SkillsExtraction(
            skills=[["JavaScript", "Python"], ["React"], ["Docker", "Kubernetes"]]
        )

        assert extraction.skills == [
            ["JavaScript", "Python"],
            ["React"],
            ["Docker", "Kubernetes"],
        ]

    def test_default_value_is_empty_list(self):
        """Schema defaults to empty list when skills not provided."""
        extraction = SkillsExtraction()

        assert extraction.skills == []

    def test_rejects_flat_string_list(self):
        """Schema rejects flat list of strings (old format)."""
        with pytest.raises(ValidationError):
            SkillsExtraction(skills=["Python", "Django", "PostgreSQL"])

    def test_rejects_mixed_flat_and_nested(self):
        """Schema rejects mix of strings and lists."""
        with pytest.raises(ValidationError):
            SkillsExtraction(skills=["Python", ["Django", "Flask"]])

    def test_preserves_skill_order_in_outer_list(self):
        """Schema preserves order of skill groups in outer list."""
        skills = [["A"], ["B"], ["C"], ["D"]]
        extraction = SkillsExtraction(skills=skills)

        assert extraction.skills == [["A"], ["B"], ["C"], ["D"]]

    def test_preserves_skill_order_in_inner_lists(self):
        """Schema preserves order of alternatives within inner lists."""
        skills = [["JavaScript", "TypeScript", "Python"]]
        extraction = SkillsExtraction(skills=skills)

        assert extraction.skills[0] == ["JavaScript", "TypeScript", "Python"]

    def test_accepts_empty_inner_lists(self):
        """Schema accepts empty inner lists (edge case).

        While semantically questionable, empty inner lists should be
        structurally valid per the schema.
        """
        extraction = SkillsExtraction(skills=[[]])

        assert extraction.skills == [[]]

    def test_accepts_skills_with_special_characters(self):
        """Schema accepts skills containing special characters."""
        skills = [["C++", "C#"], ["Node.js"], ["AWS/GCP"]]
        extraction = SkillsExtraction(skills=skills)

        assert extraction.skills == [["C++", "C#"], ["Node.js"], ["AWS/GCP"]]

    def test_skill_field_description_documents_2d_structure(self):
        """Schema field description should document 2D list semantics."""
        field_info = SkillsExtraction.model_fields["skills"]

        # The description should mention the 2D structure, OR/AND relationships
        description = field_info.description or ""
        assert "list" in description.lower() or "group" in description.lower()
