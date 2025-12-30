#!/usr/bin/env python3
#<!-- contest.py -->
import pytest
from app import app
from models import db

@pytest.fixture(scope='function', autouse=True)
def db_session():
    """Create a fresh database for each test function."""
    # Create all tables
    with app.app_context():
        db.create_all()
    
    yield db
    
    # Clean up after tests
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(db_session):
    """Create a test client."""
    return app.test_client()

def pytest_itemcollected(item):
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
