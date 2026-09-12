from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────

class UserRegister(BaseModel):
    """Payload for POST /auth/register"""
    name: str
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Payload for POST /auth/login  (JSON body, not form-data)"""
    email: str
    password: str


class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    role: str = "resident"          # 'resident' | 'admin' | 'security'
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    username: Optional[str] = None
    email: EmailStr
    role: str
    profile_image: Optional[str] = None

    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


# ──────────────────────────────────────────────
# Notice Schemas
# ──────────────────────────────────────────────

class NoticeCreate(BaseModel):
    title: str
    content: str


class NoticeResponse(NoticeCreate):
    id: str = Field(alias="_id")
    date_posted: datetime
    author_id: str

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Complaint Schemas
# ──────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    title: str
    description: str


class ComplaintResponse(ComplaintCreate):
    id: str = Field(alias="_id")
    status: str
    user_id: str
    date_submitted: datetime

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Billing Schemas
# ──────────────────────────────────────────────

class BillCreate(BaseModel):
    user_id: str
    amount: float
    description: str
    due_date: datetime


class BillResponse(BillCreate):
    id: str = Field(alias="_id")
    status: str

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# House & Family Schemas
# ──────────────────────────────────────────────

class FamilyMember(BaseModel):
    name: str
    relation: str
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_group: Optional[str] = None


class HouseCreate(BaseModel):
    house_number: str
    block: str
    owner_name: str
    family_members: List[FamilyMember] = []


class HouseResponse(HouseCreate):
    id: str = Field(alias="_id")
    association_fee: float = 50.0
    status: str = "Active"
    last_payment_date: Optional[datetime] = None
    last_payment_month: Optional[str] = "No payments yet"

    class Config:
        populate_by_name = True


class AssociationFeeUpdate(BaseModel):
    monthly_fee: float


# ──────────────────────────────────────────────
# Visitor Schemas
# ──────────────────────────────────────────────

class VisitorBase(BaseModel):
    name: str
    phone: str
    house_number: str
    purpose: Optional[str] = None


class VisitorCreate(VisitorBase):
    pass


class VisitorResponse(VisitorBase):
    id: str = Field(alias="_id")
    entry_time: datetime
    exit_time: Optional[datetime] = None
    status: str = "Entered"

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Staff Schemas
# ──────────────────────────────────────────────

class StaffBase(BaseModel):
    name: str
    role: str
    phone: str
    shift: Optional[str] = None


class StaffCreate(StaffBase):
    pass


class StaffResponse(StaffBase):
    id: str = Field(alias="_id")
    status: str = "Active"

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Monthly Rent Schemas
# ──────────────────────────────────────────────

class MonthlyRentBase(BaseModel):
    month: str
    year: int
    amount: float
    status: str = "Paid"


class MonthlyRentCreate(MonthlyRentBase):
    pass


class MonthlyRentResponse(MonthlyRentBase):
    id: str = Field(alias="_id")
    house_id: Optional[str] = None
    house_number: Optional[str] = None
    payment_date: datetime

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# MOM Schemas
# ──────────────────────────────────────────────

class MOMBase(BaseModel):
    title: str
    content: str
    meeting_date: datetime


class MOMCreate(MOMBase):
    pass


class MOMResponse(MOMBase):
    id: str = Field(alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Amenity Schemas
# ──────────────────────────────────────────────

class AmenityBase(BaseModel):
    name: str
    description: str
    location: Optional[str] = None


class AmenityCreate(AmenityBase):
    pass


class AmenityResponse(AmenityBase):
    id: str = Field(alias="_id")
    is_available: bool = True

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Expense Schemas
# ──────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    expense_date: str # YYYY-MM-DD
    description: Optional[str] = None


class ExpenseResponse(ExpenseCreate):
    id: str = Field(alias="_id")
    created_by: str
    created_at: datetime

    class Config:
        populate_by_name = True


# ──────────────────────────────────────────────
# Other Income Schemas
# ──────────────────────────────────────────────

class IncomeCreate(BaseModel):
    title: str
    amount: float
    category: str
    income_date: str # YYYY-MM-DD
    description: Optional[str] = None


class IncomeResponse(IncomeCreate):
    id: str = Field(alias="_id")
    created_by: str
    created_at: datetime

    class Config:
        populate_by_name = True

