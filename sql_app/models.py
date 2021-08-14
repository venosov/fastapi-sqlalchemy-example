from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    # It is strongly recommended that the version_id column be made NOT NULL.
    # The versioning feature does not support a NULL value in the versioning column.
    version_id = Column(Integer, nullable=False)

    items = relationship("Item", back_populates="owner")

    __mapper_args__ = {
        "version_id_col": version_id
    }


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
