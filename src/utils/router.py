from typing_extensions import TypedDict, Literal


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal["retrival", "resume", "FINISH"]
