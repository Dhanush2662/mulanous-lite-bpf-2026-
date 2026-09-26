"""Controlled API errors. Handlers render these as {"error": "..."}."""


class AppError(Exception):
    """A request failed in a way the client can handle."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
