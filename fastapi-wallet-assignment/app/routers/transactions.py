from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import SessionLocal
from .. import crud, schemas

router = APIRouter(prefix="/users/{user_id}/transactions", tags=["Transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[schemas.TransactionOut])
def fetch_transactions(
    user_id: int,
    limit: int = Query(100, le=500),
    offset: int = 0,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    type: Optional[str] = Query(None, description="Filter by type: credit|debit|adjust"),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    txs = crud.get_transactions(db, user_id=user_id, limit=limit, offset=offset, start=start, end=end, ttype=type)
    return txs
