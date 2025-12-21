"""the contracts module structure after interface regrouping.

These tests verify that all interfaces are importable from their new expected locations
after the refactoring is complete. They are designed to FAIL (RED stage) until
the implementation is done.

Requirements Covered:
- Create package-level contracts folder
- Move ICVLoader to package-level contracts
- Move IScrapperClient to package-level contracts
- Move IFilterService to package-level contracts
- Move IModelFactory to package-level contracts
- Update package-level contracts __init__.py
- Create service-level contracts folder for model_providers
- Move IModelRegistry to model_providers service-level contracts
- Move IModelProvider to model_providers service-level contracts
- Update model_providers service-level contracts __init__.py
- No circular import errors
"""

import pytest
from abc import ABC


class TestPackageLevelContractsExist:
    """Package-level contracts folder exists and is importable."""

    def test_contracts_module_is_importable(self) -> None:
        """Verify that job_agent_backend.contracts module exists and is importable."""
        # This will raise ImportError if module doesn't exist
        from job_agent_backend import contracts  # noqa: F401

        assert contracts is not None

    def test_contracts_init_has_all_attribute(self) -> None:
        """Verify that contracts.__all__ is defined."""
        from job_agent_backend import contracts

        assert hasattr(contracts, "__all__")
        assert isinstance(contracts.__all__, (list, tuple))


class TestPackageLevelInterfaceImports:
    """Interfaces importable from contracts."""

    def test_icvloader_importable_from_contracts(self) -> None:
        """ICVLoader is importable from job_agent_backend.contracts."""
        from job_agent_backend.contracts import ICVLoader

        assert ICVLoader is not None
        assert issubclass(ICVLoader, ABC)

    def test_iscrapperclient_importable_from_contracts(self) -> None:
        """IScrapperClient is importable from job_agent_backend.contracts."""
        from job_agent_backend.contracts import IScrapperClient

        assert IScrapperClient is not None
        assert issubclass(IScrapperClient, ABC)

    def test_ifilterservice_importable_from_contracts(self) -> None:
        """IFilterService is importable from job_agent_backend.contracts."""
        from job_agent_backend.contracts import IFilterService

        assert IFilterService is not None
        assert issubclass(IFilterService, ABC)

    def test_imodelfactory_importable_from_contracts(self) -> None:
        """IModelFactory is importable from job_agent_backend.contracts."""
        from job_agent_backend.contracts import IModelFactory

        assert IModelFactory is not None
        assert issubclass(IModelFactory, ABC)


class TestPackageLevelContractsAllExports:
    """Package-level contracts __init__.py exports all interfaces."""

    def test_all_package_interfaces_in_contracts_all(self) -> None:
        """Verify all 4 package-level interfaces are in contracts.__all__."""
        from job_agent_backend import contracts

        expected_interfaces = {"ICVLoader", "IScrapperClient", "IFilterService", "IModelFactory"}
        actual_all = set(contracts.__all__)

        # Check all expected interfaces are present
        for interface_name in expected_interfaces:
            assert interface_name in actual_all, f"{interface_name} not found in contracts.__all__"

    def test_bulk_import_all_package_level_interfaces(self) -> None:
        """Verify all 4 interfaces can be imported in a single statement."""
        from job_agent_backend.contracts import (
            ICVLoader,
            IScrapperClient,
            IFilterService,
            IModelFactory,
        )

        # All should be abstract base classes
        assert issubclass(ICVLoader, ABC)
        assert issubclass(IScrapperClient, ABC)
        assert issubclass(IFilterService, ABC)
        assert issubclass(IModelFactory, ABC)


class TestModelProvidersContractsExist:
    """Service-level contracts folder for model_providers exists."""

    def test_model_providers_contracts_module_is_importable(self) -> None:
        """Verify model_providers.contracts module exists and is importable."""
        from job_agent_backend.model_providers import contracts  # noqa: F401

        assert contracts is not None

    def test_model_providers_contracts_init_has_all_attribute(self) -> None:
        """Verify model_providers.contracts.__all__ is defined."""
        from job_agent_backend.model_providers import contracts

        assert hasattr(contracts, "__all__")
        assert isinstance(contracts.__all__, (list, tuple))


class TestServiceLevelInterfaceImports:
    """REQ-8, Service-level interfaces importable from model_providers.contracts."""

    def test_imodelregistry_importable_from_model_providers_contracts(self) -> None:
        """IModelRegistry importable from model_providers.contracts."""
        from job_agent_backend.model_providers.contracts import IModelRegistry

        assert IModelRegistry is not None
        assert issubclass(IModelRegistry, ABC)

    def test_imodelprovider_importable_from_model_providers_contracts(self) -> None:
        """IModelProvider importable from model_providers.contracts."""
        from job_agent_backend.model_providers.contracts import IModelProvider

        assert IModelProvider is not None
        assert issubclass(IModelProvider, ABC)


