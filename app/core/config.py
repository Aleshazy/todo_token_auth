import os
from dotenv import load_dotenv

# Load variables from .env into process environment.
load_dotenv()

# DB connection string for SQLAlchemy engine.
# Default to SQLite for quick local runs when `DATABASE_URL` is not set.
# For production or Docker setups keep using a Postgres URL in the environment.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./todo.db",
)
# Token lifetime in minutes for auth tokens.
TOKEN_LIFETIME_MINUTES = int(os.getenv("TOKEN_LIFETIME_MINUTES", "60"))