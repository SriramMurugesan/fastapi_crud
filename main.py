from fastapi import FastAPI, Depends, HTTPException
from fastapi_mcp import FastApiMCP
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User, operation_id="create_user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User], operation_id="read_users")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=schemas.User, operation_id="read_user")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User, operation_id="update_user")
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", operation_id="delete_user")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

@app.get("/", operation_id="read_root")
def read_root():
    return {"message": "FastAPI CRUD app is running!"}

# ✅ Mount MCP after all routes
mcp = FastApiMCP(
    app,
    include_operations=[
        "create_user",
        "read_users",
        "read_user",
        "update_user",
        "delete_user",
    ]
)
mcp.mount()
