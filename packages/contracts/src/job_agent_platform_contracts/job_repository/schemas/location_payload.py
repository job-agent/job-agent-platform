from typing import TypedDict


class LocationPayloadRequired(TypedDict):
    region: str


class LocationPayload(LocationPayloadRequired, total=False):
    is_remote: bool
    can_apply: bool
