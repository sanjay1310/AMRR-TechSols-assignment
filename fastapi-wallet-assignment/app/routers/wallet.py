from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from ..database import SessionLocal
from .. import crud, models, schemas

router = APIRouter(prefix="/wallet", tags=["Wallet"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{user_id}", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
def update_wallet(user_id: int, payload: schemas.WalletUpdateIn, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    amount = Decimal(str(payload.amount))
    try:
        if payload.mode == "set":
            delta = amount - user.wallet_balance
            tx = crud.add_transaction(db, user, delta, "adjust", payload.description or "Balance set")
        elif payload.mode == "credit":
            tx = crud.add_transaction(db, user, amount, "credit", payload.description or "Credit")
        elif payload.mode == "debit":
            tx = crud.add_transaction(db, user, amount, "debit", payload.description or "Debit")
        else:
            raise HTTPException(status_code=400, detail="Invalid mode")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    db.commit()
    db.refresh(tx)
    return tx