class TestServiceLevelContractsAllExports:
    """Service-level contracts __init__.py exports all interfaces."""

    def test_all_service_interfaces_in_model_providers_contracts_all(self) -> None:
        """Verify both service-level interfaces are in model_providers.contracts.__all__."""
        from job_agent_backend.model_providers import contracts

        expected_interfaces = {"IModelRegistry", "IModelProvider"}
        actual_all = set(contracts.__all__)

        for interface_name in expected_interfaces:
            assert (
                interface_name in actual_all
            ), f"{interface_name} not found in model_providers.contracts.__all__"

    def test_bulk_import_all_service_level_interfaces(self) -> None:
        """Verify both service-level interfaces can be imported in a single statement."""
        from job_agent_backend.model_providers.contracts import (
            IModelRegistry,
            IModelProvider,
        )

        assert issubclass(IModelRegistry, ABC)
        assert issubclass(IModelProvider, ABC)


class TestNoCircularImports:
    """No circular import errors."""

    def test_package_level_contracts_no_circular_imports(self) -> None:
        """Verify importing contracts module doesn't cause circular import errors."""
        # If there are circular imports, this will raise ImportError
        try:
            from job_agent_backend.contracts import (
                ICVLoader,
                IScrapperClient,
                IFilterService,
                IModelFactory,
            )
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise  # Re-raise if it's a different import error

        # Verify they are the expected types
        assert ICVLoader is not None
        assert IScrapperClient is not None
        assert IFilterService is not None
        assert IModelFactory is not None

    def test_service_level_contracts_no_circular_imports(self) -> None:
        """Verify importing model_providers.contracts doesn't cause circular imports."""
        try:
            from job_agent_backend.model_providers.contracts import (
                IModelRegistry,
                IModelProvider,
            )
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise

        assert IModelRegistry is not None
        assert IModelProvider is not None

    def test_cross_level_imports_no_circular(self) -> None:
        """Verify importing from both levels doesn't cause circular imports."""
        try:
            from job_agent_backend.contracts import IModelFactory
            from job_agent_backend.model_providers.contracts import IModelProvider

            # Both should coexist without issues
            assert IModelFactory is not None
            assert IModelProvider is not None
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            raise


class TestBackwardCompatibilityViaReExports:
    """Tests verifying backward compatibility - interfaces still accessible via old paths.

    These tests verify that service __init__.py files re-export interfaces from
    their new locations, maintaining backward compatibility for existing code.
    """

    def test_icvloader_still_importable_from_cv_loader(self) -> None:
        """ICVLoader should still be importable from cv_loader module."""
        from job_agent_backend.cv_loader import ICVLoader

        assert issubclass(ICVLoader, ABC)

    def test_iscrapperclient_still_importable_from_messaging(self) -> None:
        """IScrapperClient should still be importable from messaging module."""
        from job_agent_backend.messaging import IScrapperClient

        assert issubclass(IScrapperClient, ABC)

    def test_ifilterservice_still_importable_from_filter_service(self) -> None:
        """IFilterService should still be importable from filter_service module."""
        from job_agent_backend.filter_service import IFilterService

        assert issubclass(IFilterService, ABC)

    def test_imodelfactory_still_importable_from_model_providers(self) -> None:
        """IModelFactory should still be importable from model_providers module."""
        from job_agent_backend.model_providers import IModelFactory

        assert issubclass(IModelFactory, ABC)

    def test_imodelregistry_still_importable_from_model_providers(self) -> None:
        """IModelRegistry should still be importable from model_providers module."""
        from job_agent_backend.model_providers import IModelRegistry

        assert issubclass(IModelRegistry, ABC)

    def test_imodelprovider_still_importable_from_model_providers(self) -> None:
        """IModelProvider should still be importable from model_providers module."""
        from job_agent_backend.model_providers import IModelProvider

        assert issubclass(IModelProvider, ABC)

    def test_imodelprovider_still_importable_from_providers_submodule(self) -> None:
        """IModelProvider should still be importable from model_providers.providers."""
        from job_agent_backend.model_providers.providers import IModelProvider

        assert issubclass(IModelProvider, ABC)


