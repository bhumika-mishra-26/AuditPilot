from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from shared.db import get_session
from shared.models import Vendor

router = APIRouter()

@router.get("/", response_model=List[Vendor])
async def list_vendors(session: Session = Depends(get_session)):
    try:
        statement = select(Vendor).order_by(Vendor.name)
        results = session.exec(statement).all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/", response_model=Vendor)
async def onboard_vendor(vendor: Vendor, session: Session = Depends(get_session)):
    # Check if exists
    statement = select(Vendor).where(Vendor.vendor_id == vendor.vendor_id)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor ID already exists")
    
    try:
        session.add(vendor)
        session.commit()
        session.refresh(vendor)
        return vendor
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to onboard vendor: {str(e)}")
