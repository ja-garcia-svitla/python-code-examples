from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

app = FastAPI()


class Product(BaseModel):
    class Config:
        orm_mode = True

    id: int
    sku: str
    name: str
    price: float
    tags: List[str] = []
    discount_percent: Optional[int]
    internal_cost: float
    created_at: datetime = datetime.now()

    @validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(status_code=400, detail="price must be positive")
        return v

    @validator("sku")
    def normalize_sku(self, v):
        return v.upper()


@app.post("/products", response_model=Product)
def create_product(product: Product):
    row = db.insert(product.dict())
    return row
