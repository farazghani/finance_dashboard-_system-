from pydantic import BaseModel, field_validator
from datetime import date as dt_date


class RecordBase(BaseModel):
    amount: float
    type: str
    category: str
    date: dt_date
    notes: str | None = None


class RecordCreate(RecordBase):

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["debit", "credit"]:
            raise ValueError("Type must be debit or credit")
        return v

class RecordUpdate(BaseModel):
    amount: float | None = None
    type: str | None = None
    category: str | None = None
    date: dt_date | None = None
    notes: str | None = None

    @field_validator("amount")
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("type")
    def validate_type(cls, v):
        if v is not None and v not in ["debit", "credit"]:
            raise ValueError("Type must be debit or credit")
        return v
    

class RecordResponse(RecordBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True
