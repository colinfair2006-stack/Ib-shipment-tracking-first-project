from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Shipment Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"message": "Shipment Tracker API is running!"}

@app.post("/shipments/", response_model=schemas.ShipmentOut)
def create_shipment(shipment: schemas.ShipmentCreate, db: Session = Depends(get_db)):
    db_shipment = models.Shipment(**shipment.dict())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

@app.get("/shipments/", response_model=List[schemas.ShipmentOut])
def list_shipments(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    origin_country: Optional[str] = None,
    destination_country: Optional[str] = None,
    carrier: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(models.Shipment)
    if status:
        query = query.filter(models.Shipment.status.ilike(f"%{status}%"))
    if origin_country:
        query = query.filter(models.Shipment.origin_country.ilike(f"%{origin_country}%"))
    if destination_country:
        query = query.filter(models.Shipment.destination_country.ilike(f"%{destination_country}%"))
    if carrier:
        query = query.filter(models.Shipment.carrier.ilike(f"%{carrier}%"))
    return query.offset(skip).limit(limit).all()

@app.get("/shipments/{shipment_id}", response_model=schemas.ShipmentOut)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment

@app.put("/shipments/{shipment_id}", response_model=schemas.ShipmentOut)
def update_shipment(shipment_id: int, updates: schemas.ShipmentUpdate, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(shipment, key, value)
    db.commit()
    db.refresh(shipment)
    return shipment

@app.delete("/shipments/{shipment_id}")
def delete_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    db.delete(shipment)
    db.commit()
    return {"detail": "Shipment deleted"}
