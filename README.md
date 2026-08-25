
Yes. Let's build this as a **real, production-shaped FastAPI backend**, rather than a single `main.py` tutorial.

We'll use:

- **FastAPI 0.141.1** — the latest release shown in the official FastAPI release notes I found. ([FastAPI](https://fastapi.tiangolo.com/release-notes/?utm_source=chatgpt.com "Release Notes - FastAPI"))
    
- **Python 3.14+**
    
- **uv** for project/dependency management — the current FastAPI docs use `uv` in their examples. ([FastAPI](https://fastapi.tiangolo.com/tutorial/?utm_source=chatgpt.com "Tutorial - User Guide - FastAPI"))
    
- **PostgreSQL** as the real database
    
- **SQLModel** for ORM/database models — the current FastAPI SQL database tutorial uses SQLModel, which is built on SQLAlchemy and Pydantic. ([FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com "SQL (Relational) Databases - FastAPI"))
    
- **Alembic** for database migrations
    
- **Pydantic v2**
    
- **pydantic-settings** for environment configuration
    
- **PyJWT** for JWT creation/verification
    
- **pwdlib + Argon2** for password hashing, which is what the current FastAPI JWT tutorial recommends. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))
    
- `Annotated` + `Depends()` for dependency injection, which current FastAPI docs prefer. ([FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/?utm_source=chatgpt.com "Dependencies - FastAPI"))
    
- OAuth2 Password flow + Bearer JWT
    
- CRUD endpoints
    
- Proper response schemas so we never accidentally expose password hashes; FastAPI's response models can validate, document, serialize, and filter returned data. ([FastAPI](https://fastapi.tiangolo.com/tutorial/response-model/?utm_source=chatgpt.com "Response Model - Return Type - FastAPI"))
    

We'll make a small **Users + Todos API** so that you can understand relationships, authentication, authorization, CRUD, and database access.

---

# 1. What we're going to build

The final API will look roughly like this:

```text
                    ┌─────────────────┐
                    │     Client      │
                    │ React / Mobile  │
                    │ Postman / etc.  │
                    └────────┬────────┘
                             │
                             │ HTTP + JSON
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │                 │
                    │ Routers         │
                    │ Dependencies    │
                    │ JWT Auth        │
                    │ Validation      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    SQLModel     │
                    │   ORM layer     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │                 │
                    │ users           │
                    │ todos           │
                    └─────────────────┘
```

We'll have these endpoints:

|Method|Endpoint|Authentication|Purpose|
|---|---|---|---|
|POST|`/api/v1/auth/register`|No|Create user|
|POST|`/api/v1/auth/login`|No|Login and receive JWT|
|GET|`/api/v1/users/me`|Yes|Current user|
|POST|`/api/v1/todos`|Yes|Create todo|
|GET|`/api/v1/todos`|Yes|List user's todos|
|GET|`/api/v1/todos/{id}`|Yes|Get one todo|
|PATCH|`/api/v1/todos/{id}`|Yes|Update todo|
|DELETE|`/api/v1/todos/{id}`|Yes|Delete todo|

And the authentication flow is:

```text
register
   │
   ▼
password
   │
   ▼
Argon2 password hash
   │
   ▼
PostgreSQL
```

Then:

```text
login
  │
  ├── username/password
  │
  ▼
database lookup
  │
  ▼
verify Argon2 hash
  │
  ▼
create JWT
  │
  ▼
client
  │
  │ Authorization: Bearer <token>
  ▼
protected endpoint
  │
  ▼
decode + validate JWT
  │
  ▼
current user
```

---

# 2. Why these particular technologies?

There are many ways to build this.

For example:

```text
FastAPI
 ├── SQLAlchemy
 ├── SQLModel
 ├── Tortoise
 ├── asyncpg
 └── etc.
```

I'm choosing **SQLModel** because the current FastAPI documentation explicitly uses it for SQL databases, and SQLModel is built on SQLAlchemy + Pydantic. It supports PostgreSQL, MySQL, SQLite, Oracle, SQL Server, etc. ([FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com "SQL (Relational) Databases - FastAPI"))

For authentication, FastAPI provides security utilities that integrate with OpenAPI and the automatic Swagger documentation. The official security docs use `OAuth2PasswordBearer` for bearer-token authentication. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/?utm_source=chatgpt.com "Security - FastAPI"))

For passwords, **do not encrypt passwords**.

You hash them:

```text
password
   ↓
Argon2
   ↓
$argon2id$...
```

The hash is stored in PostgreSQL.

When the user logs in:

```text
submitted password
       ↓
verify against hash
       ↓
True / False
```

The original password is never stored.

---

# 3. Install Python and uv

You should use a modern Python version.

Check:

```bash
python --version
```

I'd use Python 3.14 for a new project.

Then install `uv`.

Check:

```bash
uv --version
```

