import os

os.environ.setdefault("DB_URL", "sqlite:///./test_backend.db")

import pytest
from sqlalchemy import text

from app.db.base import Base
from app.db.session import SessionLocal, engine


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.execute(text("DELETE FROM category"))
        session.execute(text("DELETE FROM videos"))
        session.commit()
