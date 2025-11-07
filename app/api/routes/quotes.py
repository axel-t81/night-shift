from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.schemas.quote import Quote as QuoteSchema, QuoteCreate
from app.services.quote_service import create_quote, get_latest_quote


router = APIRouter()


@router.get("/latest", response_model=QuoteSchema)
def read_latest_quote(db: Session = Depends(get_db)) -> Any:
    quote = get_latest_quote(db)
    if not quote:
        raise HTTPException(status_code=404, detail="No quote yet")
    return quote


@router.post("", response_model=QuoteSchema)
def create_new_quote(quote_in: QuoteCreate, db: Session = Depends(get_db)) -> Any:
    quote = create_quote(db, quote_in)
    return quote