The current FastAPI documentation has moved its examples toward `uv` project management. ([FastAPI](https://fastapi.tiangolo.com/release-notes/?utm_source=chatgpt.com "Release Notes - FastAPI"))

---

# 4. Create the project

Create a directory:

```bash
mkdir fastapi-crud
cd fastapi-crud
```

Initialize it:

```bash
uv init
```

You'll get a `pyproject.toml`.

The important idea is that `uv` will manage:

```text
pyproject.toml
uv.lock
```

`pyproject.toml` describes your dependencies.

`uv.lock` locks the exact dependency resolution so other developers/CI can reproduce the environment.

---

# 5. Install dependencies

Run:

```bash
uv add "fastapi[standard]" sqlmodel psycopg[binary] alembic pydantic-settings pyjwt "pwdlib[argon2]"
```

Let's understand every dependency.

### FastAPI

```text
fastapi[standard]
```

The framework.

The current FastAPI releases no longer use the old `fastapi-slim` distribution; the release notes explicitly say to use `fastapi[standard]` or `fastapi`. ([FastAPI](https://fastapi.tiangolo.com/release-notes/?utm_source=chatgpt.com "Release Notes - FastAPI"))

### SQLModel

```text
sqlmodel
```

ORM/database models.

### psycopg

```text
psycopg[binary]
```

PostgreSQL driver.

### Alembic

```text
alembic
```

Database migrations.

### pydantic-settings

```text
pydantic-settings
```

Reads things like:

```text
DATABASE_URL=...
SECRET_KEY=...
```

from environment variables.

### PyJWT

```text
pyjwt
```

Creates and verifies JWTs.

The current FastAPI JWT tutorial uses PyJWT. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))

### pwdlib

```text
pwdlib[argon2]
```

Secure password hashing.

FastAPI's current security tutorial recommends `pwdlib` with Argon2. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))

---

# 6. Our project structure

Create this structure:

```text
fastapi-crud/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── todos.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── auth.py
│       └── todos.py
│
├── migrations/
│
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

This might initially look like overkill.

It's not.

The important separation is:

```text
routes
   ↓
services
   ↓
database
```

Instead of putting everything into:

```text
main.py
```

---

# 7. Start PostgreSQL

The easiest development setup is Docker.

Create:

```text
docker-compose.yml
```

with:

```yaml
services:
  db:
    image: postgres:17
    container_name: fastapi_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app_password
      POSTGRES_DB: app_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start it:

```bash
docker compose up -d
```

Check:

```bash
docker ps
```

You should see:

```text
fastapi_postgres
```

Your PostgreSQL database is now actually running.

---

# 8. Configure environment variables

Create:

```text
.env
```

```env
DATABASE_URL=postgresql+psycopg://app:app_password@localhost:5432/app_db

SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Important:

**Never commit `.env` to Git.**

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

For a real production secret, generate a cryptographically random value rather than writing something like:

```text
SECRET_KEY=12345
```

---

# 9. Configuration class

Create:

```text
app/core/config.py
```

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

Let's understand this.

---

## `BaseSettings`

```python
class Settings(BaseSettings):
```

This is Pydantic's settings system.

It lets us map environment variables to Python attributes.

For example:

```env
DATABASE_URL=...
```

becomes:

```python
settings.database_url
```

---

## `model_config`

```python
model_config = SettingsConfigDict(
    env_file=".env",
)
```

This tells Pydantic Settings to also read `.env`.

So during development:

```text
.env
 ↓
Settings
 ↓
application
```

In production, you normally provide environment variables through your deployment system rather than relying on a checked-in `.env`.

---

# 10. Database engine

Create:

```text
app/db/session.py
```

```python
from sqlmodel import Session, create_engine

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=False,
)


def get_session():
    with Session(engine) as session:
        yield session
```

This is one of the most important pieces of the application.

---

# 11. What is the engine?

This:

```python
engine = create_engine(...)
```

represents the connection infrastructure between your Python application and PostgreSQL.

Think:

```text
FastAPI
   ↓
SQLModel
   ↓
SQLAlchemy engine
   ↓
psycopg
   ↓
PostgreSQL
```

The current FastAPI SQL database documentation uses a database engine and a session dependency. It specifically demonstrates a `yield` dependency that provides one session per request. ([FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com "SQL (Relational) Databases - FastAPI"))

---

# 12. What is a Session?

A session is roughly the unit through which your application performs database work.

For example:

```python
session.add(user)
session.commit()
```

means:

```text
Python object
     ↓
Session
     ↓
SQL
     ↓
PostgreSQL
```

---

# 13. Why `yield`?

This:

```python
def get_session():
    with Session(engine) as session:
        yield session
```

means:

```text
request starts
     ↓
create session
     ↓
give session to endpoint
     ↓
endpoint executes
     ↓
session context closes
```

FastAPI's dependency injection system is specifically designed for shared resources such as database sessions and security dependencies. ([FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/?utm_source=chatgpt.com "Dependencies - FastAPI"))

---

# 14. User database model

Create:

```text
app/models/user.py
```

```python
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
    )

    username: str = Field(
        index=True,
        unique=True,
        max_length=50,
    )

    hashed_password: str

    is_active: bool = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

This represents our PostgreSQL table.

Conceptually:

```text
users
------------------------------------------------
id
email
username
hashed_password
is_active
created_at
------------------------------------------------
```

---

# 15. Why not put the plain password here?

Notice:

```python
hashed_password: str
```

There is no:

```python
password: str
```

The database should contain:

```text
$argon2id$v=19$...
```

not:

```text
myPassword123
```

