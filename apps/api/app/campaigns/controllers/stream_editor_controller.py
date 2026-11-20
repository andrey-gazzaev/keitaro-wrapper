"""Stream editor routes."""

from collections.abc import Callable
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.campaigns.dtos.offer_out_dto import OfferOutDto
from app.campaigns.dtos.stream_editor_out_dto import StreamEditorOutDto
from app.campaigns.dtos.stream_group_out_dto import StreamGroupOutDto
from app.campaigns.dtos.stream_line_out_dto import StreamLineOutDto
from app.campaigns.dtos.stream_offer_add_in_dto import StreamOfferAddInDto
from app.campaigns.dtos.stream_offer_pin_in_dto import StreamOfferPinInDto
from app.campaigns.models.offer import Offer
from app.campaigns.models.stream_editor import StreamEditor
from app.campaigns.models.stream_group import StreamGroup
from app.campaigns.models.stream_line import StreamLine
from app.campaigns.services.stream_editor_error import StreamEditorError
from app.campaigns.services.stream_editor_service import StreamEditorService, get_stream_editor_service

StreamEditorServiceDep = Annotated[StreamEditorService, Depends(get_stream_editor_service)]

_STATUS = {
    "not_found": status.HTTP_404_NOT_FOUND,
    "conflict": status.HTTP_409_CONFLICT,
    "invalid": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "unavailable": status.HTTP_502_BAD_GATEWAY,
    "not_configured": status.HTTP_503_SERVICE_UNAVAILABLE,
}


class StreamEditorController:
    """Read and change one campaign's streams over HTTP."""

    router: APIRouter
    """Routes this controller serves."""

    def __init__(self) -> None:
        """Routes for the stream editor."""
        self.router = APIRouter(prefix="/campaigns", tags=["campaigns"])
        self.router.get("/{campaign_id}/editor")(self.show_editor)
        self.router.post("/{campaign_id}/editor/fetch")(self.fetch_editor)
        self.router.get("/{campaign_id}/editor/available-offers/{offer_id}")(self.available_offer)
        self.router.post("/{campaign_id}/editor/offers")(self.add_offer)
        self.router.post("/{campaign_id}/editor/offers/{binding_id}/remove")(self.remove_offer)
        self.router.post("/{campaign_id}/editor/offers/{binding_id}/bring-back")(self.bring_back_offer)
        self.router.post("/{campaign_id}/editor/offers/{binding_id}/pin")(self.pin_offer)
        self.router.post("/{campaign_id}/editor/offers/{binding_id}/unpin")(self.unpin_offer)
        self.router.post("/{campaign_id}/editor/streams/{stream_id}/push")(self.push_stream)
        self.router.post("/{campaign_id}/editor/streams/{stream_id}/cancel")(self.cancel_stream)

    def show_editor(self, campaign_id: int, editor: StreamEditorServiceDep) -> StreamEditorOutDto:
        """Stored streams for this campaign. Empty before the first fetch."""
        return self._call(lambda: editor.get(campaign_id))

    def fetch_editor(self, campaign_id: int, editor: StreamEditorServiceDep) -> StreamEditorOutDto:
        """Import this campaign's flows and return the editor."""
        return self._call(lambda: editor.fetch(campaign_id))

    def available_offer(self, campaign_id: int, offer_id: int, editor: StreamEditorServiceDep) -> OfferOutDto:
        """The Keitaro offer the operator can add."""
        try:
            found = editor.find_offer(campaign_id, offer_id)
        except StreamEditorError as error:
            raise self._http_error(error) from None

        return self._offer(found)

    def add_offer(
        self,
        campaign_id: int,
        incoming: StreamOfferAddInDto,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Bind an offer to a live landings stream and return the editor."""
        return self._call(lambda: editor.add(campaign_id, incoming.stream_id, incoming.offer_id))

    def remove_offer(
        self,
        campaign_id: int,
        binding_id: int,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Archive one live binding and return the editor."""
        return self._call(lambda: editor.remove(campaign_id, binding_id))

    def bring_back_offer(
        self,
        campaign_id: int,
        binding_id: int,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Restore one deleted binding and return the editor."""
        return self._call(lambda: editor.bring_back(campaign_id, binding_id))

    def pin_offer(
        self,
        campaign_id: int,
        binding_id: int,
        incoming: StreamOfferPinInDto,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Fix one offer's share and return the editor."""
        return self._call(lambda: editor.pin(campaign_id, binding_id, incoming.share))

    def unpin_offer(
        self,
        campaign_id: int,
        binding_id: int,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Return one offer to the split and return the editor."""
        return self._call(lambda: editor.unpin(campaign_id, binding_id))

    def push_stream(
        self,
        campaign_id: int,
        stream_id: int,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Replace the live flow's offers and return the editor."""
        return self._call(lambda: editor.push(campaign_id, stream_id))

    def cancel_stream(
        self,
        campaign_id: int,
        stream_id: int,
        editor: StreamEditorServiceDep,
    ) -> StreamEditorOutDto:
        """Drop unpublished bindings, restore the snapshot, and return the editor."""
        return self._call(lambda: editor.cancel(campaign_id, stream_id))

    def _call(self, load: Callable[[], StreamEditor]) -> StreamEditorOutDto:
        try:
            loaded = load()
        except StreamEditorError as error:
            raise self._http_error(error) from None

        return self._editor(loaded)

    def _editor(self, editor: StreamEditor) -> StreamEditorOutDto:
        return StreamEditorOutDto(
            campaign_id=editor.campaign_id,
            streams=[self._group(stream) for stream in editor.streams],
        )

    def _group(self, stream: StreamGroup) -> StreamGroupOutDto:
        return StreamGroupOutDto(
            id=stream.id,
            name=stream.name,
            position=stream.position,
            accepts_offers=stream.accepts_offers,
            deleted=stream.deleted,
            dirty=stream.dirty,
            lines=[self._line(line) for line in stream.lines],
        )

    def _line(self, line: StreamLine) -> StreamLineOutDto:
        return StreamLineOutDto(
            id=line.id,
            offer_id=line.offer_id,
            name=line.name,
            share=_share_text(line.share),
            pinned=line.pinned,
            deleted=line.deleted,
        )

    def _offer(self, offer: Offer) -> OfferOutDto:
        return OfferOutDto(id=offer.id, name=offer.name)

    def _http_error(self, error: StreamEditorError) -> HTTPException:
        return HTTPException(status_code=_STATUS[error.kind])


def _share_text(share: Decimal) -> str:
    return format(share.quantize(Decimal("0.01")), "f")


stream_editor_controller = StreamEditorController()
