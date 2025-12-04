"""Tests for ReferenceDataService class."""

from sqlalchemy import select

from jobs_repository.models import Company, Location, Category, Industry


class TestReferenceDataServiceGetOrCreateCompany:
    """Tests for get_or_create_company method."""

    def test_creates_new_company_when_not_exists(self, reference_data_service, db_session):
        """Test creating a new company when it doesn't exist."""
        company = reference_data_service.get_or_create_company(db_session, "New Company")

        assert company.id is not None
        assert company.name == "New Company"

        db_company = db_session.query(Company).filter_by(name="New Company").first()
        assert db_company is not None
        assert db_company.id == company.id

    def test_returns_existing_company(self, reference_data_service, sample_company, db_session):
        """Test returning existing company instead of creating duplicate."""
        company = reference_data_service.get_or_create_company(db_session, sample_company.name)

        assert company.id == sample_company.id
        assert company.name == sample_company.name

    def test_company_names_are_case_sensitive(self, reference_data_service, db_session):
        """Test that company names are case-sensitive."""
        company1 = reference_data_service.get_or_create_company(db_session, "TechCorp")
        company2 = reference_data_service.get_or_create_company(db_session, "techcorp")

        assert company1.id != company2.id
        assert db_session.query(Company).count() == 2

    def test_flushes_without_committing(self, reference_data_service, db_session):
        """Test that get_or_create flushes to get ID without committing."""
        company = reference_data_service.get_or_create_company(db_session, "Flush Test Company")

        assert company.id is not None

        db_session.rollback()

        stmt = select(Company).where(Company.name == "Flush Test Company")
        result = db_session.scalar(stmt)
        assert result is None

    def test_creates_entity_on_first_call(self, reference_data_service, db_session):
        """Test that get_or_create actually creates entity on first call."""
        stmt = select(Company).where(Company.name == "First Call Company")
        assert db_session.scalar(stmt) is None

        company = reference_data_service.get_or_create_company(db_session, "First Call Company")

        assert company.id is not None
        db_company = db_session.scalar(select(Company).where(Company.name == "First Call Company"))
        assert db_company is not None
        assert db_company.id == company.id


class TestReferenceDataServiceGetOrCreateLocation:
    """Tests for get_or_create_location method."""

    def test_creates_new_location_when_not_exists(self, reference_data_service, db_session):
        """Test creating a new location when it doesn't exist."""
        location = reference_data_service.get_or_create_location(db_session, "Seattle, WA")

        assert location.id is not None
        assert location.region == "Seattle, WA"

        db_location = db_session.query(Location).filter_by(region="Seattle, WA").first()
        assert db_location is not None
        assert db_location.id == location.id

    def test_returns_existing_location(self, reference_data_service, sample_location, db_session):
        """Test returning existing location instead of creating duplicate."""
        location = reference_data_service.get_or_create_location(db_session, sample_location.region)

        assert location.id == sample_location.id
        assert location.region == sample_location.region

    def test_location_regions_are_whitespace_sensitive(self, reference_data_service, db_session):
        """Test that location regions are whitespace-sensitive."""
        location1 = reference_data_service.get_or_create_location(db_session, "San Francisco, CA")
        location2 = reference_data_service.get_or_create_location(db_session, "San Francisco,CA")

        assert location1.id != location2.id
        assert db_session.query(Location).count() == 2


class TestReferenceDataServiceGetOrCreateCategory:
    """Tests for get_or_create_category method."""

    def test_creates_new_category_when_not_exists(self, reference_data_service, db_session):
        """Test creating a new category when it doesn't exist."""
        category = reference_data_service.get_or_create_category(db_session, "Data Science")

        assert category.id is not None
        assert category.name == "Data Science"

        db_category = db_session.query(Category).filter_by(name="Data Science").first()
        assert db_category is not None
        assert db_category.id == category.id

    def test_returns_existing_category(self, reference_data_service, sample_category, db_session):
        """Test returning existing category instead of creating duplicate."""
        category = reference_data_service.get_or_create_category(db_session, sample_category.name)

        assert category.id == sample_category.id
        assert category.name == sample_category.name


class TestReferenceDataServiceGetOrCreateIndustry:
    """Tests for get_or_create_industry method."""

    def test_creates_new_industry_when_not_exists(self, reference_data_service, db_session):
        """Test creating a new industry when it doesn't exist."""
        industry = reference_data_service.get_or_create_industry(db_session, "Healthcare")

        assert industry.id is not None
        assert industry.name == "Healthcare"

        db_industry = db_session.query(Industry).filter_by(name="Healthcare").first()
        assert db_industry is not None
        assert db_industry.id == industry.id

    def test_returns_existing_industry(self, reference_data_service, sample_industry, db_session):
        """Test returning existing industry instead of creating duplicate."""
        industry = reference_data_service.get_or_create_industry(db_session, sample_industry.name)

        assert industry.id == sample_industry.id
        assert industry.name == sample_industry.name


class TestReferenceDataServiceEdgeCases:
    """Edge case tests for ReferenceDataService."""

    def test_empty_string_name_for_company(self, reference_data_service, db_session):
        """Test creating company with empty string name."""
        company = reference_data_service.get_or_create_company(db_session, "")

        assert company.id is not None
        assert company.name == ""

    def test_very_long_company_name(self, reference_data_service, db_session):
        """Test creating company with very long name."""
        long_name = "A" * 500
        company = reference_data_service.get_or_create_company(db_session, long_name)

        assert company.id is not None
        assert company.name == long_name

    def test_special_characters_in_names(self, reference_data_service, db_session):
        """Test creating entities with special characters."""
        company = reference_data_service.get_or_create_company(
            db_session, "Tech & Data Corp. (USA)"
        )
        location = reference_data_service.get_or_create_location(db_session, "São Paulo, Brazil")
        category = reference_data_service.get_or_create_category(
            db_session, "Software Development & Engineering"
        )
        industry = reference_data_service.get_or_create_industry(db_session, "IT & Services")

        assert company.name == "Tech & Data Corp. (USA)"
        assert location.region == "São Paulo, Brazil"
        assert category.name == "Software Development & Engineering"
        assert industry.name == "IT & Services"

    def test_unicode_characters_in_names(self, reference_data_service, db_session):
        """Test creating entities with unicode characters."""
        company = reference_data_service.get_or_create_company(db_session, "株式会社テック")
        location = reference_data_service.get_or_create_location(db_session, "東京, 日本")

        assert company.name == "株式会社テック"
        assert location.region == "東京, 日本"

    def test_multiple_calls_return_same_entity(self, reference_data_service, db_session):
        """Test that multiple calls with same name return the same entity."""
        company1 = reference_data_service.get_or_create_company(db_session, "Consistent Corp")
        company2 = reference_data_service.get_or_create_company(db_session, "Consistent Corp")
        company3 = reference_data_service.get_or_create_company(db_session, "Consistent Corp")

        assert company1.id == company2.id == company3.id
        assert db_session.query(Company).filter_by(name="Consistent Corp").count() == 1
