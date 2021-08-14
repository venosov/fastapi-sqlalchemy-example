from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine, autocommit_engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Setting Isolation for Individual Sessions 1/2
def setting_isolation_for_individual_sessions():
    db = SessionLocal(bind=autocommit_engine)
    try:
        yield db
    finally:
        db.close()


# Setting Isolation for Individual Sessions 2/2
def setting_isolation_for_individual_sessions():
    db = Session()
    db.bind_mapper(models.User, autocommit_engine)
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.User,
):
    """
    Update a user.
    """
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.update_user(db, db_obj=user, obj_in=user_in)
    return user


@app.get("/context-managers/")
def context_manager(db: Session = Depends(get_db)):
    crud.context_manager(db)


@app.get("/commit-as-you-go/")
def commit_as_you_go(db: Session = Depends(get_db)):
    crud.commit_as_you_go(db)


@app.get("/savepoint/")
def savepoint(db: Session = Depends(get_db)):
    crud.savepoint(db)


@app.get("/savepoint-with-context-manager/")
def savepoint_with_context_manager(db: Session = Depends(get_db)):
    crud.savepoint_with_context_manager(db)


if __name__ == "__main__":
    uvicorn.run("sql_app.main:app", host="127.0.0.1", port=8000, log_level="info")