This distinction is extremely important.

---

# 16. Todo model

Create:

```text
app/models/todo.py
```

```python
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)

    title: str = Field(max_length=200)

    description: str | None = None

    completed: bool = False

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    owner_id: int = Field(
        foreign_key="users.id",
        index=True,
    )
```

Now PostgreSQL will conceptually have:

```text
users
  │
  │ 1
  │
  │
  │ many
  ▼
todos
```

Each todo belongs to a user.

---

# 17. Import models

Create:

```text
app/models/__init__.py
```

```python
from app.models.todo import Todo
from app.models.user import User

__all__ = ["User", "Todo"]
```

This is important later because Alembic needs to know about the models.

---

# 18. Request/response schemas

A common beginner mistake is using one model for everything.

Don't.

We have different concepts:

```text
database model
request model
response model
```

For example:

```text
User database model
        ↓
contains hashed_password

User response model
        ↓
does NOT contain hashed_password
```

This is exactly where FastAPI response models provide an important security boundary: returned data is filtered to the declared response shape. ([FastAPI](https://fastapi.tiangolo.com/tutorial/response-model/?utm_source=chatgpt.com "Response Model - Return Type - FastAPI"))

---

# 19. User schemas

Create:

```text
app/schemas/user.py
```

```python
from datetime import datetime

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    email: str
    username: str
    password: str


class UserPublic(SQLModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
```

Notice:

```python
class UserCreate:
    password
```

but:

```python
class UserPublic:
    # no password
    # no hashed_password
```

That's deliberate.

---

# 20. Todo schemas

Create:

```text
app/schemas/todo.py
```

```python
from datetime import datetime

from sqlmodel import SQLModel


class TodoCreate(SQLModel):
    title: str
    description: str | None = None


class TodoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoPublic(SQLModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    owner_id: int
```

The separation gives us:

```text
POST /todos

TodoCreate
     ↓
database Todo
     ↓
TodoPublic
```

---

# 21. Authentication schemas

Create:

```text
app/schemas/auth.py
```

```python
from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None
```

---

# 22. Password hashing

Create:

```text
app/core/security.py
```

```python
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )
```

`pwdlib` provides the password hashing abstraction and its recommended configuration uses Argon2, matching the current FastAPI security documentation. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))

---

# 23. Understanding hashing

Suppose the user registers:

```text
email: john@example.com
password: secret123
```

We do:

```python
hashed = hash_password("secret123")
```

and get something conceptually like:

```text
$argon2id$v=19$m=65536,t=3,p=4$...
```

We store that.

Later the user logs in:

```text
secret123
    ↓
verify_password()
    ↓
database hash
    ↓
True
```

We never need to decrypt anything because password hashes aren't encryption.

---

# 24. JWT creation

Add to `security.py`:

```python
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
```

The token payload contains:

```json
{
  "sub": "john",
  "exp": 1780000000
}
```

The exact JWT contains three pieces:

```text
header.payload.signature
```

The client receives the JWT.

---

# 25. What does JWT actually accomplish?

A JWT is **not** a database session.

Think:

```text
Login
 ↓
username/password verified
 ↓
JWT created
 ↓
client stores JWT
```

Next request:

```http
GET /api/v1/todos
Authorization: Bearer eyJ...
```

The API validates:

```text
signature
expiration
subject
```

and determines:

```text
This request belongs to user #123.
```

---

# 26. OAuth2PasswordBearer

Now create our authentication dependency.

Create:

```text
app/api/deps.py
```

Start with:

```python
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


SessionDep = Annotated[
    Session,
    Depends(get_session),
]
```

The current FastAPI docs recommend the `Annotated` form when possible. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/first-steps/?utm_source=chatgpt.com "Security - First Steps - FastAPI"))

---

# 27. Why `OAuth2PasswordBearer`?

This:

```python
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)
```

tells FastAPI:

> This API expects a bearer token.

So protected endpoints can say:

```python
token: Annotated[str, Depends(oauth2_scheme)]
```

FastAPI then extracts:

```http
Authorization: Bearer <JWT>
```

for us.

It also becomes part of the OpenAPI schema, so Swagger UI knows about the security mechanism. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/first-steps/?utm_source=chatgpt.com "Security - First Steps - FastAPI"))

---

# 28. Current user dependency

Continue `deps.py`:

```python
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        username = payload.get("sub")

        if not isinstance(username, str):
            raise credentials_exception

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    if user is None:
        raise credentials_exception

    return user
```

This is the central authentication dependency.

---

# 29. Let's understand it line by line

This:

```python
token: Annotated[
    str,
    Depends(oauth2_scheme),
]
```

means:

> FastAPI, get the bearer token from the request and give it to me.

Then:

```python
jwt.decode(...)
```

verifies the JWT.

If the JWT:

- has the wrong signature
    
- is malformed
    
- is expired
    
- can't be decoded
    

we reject it.

Then:

```python
username = payload.get("sub")
```

retrieves the subject.

Then:

```python
select(User).where(User.username == username)
```

looks the user up in PostgreSQL.

So authentication is not:

```text
JWT valid = user automatically valid forever
```

Instead:

```text
JWT valid
   +
user exists
   +
user can be checked against DB
   =
authenticated user
```

