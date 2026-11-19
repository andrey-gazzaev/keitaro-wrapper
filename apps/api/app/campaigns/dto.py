"""Campaign request and response bodies."""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class CampaignIn(BaseModel):
    """Name, country, and offer used to create one campaign."""

    name: str
    """Name shown to the operator. Empty and surrounding space are rejected."""

    country: str
    """Two-letter country code. A longer or non-letter value is rejected."""

    offer_id: Annotated[int, Field(ge=1)]
    """Keitaro offer id. Values below 1 are rejected."""

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        """The name without surrounding space."""
        trimmed = value.strip()

        if trimmed == "":
            raise ValueError("Name is empty.")

        return trimmed

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, value: str) -> str:
        """The country code in uppercase."""
        if len(value) != 2 or not value.isascii() or not value.isalpha():
            raise ValueError("Country must be two letters.")

        return value.upper()


class CampaignOut(BaseModel):
    """Campaign the client can show. `deleted` is true when the row is a tombstone."""

    id: int
    """Keitaro id of this campaign."""

    name: str
    """Name shown to the operator."""

    deleted: bool
    """True when the stored row is a tombstone. False while the campaign is live."""
