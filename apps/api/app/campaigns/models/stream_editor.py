"""Editor state for one campaign."""

from app.campaigns.models.stream_group import StreamGroup


class StreamEditor:
    """Streams and offer rows for one stored campaign."""

    campaign_id: int
    """Keitaro campaign id."""

    streams: list[StreamGroup]
    """Streams in position order. Empty before the first fetch."""

    def __init__(self, campaign_id: int, streams: list[StreamGroup]) -> None:
        """Editor state for this campaign."""
        self.campaign_id = campaign_id
        self.streams = streams
