import secrets
from datetime import datetime, timedelta
from fastapi import Depends, Header, HTTPException
import bcrypt # Используем чистый bcrypt напрямую
from sqlalchemy.orm import Session

# ИМПОРТИРУЕМ ВСЁ НЕОБХОДИМОЕ ИЗ НАШИХ ПАПОК
from app.db.database import get_db
from app.db.models import AuthToken, User

TOKEN_LIFETIME_MINUTES = 60

# Хеширование пароля перед сохранением в базу (напрямую через bcrypt)
def hash_password(password: str) -> str:
    # Переводим строку в байты, генерируем соль и хешируем
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8') # Возвращаем обратно как строку для базы данных

# Проверка обычного пароля с хешем из базы данных
def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

# Создание и сохранение случайного токена для сессии пользователя
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

# Поддержка форматов "Bearer <token>" и обычного токена
def extract_bearer(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[len("Bearer ") :].strip()
    return authorization.strip()

# Защитная функция: извлекает пользователя по токену из заголовков HTTP-запроса
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