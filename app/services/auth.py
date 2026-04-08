import secrets
from datetime import datetime, timedelta
from fastapi import Depends, Header, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import TOKEN_LIFETIME_MINUTES
from app.db.database import get_db
from app.db.models import AuthToken, User

# This module contains all auth helpers used by API routes:
# 1) password hashing/check,
# 2) token creation,
# 3) user resolution from Authorization header.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash password before storing in DB.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Compare plain password with hash.
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# Create and store token with expiration.
def create_token_for_user(db: Session, user: User):
    token_value = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_LIFETIME_MINUTES)

    token_row = AuthToken(
        user_id=user.id,
        token=token_value,
        expires_at=expires_at,
    )
    db.add(token_row)
    db.commit()

    return token_value, expires_at


# Support both "Bearer <token>" and raw token formats.
def extract_bearer(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :].strip()
    return authorization.strip()


# Resolve current user from Authorization header.
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token_value = extract_bearer(authorization)

    token_row = db.query(AuthToken).filter(AuthToken.token == token_value).first()
    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid token")

    if token_row.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")

    return token_row.user