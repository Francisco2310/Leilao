import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from presentation.api.main import app
from infrastructure.database.database import get_db, Base
import os
from urllib.parse import urlparse
import socket

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+psycopg2://user:password@localhost:5433/auctions_test"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def _is_postgres_running() -> bool:
    try:
        parsed = urlparse(DATABASE_URL)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def pytest_ignore_collect(collection_path, *args, **kwargs):
    if not _is_postgres_running():
        return True

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)



@pytest.fixture(scope="function")
def client(db_session):
  def override_get_db():
    try:
        yield db_session
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    
  app.dependency_overrides[get_db] = override_get_db

  with TestClient(app) as c:
    yield c
    app.dependency_overrides.clear()



    
    
        