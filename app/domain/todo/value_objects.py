class TodoTitle:
    def __init__(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        if len(value) > 200:
            raise ValueError("Title must be at most 200 characters")
        self.value = value.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TodoTitle):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


class TodoDescription:
    def __init__(self, value: str | None = None) -> None:
        if value is not None and len(value) > 1000:
            raise ValueError("Description must be at most 1000 characters")
        self.value = value.strip() if value else None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TodoDescription):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value or ""
