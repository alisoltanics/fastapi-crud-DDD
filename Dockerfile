FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir fastapi uvicorn sqlmodel psycopg2-binary pyjwt pydantic-settings pwdlib argon2-cffi python-multipart alembic

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
