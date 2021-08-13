from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Formación
# Setting Isolation for Individual Transactions 1/2
def context_manager(session: Session):
    user0 = models.User(email="email0@email.com", hashed_password="notreallyhashed")
    user1 = models.User(email="email1@email.com", hashed_password="notreallyhashed")

    with session.begin():
        # call connection() with options before any other operations proceed.
        # this will procure a new connection from the bound engine and begin a
        # real database transaction.
        session.connection(execution_options={'isolation_level': 'SERIALIZABLE'})

        session.query(models.User).delete()
        session.add(user0)
        session.add(user1)
    # commits transaction at the end, or rolls back if there
    # was an exception raised

    # outside the block, the transaction has been committed.  the connection is
    # released and reverted to its previous isolation level.


# Setting Isolation for Individual Transactions 2/2
def commit_as_you_go(session: Session):
    # call connection() with options before any other operations proceed.
    # this will procure a new connection from the bound engine and begin a real
    # database transaction.
    session.connection(execution_options={'isolation_level': 'SERIALIZABLE'})

    session.query(models.User).delete()
    user2 = models.User(email="email2@email.com", hashed_password="notreallyhashed")
    user3 = models.User(email="email3@email.com", hashed_password="notreallyhashed")
    session.add(user2)
    session.add(user3)

    # ... work with session in SERIALIZABLE isolation level...

    # commit transaction.  the connection is released
    # and reverted to its previous isolation level.
    session.commit()  # commits

    # subsequent to commit() above, a new transaction may be begun if desired,
    # which will proceed with the previous default isolation level unless
    # it is set again.

    # will automatically begin again
    user4 = models.User(email="email4@email.com", hashed_password="notreallyhashed")
    user5 = models.User(email="email5@email.com", hashed_password="notreallyhashed")
    session.add_all([user4, user5])
    session.commit()  # commits

    still_another_object = models.User(email="nouser@email.com", hashed_password="notreallyhashed")
    session.add(still_another_object)
    session.flush()  # flush still_another_object
    session.rollback()  # rolls back still_another_object


def savepoint(session: Session):
    u1 = models.User(email="email1@email.com", hashed_password="notreallyhashed")
    u2 = models.User(email="email2@email.com", hashed_password="notreallyhashed")
    u3 = models.User(email="email3@email.com", hashed_password="notreallyhashed")

    with session.begin():
        session.query(models.User).delete()
        session.add(u1)
        session.add(u2)

        nested = session.begin_nested()  # establish a savepoint
        session.add(u3)
        nested.rollback()  # rolls back u3, keeps u1 and u2


def savepoint_with_context_manager(session: Session):
    session.query(models.User).delete()
    session.commit()
    u1 = models.User(email="email1@email.com", hashed_password="notreallyhashed")

    for record in [u1]:
        try:
            with session.begin_nested():
                session.merge(record)
        except:
            print("Skipped record %s" % record)
    session.commit()
