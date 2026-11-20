"""Offer share splits and offer number checks."""

from decimal import ROUND_HALF_UP, Decimal

from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_record import StreamRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.stream_editor_error import StreamEditorError
from app.campaigns.utilities.decimals import decimal

_HUNDRED = Decimal("100")
_CENT = Decimal("0.01")


class OfferShareService:
    """Splits offer shares and checks offer numbers."""

    def split(self, rows: list[StreamOfferRecord]) -> dict[int, Decimal]:
        """Shares for the unpinned live rows. Empty when every live row is pinned."""
        pinned_total = sum(
            (decimal(row.share) for row in rows if not row.deleted and row.pinned),
            Decimal("0"),
        )
        remainder = _HUNDRED - pinned_total

        if remainder < 0:
            raise StreamEditorError("invalid")

        unpinned = sorted(
            (row for row in rows if not row.deleted and not row.pinned),
            key=lambda row: (row.created_at, row.id),
        )

        if not unpinned:
            return {}

        each = self.money(remainder / Decimal(len(unpinned)))
        last = self.money(remainder - each * (len(unpinned) - 1))

        if last < 0:
            raise StreamEditorError("invalid")

        shares: dict[int, Decimal] = {}

        for row in unpinned[:-1]:
            shares[row.id] = each

        shares[unpinned[-1].id] = last

        return shares

    def dirty(self, stream: StreamRecord, rows: list[StreamOfferRecord]) -> bool:
        """True when this stream or a row differs from the published snapshot."""
        if stream.deleted != stream.published_deleted:
            return True

        for row in rows:
            published_share = row.published_share

            if published_share is None or row.published_pinned is None or row.published_deleted is None:
                return True

            if row.pinned != row.published_pinned or row.deleted != row.published_deleted:
                return True

            if self.money(row.share) != self.money(published_share):
                return True

        return False

    def money(self, value: Decimal | int | float | str) -> Decimal:
        """This amount rounded to cents."""
        return decimal(value).quantize(_CENT, rounding=ROUND_HALF_UP)

    def json_share(self, value: Decimal | int | float | str) -> int | float:
        """This share as a JSON number. Whole cents stay integers."""
        text = format(self.money(value), "f")

        if text.endswith(".00"):
            return int(text[:-3])

        return float(text)

    def offer_id(self, value: object) -> int:
        """The Keitaro offer id. Unavailable when the value is not an integer."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise KeitaroError("unavailable")

        return value

    def remote_share(self, value: object) -> Decimal:
        """The Keitaro share in cents. Unavailable when it is missing or outside 0 to 100."""
        if isinstance(value, bool):
            raise KeitaroError("unavailable")

        if isinstance(value, int):
            share = Decimal(value)
        elif isinstance(value, float):
            share = Decimal(str(value))
        elif isinstance(value, str):
            try:
                share = Decimal(value)
            except ArithmeticError:
                raise KeitaroError("unavailable") from None
        else:
            raise KeitaroError("unavailable")

        share = self.money(share)

        if share < 0 or share > _HUNDRED:
            raise KeitaroError("unavailable")

        return share
