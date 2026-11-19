"""Editor response body."""

from pydantic import BaseModel

from app.campaigns.dtos.stream_group_out_dto import StreamGroupOutDto


class StreamEditorOutDto(BaseModel):
    """Streams and offer rows for one campaign. Streams are empty before the first fetch."""

    campaign_id: int
    """Keitaro campaign id."""

    streams: list[StreamGroupOutDto]
    """Streams in position order. Empty before the first fetch."""
