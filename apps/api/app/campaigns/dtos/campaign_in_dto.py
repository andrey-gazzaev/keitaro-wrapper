"""Campaign request body."""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

_NAME_PREFIX = "test_gazzaev_"


class CampaignInDto(BaseModel):
    """Name, country, and offer used to create one campaign."""

    name: str
    """Name shown to the operator. Empty, surrounding space, and a missing prefix are rejected."""

    country: str
    """Two-letter country code. A longer or non-letter value is rejected."""

    offer_id: Annotated[int, Field(ge=1)]
    """Keitaro offer id. Values below 1 are rejected."""

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        """The name without surrounding space."""
        trimmed = value.strip()

        if trimmed == "" or not trimmed.startswith(_NAME_PREFIX):
            raise ValueError("Name is empty.")

        return trimmed

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, value: str) -> str:
        """The country code in uppercase."""
        if len(value) != 2 or not value.isascii() or not value.isalpha():
            raise ValueError("Country must be two letters.")

        return value.upper()
