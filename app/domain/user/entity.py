from datetime import datetime, timezone

from app.domain.user.value_objects import Email, Password, Username


class User:
    def __init__(
        self,
        email: Email,
        username: Username,
        password: Password,
        id: int | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.email = email
        self.username = username
        self.password = password
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def change_email(self, new_email: Email) -> None:
        self.email = new_email
