"""Flow bodies created with a campaign."""


class CampaignStreamService:
    """Flows created with a campaign."""

    redirect_url: str = "https://www.google.com"
    """URL the country flow opens."""

    def country(self, campaign_id: int, country: str) -> dict[str, object]:
        """Body for the country flow. It accepts that country and redirects to Google."""
        return {
            "campaign_id": campaign_id,
            "type": "regular",
            "name": "Country",
            "position": 1,
            "schema": "redirect",
            "action_type": "http",
            "action_payload": self.redirect_url,
            "offers": [],
            "filters": [
                {
                    "name": "country",
                    "mode": "accept",
                    "payload": [country],
                }
            ],
        }

    def offer(self, campaign_id: int, offer_id: int) -> dict[str, object]:
        """Body for the offer flow. The offer takes the full share."""
        return {
            "campaign_id": campaign_id,
            "type": "regular",
            "name": "Offer",
            "position": 2,
            "schema": "landings",
            "action_type": "http",
            "filters": [],
            "offers": [
                {
                    "offer_id": offer_id,
                    "share": 100,
                    "state": "active",
                }
            ],
        }
