from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class Login(SQLModel):
    username: str
    password: str
