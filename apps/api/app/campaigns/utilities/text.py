"""Read a loose value as text."""


def text(value: object) -> str:
    """This text. Empty when the value is not a string."""
    if isinstance(value, str):
        return value

    return ""
