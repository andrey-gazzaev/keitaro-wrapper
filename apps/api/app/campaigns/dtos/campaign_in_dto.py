"""Campaign request body."""

import os
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


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
        """The trimmed name. A name that misses the configured prefix is rejected."""
        trimmed = value.strip()

        if trimmed == "":
            raise ValueError("Name is empty.")

        prefix = os.environ.get("CAMPAIGN_PREFIX", "")

        if prefix != "" and not trimmed.startswith(prefix):
            raise ValueError("Name is missing the required prefix.")

        return trimmed

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, value: str) -> str:
        """The country code in uppercase."""
        if len(value) != 2 or not value.isascii() or not value.isalpha():
            raise ValueError("Country must be two letters.")

        return value.upper()
