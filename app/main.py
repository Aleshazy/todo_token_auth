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

# Main API module.
# Request flow: route -> auth dependency (if protected) -> ORM query -> schema response.

# POST /register -> create account
# POST /login -> get token
# GET /todos -> all my todos
# GET /todos/pending -> only incomplete
# GET /todos/pending/count -> number of incomplete
# POST /todos -> create todo
# PATCH /todos/{todo_id}/status -> change completion
# DELETE /todos/{todo_id} -> delete completed todo
app = FastAPI(title="TODO List API")


@app.on_event("startup")
# Create tables at app startup.
def startup():
    Base.metadata.create_all(bind=engine)


# Public auth routes.
@app.post("/register")
# Create a new user account.
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}


@app.post("/login", response_model=TokenResponse)
# Authenticate user and return access token.
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token, expires_at = create_token_for_user(db, user)
    return TokenResponse(access_token=token, expires_at=expires_at)


# Protected todo routes.
@app.get("/todos", response_model=List[TodoResponse])
# Return all todos for current user.
def get_all_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Todo).filter(Todo.owner_id == current_user.id).order_by(Todo.id).all()
    return rows


@app.get("/todos/pending", response_model=List[TodoResponse])
# Return only incomplete todos.
def get_pending_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Todo)
        .filter(Todo.owner_id == current_user.id, Todo.is_complete == False)
        .order_by(Todo.id)
        .all()
    )
    return rows


@app.get("/todos/pending/count", response_model=PendingCountResponse)
# Count incomplete todos using ORM.
def get_pending_todos_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pending_count = db.query(Todo).filter(Todo.owner_id == current_user.id, Todo.is_complete == False).count()
    return PendingCountResponse(pending_count=pending_count)


@app.post("/todos", response_model=TodoResponse, status_code=201)
# Create a new todo for current user.
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


@app.patch("/todos/{todo_id}/status", response_model=TodoResponse)
# Update todo completion status.
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


@app.delete("/todos/{todo_id}")
# Delete todo only if it is complete.
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