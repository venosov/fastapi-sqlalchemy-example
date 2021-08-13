from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, isolation_level='READ UNCOMMITTED'
)

# the Engine.execution_options() method, which will produce a shallow copy of the original Engine which shares the same
# connection pool as the parent engine. This is often preferable when operations will be separated into “transactional”
# and “autocommit” operations
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

# Setting Isolation For A Sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
autocommit_session = sessionmaker(autocommit_engine)

Base = declarative_base()
