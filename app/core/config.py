import os
from dotenv import load_dotenv

# Load variables from .env into process environment.
load_dotenv()

# DB connection string for SQLAlchemy engine.
DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg://postgres:password@localhost:5432/todo_db",
)
# Token lifetime in minutes for auth tokens.
TOKEN_LIFETIME_MINUTES = int(os.getenv("TOKEN_LIFETIME_MINUTES", "60"))