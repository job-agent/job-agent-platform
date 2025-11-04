from typing import TypedDict


class CompanyPayloadRequired(TypedDict):
    name: str


class CompanyPayload(CompanyPayloadRequired, total=False):
    website: str
