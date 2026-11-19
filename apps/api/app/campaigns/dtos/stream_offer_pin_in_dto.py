"""Pin-share request body."""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class StreamOfferPinInDto(BaseModel):
    """Share to keep fixed on one offer."""

    share: Decimal = Field(ge=0, le=100)
    """Working share from 0 to 100. More than two decimal places are rejected."""

    @field_validator("share")
    @classmethod
    def two_places(cls, value: Decimal) -> Decimal:
        """The share when it has at most two decimal places."""
        exponent = value.as_tuple().exponent

        if not isinstance(exponent, int) or exponent < -2:
            raise ValueError("Share has more than two decimal places.")

        return value
