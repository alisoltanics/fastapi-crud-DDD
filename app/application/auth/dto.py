from pydantic import BaseModel


class LoginDTO(BaseModel):
    username: str
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str
