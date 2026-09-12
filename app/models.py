from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="resident", nullable=False)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(DateTime, default=datetime.utcnow)
    author_id = Column(String(255), nullable=True)


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="Pending", nullable=False)
    user_id = Column(String(255), nullable=True)
    date_submitted = Column(DateTime, default=datetime.utcnow)


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="Unpaid", nullable=False)


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    house_number = Column(String(50), unique=True, index=True, nullable=False)
    block = Column(String(50), nullable=False)
    owner_name = Column(String(255), nullable=False)
    family_members = Column(JSON, default=list)
    status = Column(String(50), default="Active", nullable=False)
    last_payment_date = Column(DateTime, nullable=True)
    last_payment_month = Column(String(100), default="No payments yet")


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    house_number = Column(String(50), nullable=False)
    purpose = Column(String(255), nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="Entered", nullable=False)


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    shift = Column(String(100), nullable=True)
    status = Column(String(50), default="Active", nullable=False)


class MonthlyRent(Base):
    __tablename__ = "monthly_rents"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(String(255), nullable=True)
    house_number = Column(String(50), nullable=True)
    month = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="Paid", nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)


class MOM(Base):
    __tablename__ = "moms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    meeting_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    expense_date = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(255), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    income_date = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(255), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)


class CommitteeMember(Base):
    __tablename__ = "committee_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    order = Column(Integer, default=99)
    published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class CMSPage(Base):
    __tablename__ = "cms_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)


class Slide(Base):
    __tablename__ = "slides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=False)
    link = Column(String(500), nullable=True)
    order = Column(Integer, default=0)
    active = Column(Boolean, default=True)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    category = Column(String(50), default="general")
    published = Column(Boolean, default=True)
    date = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    category = Column(String(50), default="general")
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

