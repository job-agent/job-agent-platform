"""Migration verification tests for jobs-repository to db-core.

These tests verify the migration-specific behavior after jobs-repository
is refactored to use db-core. They focus on:
1. Import verification - packages can import from db-core after migration
2. Repository inheritance - JobRepository properly inherits BaseRepository
3. Exception mapping - correct db-core exceptions are raised
4. Session management - _session_scope still works after inheriting from BaseRepository

These tests are designed to FAIL before the migration is complete (RED phase).
Existing repository functionality tests should NOT be duplicated here.
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session


class TestDbCoreImports:
    """Verify that db-core imports work correctly after migration."""

    def test_can_import_base_repository_from_db_core(self):
        """Verify BaseRepository can be imported from db-core.

        After migration, jobs-repository should be able to import
        BaseRepository from db-core for inheritance.
        """
        from db_core import BaseRepository

        assert BaseRepository is not None

    def test_can_import_transaction_error_from_db_core(self):
        """Verify TransactionError can be imported from db-core."""
        from db_core import TransactionError

        assert TransactionError is not None

    def test_can_import_database_error_from_db_core(self):
        """Verify DatabaseError base class can be imported from db-core."""
        from db_core import DatabaseError

        assert DatabaseError is not None

    def test_can_import_get_session_factory_from_db_core(self):
        """Verify get_session_factory can be imported from db-core."""
        from db_core import get_session_factory

        assert get_session_factory is not None
        assert callable(get_session_factory)


class TestJobRepositoryInheritance:
    """Verify JobRepository properly inherits from BaseRepository."""

    def test_job_repository_inherits_from_base_repository(self):
        """JobRepository should be a subclass of db-core BaseRepository.

        After migration, JobRepository class declaration should be:
        class JobRepository(BaseRepository, IJobRepository)
        """
        from db_core import BaseRepository
        from jobs_repository.repository import JobRepository

        assert issubclass(JobRepository, BaseRepository), (
            "JobRepository must inherit from db_core.BaseRepository after migration"
        )

    def test_job_repository_instance_is_base_repository(
        self, reference_data_service, job_mapper, db_session
    ):
        """JobRepository instance should pass isinstance check for BaseRepository.

        This verifies the inheritance chain is correctly set up.
        """
        from db_core import BaseRepository
        from jobs_repository.repository import JobRepository

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        assert isinstance(repo, BaseRepository), (
            "JobRepository instance must be an instance of BaseRepository"
        )

    def test_job_repository_inherits_session_scope_from_base_repository(
        self, reference_data_service, job_mapper, db_session
    ):
        """JobRepository should have _session_scope method from BaseRepository.

        After migration, JobRepository should NOT define its own _session_scope;
        it should use the inherited one from BaseRepository.
        """
        from jobs_repository.repository import JobRepository
        from db_core.repository.base import BaseRepository

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        # The _session_scope should be inherited, not overridden
        assert hasattr(repo, "_session_scope")

        # Verify it's using the BaseRepository implementation
        # by checking the method is from BaseRepository, not defined locally
        assert JobRepository._session_scope is BaseRepository._session_scope, (
            "JobRepository should use BaseRepository._session_scope, not define its own"
        )

    def test_job_repository_init_calls_super_init(self, reference_data_service, job_mapper):
        """JobRepository __init__ should call super().__init__ with session params.

        After migration, JobRepository should delegate session management
        to BaseRepository via super().__init__(session=..., session_factory=...).
        """
        mock_session = MagicMock(spec=Session)

        from jobs_repository.repository import JobRepository

        # When initialized with session, _close_session should be False
        # This behavior comes from BaseRepository
        repo = JobRepository(reference_data_service, job_mapper, session=mock_session)

        assert repo._close_session is False, (
            "JobRepository should delegate session handling to BaseRepository; "
            "_close_session should be False when session is provided"
        )


class TestJobRepositoryExceptionMapping:
    """Verify JobRepository uses db-core exceptions."""

    def test_transaction_error_is_from_db_core(self):
        """TransactionError raised by JobRepository should be from db-core.

        After migration, the TransactionError import in job_repository.py
        should be: from db_core import TransactionError
        """
        from db_core import TransactionError as DbCoreTransactionError

        # Import the TransactionError that JobRepository uses
        # After migration this should come from db-core
        from jobs_repository.repository.job_repository import TransactionError

        assert TransactionError is DbCoreTransactionError, (
            "TransactionError in job_repository.py should be imported from db_core, "
            "not from job_agent_platform_contracts"
        )

    def test_transaction_error_inherits_from_database_error(self):
        """TransactionError should be a subclass of DatabaseError.

        db-core's exception hierarchy:
        DatabaseError -> TransactionError
        """
        from db_core import TransactionError, DatabaseError

        assert issubclass(TransactionError, DatabaseError)

    def test_sqlalchemy_error_raises_db_core_transaction_error(
        self, reference_data_service, job_mapper, db_session
    ):
        """SQLAlchemyError should be converted to db-core TransactionError.

        When a SQLAlchemyError occurs during repository operations,
        it should be wrapped in db-core's TransactionError.
        """
        from sqlalchemy.exc import SQLAlchemyError
        from db_core import TransactionError
        from jobs_repository.repository import JobRepository

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)
        job_data = {"job_id": 999, "title": "Test Job"}

        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("DB error")):
            with pytest.raises(TransactionError) as exc_info:
                repo.create(job_data)

        # Verify it's specifically db-core's TransactionError
        from db_core import DatabaseError

        assert isinstance(exc_info.value, DatabaseError)


class TestJobRepositorySessionManagement:
    """Verify session management works correctly after inheriting from BaseRepository."""

    def test_session_scope_commits_on_success(self, reference_data_service, job_mapper, db_session):
        """_session_scope should commit transaction on successful operation.

        This behavior should be inherited from BaseRepository.
        """
        from jobs_repository.repository import JobRepository

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        with patch.object(db_session, "commit") as mock_commit:
            repo.create({"job_id": 1001, "title": "Commit Test Job"})

        mock_commit.assert_called()

    def test_session_scope_rolls_back_on_exception(
        self, reference_data_service, job_mapper, db_session
    ):
        """_session_scope should rollback on exception.

        This behavior should be inherited from BaseRepository.
        """
        from jobs_repository.repository import JobRepository
        from sqlalchemy.exc import SQLAlchemyError

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        with patch.object(db_session, "commit", side_effect=SQLAlchemyError("error")):
            with patch.object(db_session, "rollback") as mock_rollback:
                try:
                    repo.create({"job_id": 1002, "title": "Rollback Test"})
                except Exception:
                    pass

        mock_rollback.assert_called()

    def test_session_scope_closes_managed_session(
        self, reference_data_service, job_mapper, in_memory_engine
    ):
        """_session_scope should close session when using session_factory.

        When JobRepository is initialized with session_factory (not session),
        _close_session should be True and sessions should be closed after use.
        """
        from sqlalchemy.orm import sessionmaker
        from jobs_repository.repository import JobRepository

        factory = sessionmaker(bind=in_memory_engine)
        repo = JobRepository(reference_data_service, job_mapper, session_factory=factory)

        assert repo._close_session is True

    def test_session_scope_does_not_close_external_session(
        self, reference_data_service, job_mapper, db_session
    ):
        """_session_scope should not close externally provided session.

        When JobRepository is initialized with session (not session_factory),
        _close_session should be False.
        """
        from jobs_repository.repository import JobRepository

        repo = JobRepository(reference_data_service, job_mapper, session=db_session)

        assert repo._close_session is False


class TestJobRepositoryDomainExceptionsRetained:
    """Verify domain-specific exceptions are still from contracts.

    Per requirements, domain-specific exceptions should remain in contracts:
    - JobAlreadyExistsError
    - ValidationError
    Only infrastructure exceptions move to db-core.
    """

    def test_job_already_exists_error_from_contracts(self):
        """JobAlreadyExistsError should still come from contracts.

        This is a domain-specific exception that should NOT be moved to db-core.
        """
        from job_agent_platform_contracts.job_repository.exceptions import (
            JobAlreadyExistsError,
        )
        from jobs_repository.repository.job_repository import JobAlreadyExistsError as RepoError

        assert RepoError is JobAlreadyExistsError

    def test_validation_error_from_contracts(self):
        """ValidationError should still come from contracts.

        This is a domain-specific exception that should NOT be moved to db-core.
        """
        from job_agent_platform_contracts.job_repository.exceptions import (
            ValidationError,
        )
        from jobs_repository.repository.job_repository import ValidationError as RepoError

        assert RepoError is ValidationError


class TestAlembicBaseImportUpdate:
    """Verify Alembic env.py imports Base from the correct location."""

    def test_alembic_env_imports_base_from_models(self):
        """Alembic env.py should import Base from jobs_repository.models.base.

        After migration, the import should be:
        from jobs_repository.models.base import Base

        NOT:
        from jobs_repository.database import Base
        """
        from pathlib import Path

        # Find the alembic env.py file
        package_root = Path(__file__).parent.parent.parent
        env_py = package_root / "alembic" / "env.py"

        if not env_py.exists():
            pytest.skip("alembic/env.py does not exist")

        content = env_py.read_text()

        # After migration, should import from models.base, not database
        assert "from jobs_repository.models.base import Base" in content, (
            "alembic/env.py should import Base from jobs_repository.models.base, "
            "not from jobs_repository.database"
        )

        # Should NOT import from database anymore
        assert "from jobs_repository.database import Base" not in content, (
            "alembic/env.py should NOT import from jobs_repository.database after migration"
        )
