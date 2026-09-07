import re


class Email:
    def __init__(self, value: str) -> None:
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", value):
            raise ValueError(f"Invalid email: {value}")
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


class Username:
    def __init__(self, value: str) -> None:
        if len(value) < 3 or len(value) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Username):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


class Password:
    def __init__(self, value: str) -> None:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.value = value

    def __str__(self) -> str:
        return "***"
