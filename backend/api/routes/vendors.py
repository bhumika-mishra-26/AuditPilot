from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
from typing import List

router = APIRouter()

# DATA_FILE path resolution
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_FILE = BASE_DIR / "data" / "vendors.json"

class Vendor(BaseModel):
    vendor_id: str
    name: str
    status: str = "active"
    risk: str = "Low"
    spend: str = "$0"

def _load_vendors() -> List[dict]:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def _save_vendors(vendors: List[dict]):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(vendors, f, indent=2)

@router.get("/", response_model=List[Vendor])
async def list_vendors():
    try:
        return _load_vendors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Vendor)
async def onboard_vendor(vendor: Vendor):
    vendors = _load_vendors()
    if any(v["vendor_id"] == vendor.vendor_id for v in vendors):
        raise HTTPException(status_code=400, detail="Vendor ID already exists")
    
    new_vendor = vendor.dict()
    vendors.append(new_vendor)
    _save_vendors(vendors)
    return vendor
