"""Tests for database exception classes."""

import pytest

from db_core.exceptions import DatabaseError, DatabaseConnectionError, TransactionError


class TestDatabaseError:
    """Test suite for DatabaseError base exception."""

    def test_is_base_exception_class(self):
        """DatabaseError should be a base exception that other db errors inherit from."""
        error = DatabaseError("test error")

        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_can_be_raised_and_caught(self):
        """DatabaseError can be raised and caught."""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError("base database error")

        assert "base database error" in str(exc_info.value)


class TestDatabaseConnectionError:
    """Test suite for DatabaseConnectionError exception."""

    def test_inherits_from_database_error(self):
        """DatabaseConnectionError should inherit from DatabaseError."""
        error = DatabaseConnectionError("connection failed")

        assert isinstance(error, DatabaseError)
        assert isinstance(error, Exception)

    def test_can_be_raised_with_message(self):
        """DatabaseConnectionError can be raised with a descriptive message."""
        with pytest.raises(DatabaseConnectionError) as exc_info:
            raise DatabaseConnectionError("Failed to connect to database: timeout")

        assert "Failed to connect to database" in str(exc_info.value)
        assert "timeout" in str(exc_info.value)

    def test_can_be_caught_as_database_error(self):
        """DatabaseConnectionError can be caught as DatabaseError."""
        with pytest.raises(DatabaseError):
            raise DatabaseConnectionError("connection failed")

    def test_preserves_original_exception_chain(self):
        """DatabaseConnectionError preserves exception chain when raised from another error."""
        original = Exception("original error")

        with pytest.raises(DatabaseConnectionError) as exc_info:
            try:
                raise original
            except Exception as e:
                raise DatabaseConnectionError(f"Wrapped: {e}") from e

        assert exc_info.value.__cause__ is original


class TestTransactionError:
    """Test suite for TransactionError exception."""

    def test_inherits_from_database_error(self):
        """TransactionError should inherit from DatabaseError."""
        error = TransactionError("transaction failed")

        assert isinstance(error, DatabaseError)
        assert isinstance(error, Exception)

    def test_can_be_raised_with_message(self):
        """TransactionError can be raised with a descriptive message."""
        with pytest.raises(TransactionError) as exc_info:
            raise TransactionError("Transaction failed: deadlock detected")

        assert "Transaction failed" in str(exc_info.value)
        assert "deadlock detected" in str(exc_info.value)

    def test_can_be_caught_as_database_error(self):
        """TransactionError can be caught as DatabaseError."""
        with pytest.raises(DatabaseError):
            raise TransactionError("transaction failed")

    def test_preserves_original_exception_chain(self):
        """TransactionError preserves exception chain when raised from another error."""
        original = Exception("original error")

        with pytest.raises(TransactionError) as exc_info:
            try:
                raise original
            except Exception as e:
                raise TransactionError(f"Wrapped: {e}") from e

        assert exc_info.value.__cause__ is original


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_database_connection_error_not_instance_of_transaction_error(self):
        """DatabaseConnectionError and TransactionError are sibling classes."""
        connection_error = DatabaseConnectionError("conn")

        assert not isinstance(connection_error, TransactionError)

    def test_transaction_error_not_instance_of_database_connection_error(self):
        """TransactionError and DatabaseConnectionError are sibling classes."""
        transaction_error = TransactionError("trans")

        assert not isinstance(transaction_error, DatabaseConnectionError)

    def test_both_share_common_base(self):
        """Both error types share DatabaseError as common base."""
        connection_error = DatabaseConnectionError("conn")
        transaction_error = TransactionError("trans")

        assert isinstance(connection_error, DatabaseError)
        assert isinstance(transaction_error, DatabaseError)
