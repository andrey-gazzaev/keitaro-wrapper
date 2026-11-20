"""Read a loose value as a whole number."""


def whole(value: object) -> int | None:
    """This whole number. None when the value is not an integer."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None

    return value
