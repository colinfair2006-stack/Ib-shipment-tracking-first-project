from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShipmentBase(BaseModel):
    tracking_number: str
    origin_country: str
    destination_country: str
    carrier: str
    status: Optional[str] = "Pending"
    description: Optional[str] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    carrier: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None

class ShipmentOut(ShipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
