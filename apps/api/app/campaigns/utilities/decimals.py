"""Read a loose number as a decimal."""

from decimal import Decimal


def decimal(value: Decimal | int | float | str) -> Decimal:
    """This number as a decimal."""
    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))
