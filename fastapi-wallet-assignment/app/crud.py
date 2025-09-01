from sqlalchemy.orm import Session
from sqlalchemy import select, func
from . import models
from .schemas import UserCreate
from decimal import Decimal

def get_users(db: Session):
    return db.execute(select(models.User)).scalars().all()

def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)

def create_user(db: Session, user: UserCreate):
    u = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        wallet_balance=Decimal(str(user.wallet_balance or 0))
    )
    db.add(u)
    db.flush()
    return u

def add_transaction(db: Session, user: models.User, amount: Decimal, ttype: str, description: str | None):
    tx = models.Transaction(user_id=user.id, amount=amount, type=ttype, description=description)
    if ttype == "credit":
        user.wallet_balance += amount
    elif ttype == "debit":
        if user.wallet_balance - amount < 0:
            raise ValueError("Insufficient funds")
        user.wallet_balance -= amount
    elif ttype == "adjust":
        user.wallet_balance += amount  # amount may be negative or positive
    else:
        raise ValueError("Invalid transaction type")
    db.add(tx)
    return tx

def get_transactions(db: Session, user_id: int, limit: int = 100, offset: int = 0,
                     start=None, end=None, ttype: str | None = None):
    stmt = select(models.Transaction).where(models.Transaction.user_id == user_id)
    if start is not None:
        stmt = stmt.where(models.Transaction.created_at >= start)
    if end is not None:
        stmt = stmt.where(models.Transaction.created_at <= end)
    if ttype:
        stmt = stmt.where(models.Transaction.type == ttype)
    stmt = stmt.order_by(models.Transaction.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()
