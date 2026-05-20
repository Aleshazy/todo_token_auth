from typing import List
from fastapi import Depends, FastAPI, HTTPException, Path
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.db.models import Todo, User
from app.schemas import (
    LoginRequest,
    PendingCountResponse,
    TodoCreate,
    TodoResponse,
    TodoStatusUpdate,
    TokenResponse,
    UserCreate,
)
from app.services.auth import create_token_for_user, get_current_user, hash_password, verify_password

app = FastAPI(title="TODO List API")

# Создаем таблицы в БД при запуске приложения
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# 1. Регистрация
@app.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

# 2. Логин
@app.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, expires_at = create_token_for_user(db, user)
    return TokenResponse(access_token=token, expires_at=expires_at)

# 3. Получить ВСЕ задачи пользователя
@app.get("/todos", response_model=List[TodoResponse])
def get_all_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id).order_by(Todo.id).all()

# 4. Получить только НЕВЫПОЛНЕННЫЕ задачи
@app.get("/todos/pending", response_model=List[TodoResponse])
def get_pending_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.owner_id == current_user.id, Todo.is_complete == False).order_by(Todo.id).all()

# 5. Количество невыполненных задач
@app.get("/todos/pending/count", response_model=PendingCountResponse)
def get_pending_todos_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pending_count = db.query(Todo).filter(Todo.owner_id == current_user.id, Todo.is_complete == False).count()
    return PendingCountResponse(pending_count=pending_count)

# 6. Создать новую задачу
@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(payload: TodoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = Todo(
        title=payload.title,
        description=payload.description,
        is_complete=False,
        owner_id=current_user.id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

# 7. Изменить статус задачи (выполнена/нет)
@app.patch("/todos/{todo_id}/status", response_model=TodoResponse)
def update_todo_status(
    payload: TodoStatusUpdate,
    todo_id: int = Path(ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.is_complete = payload.is_complete
    db.commit()
    db.refresh(todo)
    return todo

# 8. Удалить задачу (только если она выполнена)
@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int = Path(ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if not todo.is_complete:
        raise HTTPException(status_code=400, detail="Cannot delete incomplete todo")

    db.delete(todo)
    db.commit()
    return {"message": "Deleted", "id": todo_id}