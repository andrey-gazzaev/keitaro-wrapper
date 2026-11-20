"""Read a country filter payload."""

import json


def country_payload(payload: object) -> list[str] | None:
    """Country codes in this payload. None when it is not a list of strings."""
    value = payload

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None

    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None

    return value
