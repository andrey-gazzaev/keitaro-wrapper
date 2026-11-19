"""Campaign response body."""

from pydantic import BaseModel


class CampaignOutDto(BaseModel):
    """Campaign the client can show. `deleted` is true when the row is a tombstone."""

    id: int
    """Keitaro id of this campaign."""

    name: str
    """Name shown to the operator."""

    deleted: bool
    """True when the stored row is a tombstone. False while the campaign is live."""
