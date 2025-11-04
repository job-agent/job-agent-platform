from typing import TypedDict


class SalaryPayload(TypedDict, total=False):
    currency: str
    min_value: float
    max_value: float
