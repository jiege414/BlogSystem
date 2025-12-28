import os
import tempfile

import pytest

from app import create_app
from extensions import db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()