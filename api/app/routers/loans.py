import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_db
from app.models import Book, Loan
from app.schemas.loan import LoanCreate, LoanOut, LoanReturn

router = APIRouter()


async def _get_loan_or_404(loan_id: uuid.UUID, db: AsyncSession) -> Loan:
    result = await db.execute(select(Loan).where(Loan.id == loan_id))
    loan = result.scalar_one_or_none()
    if loan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_loan(
    body: LoanCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> LoanOut:
    result = await db.execute(select(Book.id).where(Book.id == body.book_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    loan = Loan(
        book_id=body.book_id,
        borrower_name=body.borrower_name,
        due_date=body.due_date,
        notes=body.notes,
    )
    db.add(loan)
    await db.commit()
    await db.refresh(loan)
    return LoanOut.model_validate(loan)


@router.get("/")
async def list_loans(
    open_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> list[LoanOut]:
    stmt = select(Loan).order_by(Loan.loaned_at.desc())
    if open_only:
        stmt = stmt.where(Loan.returned_at.is_(None))
    result = await db.execute(stmt)
    return [LoanOut.model_validate(loan) for loan in result.scalars().all()]


@router.post("/{loan_id}/return")
async def return_loan(
    loan_id: uuid.UUID,
    body: LoanReturn | None = None,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(get_current_user),
) -> LoanOut:
    loan = await _get_loan_or_404(loan_id, db)

    if body is not None and body.returned_at is not None:
        loan.returned_at = body.returned_at
    else:
        loan.returned_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(loan)
    return LoanOut.model_validate(loan)
