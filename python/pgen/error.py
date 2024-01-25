from dataclasses import dataclass

@dataclass
class APIError():
    errorMessage: str
    status: int