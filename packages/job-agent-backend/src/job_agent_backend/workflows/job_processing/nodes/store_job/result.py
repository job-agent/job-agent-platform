"""Result type for store_job node."""

from typing_extensions import TypedDict


class StoreJobResult(TypedDict):
    """Result from store_job node."""

    status: str