class TestInterfaceIdentity:
    """Tests verifying that interfaces from different import paths are identical.

    This ensures the re-exports point to the same class object, not copies.
    """

    def test_icvloader_is_same_object_from_both_paths(self) -> None:
        """ICVLoader from contracts is same object as from cv_loader."""
        from job_agent_backend.contracts import ICVLoader as ICVLoaderFromContracts
        from job_agent_backend.cv_loader import ICVLoader as ICVLoaderFromService

        assert ICVLoaderFromContracts is ICVLoaderFromService

    def test_iscrapperclient_is_same_object_from_both_paths(self) -> None:
        """IScrapperClient from contracts is same object as from messaging."""
        from job_agent_backend.contracts import IScrapperClient as IScrapperClientFromContracts
        from job_agent_backend.messaging import IScrapperClient as IScrapperClientFromService

        assert IScrapperClientFromContracts is IScrapperClientFromService

    def test_ifilterservice_is_same_object_from_both_paths(self) -> None:
        """IFilterService from contracts is same object as from filter_service."""
        from job_agent_backend.contracts import IFilterService as IFilterServiceFromContracts
        from job_agent_backend.filter_service import IFilterService as IFilterServiceFromService

        assert IFilterServiceFromContracts is IFilterServiceFromService

    def test_imodelfactory_is_same_object_from_both_paths(self) -> None:
        """IModelFactory from contracts is same object as from model_providers."""
        from job_agent_backend.contracts import IModelFactory as IModelFactoryFromContracts
        from job_agent_backend.model_providers import IModelFactory as IModelFactoryFromService

        assert IModelFactoryFromContracts is IModelFactoryFromService

    def test_imodelregistry_is_same_object_from_both_paths(self) -> None:
        """IModelRegistry from model_providers.contracts is same as from model_providers."""
        from job_agent_backend.model_providers.contracts import (
            IModelRegistry as IModelRegistryFromContracts,
        )
        from job_agent_backend.model_providers import (
            IModelRegistry as IModelRegistryFromService,
        )

        assert IModelRegistryFromContracts is IModelRegistryFromService

    def test_imodelprovider_is_same_object_from_all_paths(self) -> None:
        """IModelProvider is same object from all three import paths."""
        from job_agent_backend.model_providers.contracts import (
            IModelProvider as IModelProviderFromContracts,
        )
        from job_agent_backend.model_providers import (
            IModelProvider as IModelProviderFromModelProviders,
        )
        from job_agent_backend.model_providers.providers import (
            IModelProvider as IModelProviderFromProviders,
        )

        assert IModelProviderFromContracts is IModelProviderFromModelProviders
        assert IModelProviderFromContracts is IModelProviderFromProviders


class TestInterfaceContracts:
    """Tests verifying that interfaces have the expected methods defined.

    These tests ensure the interfaces have correct signatures after the move.
    """

    def test_icvloader_has_required_methods(self) -> None:
        """ICVLoader should have load_from_text and load_from_pdf methods."""
        from job_agent_backend.contracts import ICVLoader

        assert hasattr(ICVLoader, "load_from_text")
        assert hasattr(ICVLoader, "load_from_pdf")

    def test_iscrapperclient_has_required_methods(self) -> None:
        """IScrapperClient should have scrape_jobs_streaming method."""
        from job_agent_backend.contracts import IScrapperClient

        assert hasattr(IScrapperClient, "scrape_jobs_streaming")

    def test_ifilterservice_has_required_methods(self) -> None:
        """IFilterService should have configure, filter, and filter_with_rejected methods."""
        from job_agent_backend.contracts import IFilterService

        assert hasattr(IFilterService, "configure")
        assert hasattr(IFilterService, "filter")
        assert hasattr(IFilterService, "filter_with_rejected")

    def test_imodelfactory_has_required_methods(self) -> None:
        """IModelFactory should have get_model, clear_cache, get_cache_size methods."""
        from job_agent_backend.contracts import IModelFactory

        assert hasattr(IModelFactory, "get_model")
        assert hasattr(IModelFactory, "clear_cache")
        assert hasattr(IModelFactory, "get_cache_size")

    def test_imodelregistry_has_required_methods(self) -> None:
        """IModelRegistry should have get, get_model, list_models methods."""
        from job_agent_backend.model_providers.contracts import IModelRegistry

        assert hasattr(IModelRegistry, "get")
        assert hasattr(IModelRegistry, "get_model")
        assert hasattr(IModelRegistry, "list_models")

    def test_imodelprovider_has_required_methods(self) -> None:
        """IModelProvider should have get_model method."""
        from job_agent_backend.model_providers.contracts import IModelProvider

        assert hasattr(IModelProvider, "get_model")
