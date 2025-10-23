from sqlalchemy.orm import Session
from typing import Optional

from app.models.quote import Quote as QuoteModel
from app.schemas.quote import QuoteCreate


def create_quote(db: Session, quote_in: QuoteCreate) -> QuoteModel:
    quote = QuoteModel(text=quote_in.text)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def get_latest_quote(db: Session) -> Optional[QuoteModel]:
    return db.query(QuoteModel).order_by(QuoteModel.created_at.desc()).first()


