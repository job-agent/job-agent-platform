"""Infrastructure verification tests for essay-repository package."""

from pathlib import Path

import pytest


def get_package_root() -> Path:
    """Get the essay-repository package root directory."""
    # This file is at: packages/essay-repository/src/essay_repository/infrastructure_test.py
    # Package root is at: packages/essay-repository/
    return Path(__file__).parent.parent.parent


def get_project_root() -> Path:
    """Get the job-agent-platform project root directory."""
    # Package root is at: packages/essay-repository/
    # Project root is at: job-agent-platform/
    return get_package_root().parent.parent


class TestAlembicSetup:
    """Alembic migration infrastructure."""

    def test_alembic_ini_exists(self) -> None:
        """Verify alembic.ini configuration file exists in package root."""
        package_root = get_package_root()
        alembic_ini = package_root / "alembic.ini"

        assert alembic_ini.exists(), (
            f"alembic.ini not found at {alembic_ini}. "
            "requires Alembic migration setup for essay-repository."
        )
        assert alembic_ini.is_file(), f"{alembic_ini} exists but is not a file"

    def test_alembic_env_py_exists(self) -> None:
        """Verify alembic/env.py environment file exists."""
        package_root = get_package_root()
        env_py = package_root / "alembic" / "env.py"

        assert env_py.exists(), (
            f"alembic/env.py not found at {env_py}. "
            "requires Alembic migration environment setup."
        )
        assert env_py.is_file(), f"{env_py} exists but is not a file"

    def test_alembic_versions_directory_exists(self) -> None:
        """Verify alembic/versions/ directory exists for migration scripts."""
        package_root = get_package_root()
        versions_dir = package_root / "alembic" / "versions"

        assert versions_dir.exists(), (
            f"alembic/versions/ directory not found at {versions_dir}. "
            "requires migrations directory."
        )
        assert versions_dir.is_dir(), f"{versions_dir} exists but is not a directory"

    def test_alembic_script_template_exists(self) -> None:
        """Verify alembic/script.py.mako template exists."""
        package_root = get_package_root()
        script_template = package_root / "alembic" / "script.py.mako"

        assert script_template.exists(), (
            f"alembic/script.py.mako not found at {script_template}. "
            "Alembic migration template is required for generating new migrations."
        )

    def test_alembic_ini_references_correct_script_location(self) -> None:
        """Verify alembic.ini points to the correct script_location."""
        package_root = get_package_root()
        alembic_ini = package_root / "alembic.ini"

        if not alembic_ini.exists():
            pytest.skip("alembic.ini does not exist yet")

        content = alembic_ini.read_text()
        assert (
            "script_location = alembic" in content
        ), "alembic.ini should have 'script_location = alembic' configuration"

    def test_alembic_env_imports_essay_repository_base(self) -> None:
        """Verify alembic/env.py imports Base from essay_repository package."""
        package_root = get_package_root()
        env_py = package_root / "alembic" / "env.py"

        if not env_py.exists():
            pytest.skip("alembic/env.py does not exist yet")

        content = env_py.read_text()
        assert (
            "essay_repository" in content
        ), "alembic/env.py should import from essay_repository package"
        assert "Base" in content, "alembic/env.py should import Base for metadata"

    def test_initial_migration_exists(self) -> None:
        """Verify at least one migration file exists for creating essays schema/table."""
        package_root = get_package_root()
        versions_dir = package_root / "alembic" / "versions"

        if not versions_dir.exists():
            pytest.skip("alembic/versions directory does not exist yet")

        migration_files = list(versions_dir.glob("*.py"))
        # Filter out __pycache__ and __init__.py
        migration_files = [
            f for f in migration_files if f.name != "__init__.py" and not f.name.startswith("__")
        ]

        assert len(migration_files) > 0, (
            f"No migration files found in {versions_dir}. "
            "requires migration to create essays.essays table."
        )


class TestReinstallPackagesScript:
    """Tests for reinstall_packages.sh including essay-repository."""

    def test_reinstall_packages_script_exists(self) -> None:
        """Verify reinstall_packages.sh script exists."""
        project_root = get_project_root()
        script_path = project_root / "scripts" / "reinstall_packages.sh"

        assert script_path.exists(), f"scripts/reinstall_packages.sh not found at {script_path}"

    def test_reinstall_packages_includes_essay_repository(self) -> None:
        """Verify reinstall_packages.sh PACKAGES array includes essay-repository."""
        project_root = get_project_root()
        script_path = project_root / "scripts" / "reinstall_packages.sh"

        if not script_path.exists():
            pytest.skip("reinstall_packages.sh does not exist")

        content = script_path.read_text()

        # Check that essay-repository is in the PACKAGES array
        assert '"essay-repository"' in content or "'essay-repository'" in content, (
            "scripts/reinstall_packages.sh should include 'essay-repository' in PACKAGES array. "
            "This is required for the new package to be installed via ./scripts/reinstall_packages.sh"
        )

    def test_essay_repository_comes_after_dependencies(self) -> None:
        """Verify essay-repository is listed after its dependencies in PACKAGES."""
        project_root = get_project_root()
        script_path = project_root / "scripts" / "reinstall_packages.sh"

        if not script_path.exists():
            pytest.skip("reinstall_packages.sh does not exist")

        content = script_path.read_text()

        if '"essay-repository"' not in content and "'essay-repository'" not in content:
            pytest.skip("essay-repository not yet in reinstall_packages.sh")

        # essay-repository depends on job-agent-platform-contracts
        # so it should come after contracts in the PACKAGES array
        contracts_pos = content.find("job-agent-platform-contracts")
        essay_pos = content.find("essay-repository")

        assert contracts_pos < essay_pos, (
            "essay-repository should be listed after job-agent-platform-contracts "
            "in the PACKAGES array (dependency order)"
        )
