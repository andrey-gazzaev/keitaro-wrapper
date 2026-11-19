"""Campaign domain types."""


class CampaignDraft:
    """Values used to create one campaign."""

    name: str
    """Name shown to the operator."""

    country: str
    """Two-letter country code, already uppercased."""

    offer_id: int
    """Keitaro offer that receives the offer flow."""

    def __init__(self, name: str, country: str, offer_id: int) -> None:
        """A draft with this name, country, and offer."""
        self.name = name
        self.country = country
        self.offer_id = offer_id


class Campaign:
    """A campaign stored for this tracker."""

    id: int
    """Keitaro id of this campaign."""

    name: str
    """Name shown to the operator."""

    deleted: bool
    """True when the stored row is a tombstone. False while the campaign is live."""

    def __init__(self, id: int, name: str, deleted: bool) -> None:
        """A stored campaign with this id, name, and deleted flag."""
        self.id = id
        self.name = name
        self.deleted = deleted