---

# 30. Login route

Create:

```text
app/api/routes/auth.py
```

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import SessionDep
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserPublic


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)
```

---

# 31. Registration endpoint

Add:

```python
@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    session: SessionDep,
):
    existing_user = session.exec(
        select(User).where(
            User.username == user_data.username
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = session.exec(
        select(User).where(
            User.email == user_data.email
        )
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(
            user_data.password
        ),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
```

FastAPI allows you to explicitly declare HTTP status codes such as `201 Created` on the path operation decorator. ([FastAPI](https://fastapi.tiangolo.com/tutorial/response-status-code/?utm_source=chatgpt.com "Response Status Code - FastAPI"))

---

# 32. Login endpoint

Add:

```python
@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    session: SessionDep,
):
    user = session.exec(
        select(User).where(
            User.username == form_data.username
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        subject=user.username
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )
```

Notice something important:

We don't accept JSON like:

```json
{
    "username": "john",
    "password": "secret"
}
```

for this OAuth2 password flow.

The OAuth2 password flow uses form data.

FastAPI's security utilities integrate this with the generated OpenAPI documentation. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/?utm_source=chatgpt.com "Security - FastAPI"))

---

# 33. Users route

Create:

```text
app/api/routes/users.py
```

```python
from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserPublic


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserPublic,
)
def get_me(
    current_user: CurrentUser,
):
    return current_user
```

But we haven't defined `CurrentUser` yet.

Let's do that.

---

# 34. Create a reusable CurrentUser dependency

In `app/api/deps.py`, add:

```python
CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
```

Now instead of repeatedly writing:

```python
current_user: Annotated[
    User,
    Depends(get_current_user),
]
```

we can simply write:

```python
current_user: CurrentUser
```

This is one of the reasons `Annotated` makes FastAPI projects much cleaner.

---

# 35. Todo service

Create:

```text
app/services/todos.py
```

We'll keep database/business operations here.

```python
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


def create_todo(
    session: Session,
    data: TodoCreate,
    owner_id: int,
) -> Todo:

    todo = Todo(
        title=data.title,
        description=data.description,
        owner_id=owner_id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo
```

---

# 36. Read one todo

Continue:

```python
def get_todo(
    session: Session,
    todo_id: int,
    owner_id: int,
) -> Todo:

    todo = session.get(Todo, todo_id)

    if todo is None or todo.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return todo
```

This line is extremely important:

```python
todo.owner_id != owner_id
```

It prevents this:

```text
User A
  ↓
GET /todos/99

Todo 99 belongs to User B
```

from exposing User B's data.

That's authorization.

---

# 37. List todos

```python
def list_todos(
    session: Session,
    owner_id: int,
) -> list[Todo]:

    statement = (
        select(Todo)
        .where(Todo.owner_id == owner_id)
        .order_by(Todo.id.desc())
    )

    return list(session.exec(statement).all())
```

---

# 38. Update todo

```python
def update_todo(
    session: Session,
    todo: Todo,
    data: TodoUpdate,
) -> Todo:

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo
```

This:

```python
exclude_unset=True
```

is important for PATCH.

Suppose the request is:

```json
{
    "completed": true
}
```

We want to change only:

```text
completed
```

not accidentally replace:

```text
title
description
```

with `None`.

---

# 39. Delete todo

```python
def delete_todo(
    session: Session,
    todo: Todo,
) -> None:

    session.delete(todo)
    session.commit()
```

---

# 40. Todo routes

Create:

```text
app/api/routes/todos.py
```

```python
from fastapi import APIRouter, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.todo import (
    TodoCreate,
    TodoPublic,
    TodoUpdate,
)
from app.services.todos import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
```

---

# 41. Create todo

```python
@router.post(
    "",
    response_model=TodoPublic,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: TodoCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    return create_todo(
        session=session,
        data=data,
        owner_id=current_user.id,
    )
```

Notice how clean the route is.

It basically says:

```text
request
 ↓
authenticated user
 ↓
service
 ↓
database
 ↓
response
```

---

# 42. List todos

```python
@router.get(
    "",
    response_model=list[TodoPublic],
)
def list_all(
    current_user: CurrentUser,
    session: SessionDep,
):
    return list_todos(
        session=session,
        owner_id=current_user.id,
    )
```

---

# 43. Get one

```python
@router.get(
    "/{todo_id}",
    response_model=TodoPublic,
)
def get_one(
    todo_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    return get_todo(
        session=session,
        todo_id=todo_id,
        owner_id=current_user.id,
    )
```

---

# 44. Update

```python
@router.patch(
    "/{todo_id}",
    response_model=TodoPublic,
)
def update(
    todo_id: int,
    data: TodoUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    todo = get_todo(
        session=session,
        todo_id=todo_id,
        owner_id=current_user.id,
    )

    return update_todo(
        session=session,
        todo=todo,
        data=data,
    )
```

---

# 45. Delete

```python
@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    todo_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    todo = get_todo(
        session=session,
        todo_id=todo_id,
        owner_id=current_user.id,
    )

    delete_todo(
        session=session,
        todo=todo,
    )

    return None
```

---

# 46. Main application

Now create:

```text
app/main.py
```

```python
from fastapi import FastAPI

from app.api.routes import auth, todos, users


app = FastAPI(
    title="Todo API",
    version="1.0.0",
)


app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    users.router,
    prefix="/api/v1",
)

app.include_router(
    todos.router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

This is intentionally small.

`main.py` should mostly assemble the application rather than contain all your business logic.

---

# 47. Create the database migration system

We don't want this:

```python
SQLModel.metadata.create_all(engine)
```

as our production database management strategy.

That's okay for tiny experiments.

For a real application, use **Alembic migrations**.

Initialize Alembic:

```bash
uv run alembic init migrations
```

You'll get:

```text
migrations/
    versions/
    env.py
    script.py.mako

alembic.ini
```

---

# 48. Configure Alembic

Open:

```text
migrations/env.py
```

Import your settings and models.

You'll want something conceptually like:

```python
from sqlmodel import SQLModel

from app.core.config import settings
from app.models import Todo, User


target_metadata = SQLModel.metadata
```

The imports are important.

Why?

Because Python has to actually load:

```text
User
Todo
```

before SQLModel's metadata knows about their tables.

---

# 49. Database URL in Alembic

Rather than hard-coding:

```ini
sqlalchemy.url = ...
```

you can configure Alembic from your application settings.

In `migrations/env.py`, set the URL dynamically:

```python
from alembic import context

from app.core.config import settings


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)
```

Then:

```python
target_metadata = SQLModel.metadata
```

---

# 50. Generate your first migration

Run:

```bash
uv run alembic revision --autogenerate -m "create users and todos"
```

Alembic compares:

```text
Python models
     ↓
SQLModel.metadata
```

against:

```text
PostgreSQL schema
```

and generates a migration.

You should see a file in:

```text
migrations/versions/
```

---

# 51. Apply the migration

Run:

```bash
uv run alembic upgrade head
```

Now PostgreSQL gets:

```text
users
todos
```

You can check using:

```bash
docker exec -it fastapi_postgres psql -U app -d app_db
```

Then:

```sql
\dt
```

You should see the tables.

---

# 52. Why migrations matter

Imagine version 1:

```text
users
- id
- username
```

Then version 2:

```text
users
- id
- username
- email
```

You change the model:

```python
email: str
```

Then generate:

```bash
uv run alembic revision --autogenerate -m "add email"
```

and apply:

```bash
uv run alembic upgrade head
```

Now the database evolves in a controlled way.

This is essential when deploying to production.

---

# 53. Run FastAPI

The current FastAPI documentation uses:

```bash
uv run fastapi dev
```

for development. ([FastAPI](https://fastapi.tiangolo.com/tutorial/?utm_source=chatgpt.com "Tutorial - User Guide - FastAPI"))

So run:

```bash
uv run fastapi dev app/main.py
```

You should see something similar to:

```text
FastAPI
Starting development server
```

---

# 54. Open Swagger

Go to:

```text
http://127.0.0.1:8000/docs
```

You'll see Swagger UI.

FastAPI automatically generates this from your application/OpenAPI schema.

You should see:

```text
authentication
users
todos
```

---

# 55. Test registration

Use Swagger or curl.

Request:

```http
POST /api/v1/auth/register
```

JSON:

```json
{
  "email": "john@example.com",
  "username": "john",
  "password": "secret123"
}
```

Response:

```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "john",
  "is_active": true,
  "created_at": "..."
}
```

Notice:

```text
hashed_password
```

is missing.

That's intentional.

---

# 56. Test login

Call:

```http
POST /api/v1/auth/login
```

The body is form data:

```text
username=john
password=secret123
```

You should get:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

# 57. Authorize Swagger

Click:

```text
Authorize
```

Enter:

```text
username: john
password: secret123
```

Swagger can then use the OAuth2 security definition to authenticate subsequent requests.

This is one of the advantages of using FastAPI's built-in security abstractions instead of manually reading an `Authorization` header everywhere. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/first-steps/?utm_source=chatgpt.com "Security - First Steps - FastAPI"))

---

# 58. Create a Todo

Call:

```http
POST /api/v1/todos
```

with:

```json
{
  "title": "Learn FastAPI",
  "description": "Build a real API"
}
```

Because the endpoint has:

```python
current_user: CurrentUser
```

FastAPI first executes:

```text
OAuth2PasswordBearer
        ↓
get_current_user()
        ↓
JWT validation
        ↓
PostgreSQL user lookup
        ↓
CurrentUser
        ↓
create todo
```

The todo receives:

```text
owner_id = current_user.id
```

So the database records the relationship.

---

# 59. Get your todos

Call:

```http
GET /api/v1/todos
```

You might get:

```json
[
  {
    "id": 1,
    "title": "Learn FastAPI",
    "description": "Build a real API",
    "completed": false,
    "created_at": "...",
    "owner_id": 1
  }
]
```

---

# 60. Update a todo

Call:

```http
PATCH /api/v1/todos/1
```

with:

```json
{
  "completed": true
}
```

Because we use:

```python
data.model_dump(exclude_unset=True)
```

only the provided property changes.

---

# 61. Delete it

Call:

```http
DELETE /api/v1/todos/1
```

Response:

```text
204 No Content
```

That's the normal REST-style response for a successful deletion where there is no response body.

---

# 62. The complete request lifecycle

This is the most important thing to understand.

Suppose you send:

```http
GET /api/v1/todos/10

Authorization: Bearer eyJ...
```

FastAPI receives it.

### Step 1 — routing

FastAPI finds:

```python
@router.get("/{todo_id}")
```

### Step 2 — dependency resolution

It sees:

```python
current_user: CurrentUser
```

which expands to:

```python
Depends(get_current_user)
```

### Step 3 — OAuth2 extraction

`OAuth2PasswordBearer` extracts:

```text
eyJ...
```

from:

```http
Authorization: Bearer eyJ...
```

### Step 4 — JWT verification

We execute:

```python
jwt.decode(...)
```

### Step 5 — database lookup

We find:

```text
users.username == JWT.sub
```

### Step 6 — authorization

We query:

```text
todo.id == 10
AND
todo.owner_id == current_user.id
```

### Step 7 — database

PostgreSQL returns the row.

### Step 8 — response model

FastAPI converts the result into:

```python
TodoPublic
```

### Step 9 — JSON

Client receives JSON.

So:

```text
HTTP
 ↓
FastAPI router
 ↓
Dependency Injection
 ↓
JWT
 ↓
User
 ↓
Authorization
 ↓
SQLModel
 ↓
PostgreSQL
 ↓
Pydantic/response model
 ↓
JSON
```

That's the architecture you should internalize.

---

# 63. Why dependency injection is so important

You could write:

```python
token = request.headers["Authorization"]
```

in every endpoint.

Don't.

Instead:

```python
current_user: CurrentUser
```

Now authentication is centralized.

FastAPI's dependency system is specifically intended for things such as shared logic, database connections, authentication, and authorization. ([FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/?utm_source=chatgpt.com "Dependencies - FastAPI"))

This gives you:

```text
Endpoint A ─┐
Endpoint B ─┼──> get_current_user()
Endpoint C ─┤
Endpoint D ─┘
```

instead of duplicating authentication code.

---

# 64. Why we use services

We could put this directly into the route:

```python
@router.post(...)
def create(...):
    todo = Todo(...)
    session.add(todo)
    session.commit()
    ...
```

That works.

But as your application grows, your routes become enormous.

Instead:

```text
route
  ↓
service
  ↓
database
```

The route handles HTTP concerns:

```text
status codes
request validation
dependencies
response models
```

The service handles application logic:

```text
create todo
update todo
delete todo
authorization rules
```

This makes testing and maintenance easier.

---

# 65. One improvement: email validation

Our example currently has:

```python
email: str
```

For a real application, use Pydantic's email type.

Install:

```bash
uv add "pydantic[email]"
```

Then:

```python
from pydantic import EmailStr
```

and:

```python
class UserCreate(SQLModel):
    email: EmailStr
    username: str
    password: str
```

Now FastAPI validates the request before your endpoint runs.

---

# 66. One improvement: password validation

Don't allow:

```text
password = "123"
```

For example:

```python
from pydantic import Field


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
```

Now invalid input gets rejected automatically.

FastAPI/Pydantic handles validation before your business logic.

---

# 67. One important security improvement: don't expose whether an account exists

For login we correctly use:

```text
Incorrect username or password
```

rather than:

```text
Username doesn't exist
```

versus:

```text
Wrong password
```

This makes account enumeration harder.

---

# 68. JWT expiration

Our JWT contains:

```python
"exp": expire
```

This means:

```text
JWT created
      ↓
30 minutes
      ↓
expired
```

The client then needs to authenticate again, unless you implement a refresh-token system.

The official FastAPI JWT example also demonstrates expiration and validation of JWTs. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))

---

# 69. Access tokens vs refresh tokens

For a more production-grade application, I'd eventually use:

```text
Access token
    ↓
short lifetime
5–30 minutes

Refresh token
    ↓
longer lifetime
days/weeks
```

The access token is used on API calls.

The refresh token obtains a new access token.

For the first version, however:

```text
one short-lived access JWT
```

is much easier to understand.

---

# 70. JWT algorithm

We're using:

```env
ALGORITHM=HS256
```

This is symmetric signing:

```text
secret
  ↓
sign JWT

secret
  ↓
verify JWT
```

For a distributed architecture you may eventually prefer asymmetric algorithms such as:

```text
RS256
ES256
```

where:

```text
private key → signs

public key → verifies
```

The current FastAPI docs note that if you use RSA/ECDSA algorithms with PyJWT, you should install the cryptography dependencies. ([FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"))

For learning and a small service, HS256 is perfectly reasonable.

---

# 71. Don't put secrets in the JWT

Don't do:

```json
{
  "sub": "john",
  "password": "secret123"
}
```

JWT payloads are not encrypted by default.

A JWT should contain things such as:

```json
{
  "sub": "john",
  "exp": 1780000000
}
```

not sensitive credentials.

---

# 72. Database authorization is separate from authentication

This distinction is extremely important.

### Authentication

> Who are you?

JWT:

```text
user = john
```

### Authorization

> Are you allowed to access this resource?

Database check:

```python
todo.owner_id == current_user.id
```

So:

```text
Authentication
     ↓
Who?
     ↓
John

Authorization
     ↓
Can John access Todo 10?
     ↓
Does Todo 10 belong to John?
```

A lot of beginner APIs implement authentication and forget authorization.

---

# 73. HTTP status codes we use

Our API uses:

```text
200 OK
```

for successful reads/updates.

```text
201 Created
```

for creation.

```text
204 No Content
```

for deletion.

```text
400 Bad Request
```

for invalid registration state such as an existing username.

```text
401 Unauthorized
```

for invalid/missing authentication.

```text
404 Not Found
```

when the requested todo doesn't exist or doesn't belong to the user.

FastAPI provides `HTTPException` for these API error responses. ([FastAPI](https://fastapi.tiangolo.com/tutorial/handling-errors/?utm_source=chatgpt.com "Handling Errors - FastAPI"))

---

# 74. Why `404` instead of saying "this belongs to another user"?

Suppose:

```http
GET /todos/999
```

belongs to someone else.

We respond:

```json
{
  "detail": "Todo not found"
}
```

rather than:

```json
{
  "detail": "Todo exists but belongs to user 42"
}
```

That's safer because we don't reveal the existence or ownership of resources the user shouldn't access.

---

# 75. A more complete production architecture

Once the application grows, I'd evolve it toward:

```text
app/
│
├── main.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── logging.py
│
├── db/
│   ├── session.py
│   └── models.py
│
├── models/
│   ├── user.py
│   └── todo.py
│
├── schemas/
│   ├── auth.py
│   ├── user.py
│   └── todo.py
│
├── api/
│   ├── deps.py
│   └── routes/
│
├── services/
│
└── repositories/
```

You don't need repositories immediately.

Start simple.

---

# 76. Where each piece belongs

A useful mental model:

### `models/`

Database representation.

```text
What does the database store?
```

### `schemas/`

API input/output representation.

```text
What does the API accept/return?
```

### `routes/`

HTTP layer.

```text
What URL does the client call?
```

### `services/`

Business logic.

```text
What should the application do?
```

### `core/`

Infrastructure/security/configuration.

```text
How is the application configured?
How is authentication implemented?
```

### `db/`

Database infrastructure.

```text
How do we connect to PostgreSQL?
```

### `deps.py`

Reusable FastAPI dependencies.

```text
How do endpoints obtain sessions/users/etc.?
```

---

# 77. What happens if PostgreSQL goes down?

Suppose:

```text
FastAPI
   ↓
PostgreSQL ❌
```

Your database operations fail.

That's why production systems should also have:

- database health monitoring
    
- connection pooling
    
- retry strategy where appropriate
    
- backups
    
- migrations
    
- monitoring/logging
    

Don't blindly retry every SQL operation because retries can create duplicate writes.

---

# 78. Connection pooling

SQLAlchemy's engine manages database connections through a pool.

That means your application doesn't necessarily create a brand-new TCP/database connection for every query.

Conceptually:

```text
FastAPI requests
      │
      ├──────┐
      ├──────┤
      ├──────┤
      └──────┘
          │
          ▼
   connection pool
    ┌──┬──┬──┬──┐
    │  │  │  │  │
    └──┴──┴──┴──┘
          │
          ▼
      PostgreSQL
```

The exact pool configuration should be tuned for your deployment.

---

# 79. Don't create one Session globally

Don't do:

```python
session = Session(engine)
```

and reuse it forever.

Instead:

```python
def get_session():
    with Session(engine) as session:
        yield session
```

so each request gets its own session lifecycle.

This matches the pattern demonstrated by the current FastAPI SQL database docs. ([FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com "SQL (Relational) Databases - FastAPI"))

---

# 80. Don't use `create_all()` as your deployment strategy

You'll often see:

```python
SQLModel.metadata.create_all(engine)
```

in beginner tutorials.

It's useful for a tiny application.

But when your application evolves:

```text
database version 1
       ↓
database version 2
       ↓
database version 3
```

you want explicit migrations.

That's why we're using:

```text
Alembic
```

---

# 81. Testing

Once the application works, add:

```text
tests/
├── conftest.py
├── test_auth.py
├── test_users.py
└── test_todos.py
```

Install:

```bash
uv add --dev pytest httpx
```

Then test scenarios such as:

```text
register user
login
get /users/me
create todo
list todos
update todo
delete todo
```

And importantly:

```text
User A cannot access User B's todo
```

That last test is an authorization test, not just a CRUD test.

---

# 82. Database tests

For proper integration tests, don't rely on your personal development database.

Use a separate test database, e.g.:

```text
app_db
app_test_db
```

or a disposable PostgreSQL container.

Your tests should be reproducible.

---

# 83. Production deployment

A typical production architecture becomes:

```text
                   Internet
                      │
                      ▼
                HTTPS / TLS
                      │
                      ▼
             reverse proxy/load
                  balancer
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     FastAPI #1              FastAPI #2
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
                 PostgreSQL
```

FastAPI's official full-stack template is also a useful reference for a larger production-shaped stack; it uses FastAPI, SQLModel, PostgreSQL, JWT authentication, Docker Compose, testing, and deployment tooling. ([FastAPI](https://fastapi.tiangolo.com/project-generation/?utm_source=chatgpt.com "Full Stack FastAPI Template - FastAPI"))

---

# 84. Production environment variables

Instead of:

```env
DATABASE_URL=localhost
```

production might have:

```env
DATABASE_URL=postgresql+psycopg://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

These should be provided by your hosting/secrets system.

Never commit:

```text
.env
```

containing real credentials.

---

# 85. HTTPS is mandatory for production authentication

Your development environment can use:

```text
http://localhost
```

Production should use:

```text
https://api.example.com
```

Otherwise credentials/tokens can be exposed in transit.

---

# 86. What we have accomplished

At this point, the architecture is:

```text
                         FastAPI
                            │
                ┌───────────┴───────────┐
                │                       │
             Auth API               Todo API
                │                       │
         ┌──────┴──────┐          JWT dependency
         │             │                 │
      Register       Login               │
         │             │                 │
         ▼             ▼                 ▼
      Argon2       verify password   current user
         │             │                 │
         └──────┬──────┘                 │
                │                        │
                └──────────┬─────────────┘
                           │
                           ▼
                       SQLModel
                           │
                           ▼
                      PostgreSQL
```

And:

```text
Client
  │
  │ username/password
  ▼
/auth/login
  │
  ▼
JWT
  │
  │ Authorization: Bearer ...
  ▼
Protected API
  │
  ▼
JWT validation
  │
  ▼
Current User
  │
  ▼
Authorization
  │
  ▼
CRUD
```

---

# 87. The most important concepts to learn

Don't just copy the code. Make sure you understand these eight concepts:

### 1. FastAPI routing

```python
@router.get(...)
@router.post(...)
@router.patch(...)
@router.delete(...)
```

### 2. Pydantic/SQLModel validation

```python
class TodoCreate(...)
```

### 3. Dependency injection

```python
Annotated[..., Depends(...)]
```

### 4. Database sessions

```python
Session(engine)
```

### 5. ORM/database queries

```python
select(Todo).where(...)
```

### 6. Password hashing

```python
hash_password(...)
verify_password(...)
```

### 7. JWT authentication

```python
create_access_token(...)
jwt.decode(...)
```

### 8. Authorization

```python
todo.owner_id == current_user.id
```

If you understand those eight, you understand the foundation of most FastAPI CRUD applications.

---

# 88. Recommended learning order

Don't try to learn everything simultaneously.

I'd learn it in this order:

```text
1. FastAPI basics
       ↓
2. Request/response models
       ↓
3. Dependency injection
       ↓
4. SQLModel
       ↓
5. PostgreSQL
       ↓
6. Alembic
       ↓
7. Password hashing
       ↓
8. JWT
       ↓
9. Authentication dependencies
       ↓
10. Authorization
       ↓
11. Testing
       ↓
12. Docker/deployment
```

The official FastAPI tutorial is structured as a progressive reference, and its database/security sections map very well onto this progression. ([FastAPI](https://fastapi.tiangolo.com/tutorial/?utm_source=chatgpt.com "Tutorial - User Guide - FastAPI"))

---

# 89. One thing I'd change for a serious production app

The example above uses:

```text
HS256
```

and a simple access-token-only model because it keeps the concepts understandable.

For a serious application, I'd add:

```text
short-lived access token
        +
refresh token
        +
token revocation strategy
        +
rate limiting
        +
email verification
        +
password reset
        +
account lockout/risk controls
        +
audit logging
```

And depending on the application, you might use an external identity provider instead of implementing the complete identity system yourself.

---

# 90. Your final project should conceptually look like this

```text
fastapi-crud/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── todos.py
│   │
│   └── services/
│       └── todos.py
│
├── migrations/
│   └── versions/
│
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

That is a very reasonable foundation for a real FastAPI backend.

---

## The key takeaway

The important architecture isn't really "FastAPI + JWT + PostgreSQL."

It's this:

```text
                    ┌───────────────┐
                    │    Router     │
                    │ HTTP concern  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Dependencies  │
                    │ Auth / Session │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Service    │
                    │ Business logic│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   SQLModel    │
                    │     ORM       │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    └───────────────┘
```

with authentication running as a dependency:

```text
Authorization: Bearer JWT
             │
             ▼
      OAuth2PasswordBearer
             │
             ▼
        jwt.decode()
             │
             ▼
        find User
             │
             ▼
       CurrentUser
             │
             ▼
       authorization
             │
             ▼
          CRUD
```

That design scales far better than putting database queries, password hashing, JWT code, and routes all into one `main.py`.

The official FastAPI documentation currently aligns closely with the choices above: `uv`-based projects, `Annotated` dependencies, SQLModel for SQL databases, and PyJWT + `pwdlib`/Argon2 for the JWT/password-hashing flow. ([FastAPI](https://fastapi.tiangolo.com/release-notes/?utm_source=chatgpt.com "Release Notes - FastAPI"))

### Official references

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/?utm_source=chatgpt.com)
    
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com)
    
- [FastAPI OAuth2 + JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com)
    
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/?utm_source=chatgpt.com)
    
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/?utm_source=chatgpt.com)
    
- [FastAPI Full Stack Template](https://fastapi.tiangolo.com/project-generation/?utm_source=chatgpt.com)
