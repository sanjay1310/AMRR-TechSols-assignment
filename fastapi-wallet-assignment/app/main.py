from fastapi import FastAPI
from .database import Base, engine, SessionLocal
from . import models, crud, schemas
from .config import settings
from .routers import users, wallet, transactions
from decimal import Decimal

app = FastAPI(title="Wallet Service", version="1.0.0")

# Create tables
Base.metadata.create_all(bind=engine)

# Seed sample data if requested
if settings.seed:
    from sqlalchemy.orm import Session
    with SessionLocal() as db:
        if not db.query(models.User).first():
            crud.create_user(db, schemas.UserCreate(name="Aarav", email="aarav@example.com", phone="9000000001", wallet_balance=1000))
            crud.create_user(db, schemas.UserCreate(name="Diya", email="diya@example.com", phone="9000000002", wallet_balance=500))
            crud.create_user(db, schemas.UserCreate(name="Vivaan", email="vivaan@example.com", phone="9000000003", wallet_balance=0))
            db.commit()

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Wallet Service is running", "docs": "/docs"}

app.include_router(users.router)
app.include_router(wallet.router)
app.include_router(transactions.router)
