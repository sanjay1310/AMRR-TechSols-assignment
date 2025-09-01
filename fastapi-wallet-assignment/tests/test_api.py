import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SEED"] = ""

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_user_lifecycle_and_wallet():
    # create a user
    u = {"name": "Test User", "email": "test@example.com", "phone": "1234567890", "wallet_balance": 0}
    r = client.post("/users", json=u)
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]

    # list users
    r = client.get("/users")
    assert r.status_code == 200
    assert any(x["id"] == user_id for x in r.json())

    # credit
    r = client.post(f"/wallet/{user_id}", json={"amount": 200, "mode": "credit"})
    assert r.status_code == 201
    # debit
    r = client.post(f"/wallet/{user_id}", json={"amount": 50, "mode": "debit"})
    assert r.status_code == 201

    # fetch transactions
    r = client.get(f"/users/{user_id}/transactions")
    assert r.status_code == 200
    assert len(r.json()) == 2

    # set balance
    r = client.post(f"/wallet/{user_id}", json={"amount": 1000, "mode": "set"})
    assert r.status_code == 201

    # verify user balance in list
    r = client.get("/users")
    user = [x for x in r.json() if x["id"] == user_id][0]
    assert round(user["wallet_balance"], 2) == 1000.00

    # overdraft should fail
    r = client.post(f"/wallet/{user_id}", json={"amount": 2000, "mode": "debit"})
    assert r.status_code == 409
