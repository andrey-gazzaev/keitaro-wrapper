"""Values used to create one campaign."""


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
