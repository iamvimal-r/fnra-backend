import os
from datetime import datetime
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, SessionLocal, Base
from app import models

# Ensure tables exist
Base.metadata.create_all(bind=engine)

ATLAS_URL = "mongodb+srv://vimalfalcon123_db_user:0eYaej9Ur8jn5ZIH@cluster0.xyyi11z.mongodb.net/residance_db?retryWrites=true&w=majority"

def parse_datetime(val):
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.utcnow()

def migrate():
    print("Connecting to MongoDB Atlas...")
    mongo_client = pymongo.MongoClient(ATLAS_URL, tlsCAFile=certifi.where())
    mongo_db = mongo_client.get_default_database()

    db = SessionLocal()
    try:
        # 1. Users
        mongo_users = list(mongo_db.users.find())
        print(f"Migrating {len(mongo_users)} users...")
        mongo_user_id_map = {}
        for u in mongo_users:
            m_id = str(u["_id"])
            existing = db.query(models.User).filter(models.User.email == u["email"]).first()
            if not existing:
                user = models.User(
                    name=u.get("name", ""),
                    username=u.get("username", u.get("name", "")),
                    email=u.get("email", ""),
                    hashed_password=u.get("hashed_password", ""),
                    role=u.get("role", "resident"),
                    profile_image=u.get("profile_image"),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                mongo_user_id_map[m_id] = str(user.id)
            else:
                mongo_user_id_map[m_id] = str(existing.id)

        # 2. Houses
        mongo_houses = list(mongo_db.houses.find())
        print(f"Migrating {len(mongo_houses)} houses...")
        mongo_house_id_map = {}
        for h in mongo_houses:
            m_id = str(h["_id"])
            h_num = h.get("house_number", "")
            existing = db.query(models.House).filter(models.House.house_number == h_num).first()
            if not existing:
                house = models.House(
                    house_number=h_num,
                    block=h.get("block", ""),
                    owner_name=h.get("owner_name", ""),
                    family_members=h.get("family_members", []),
                    status=h.get("status", "Active"),
                )
                db.add(house)
                db.commit()
                db.refresh(house)
                mongo_house_id_map[m_id] = str(house.id)
            else:
                mongo_house_id_map[m_id] = str(existing.id)

        # 3. Monthly Rents
        mongo_rents = list(mongo_db.rents.find())
        print(f"Migrating {len(mongo_rents)} rents...")
        for r in mongo_rents:
            old_h_id = str(r.get("house_id", ""))
            new_h_id = mongo_house_id_map.get(old_h_id, old_h_id)
            
            # Check duplicate by house_id, month, year
            existing = db.query(models.MonthlyRent).filter(
                models.MonthlyRent.house_id == new_h_id,
                models.MonthlyRent.month == r.get("month"),
                models.MonthlyRent.year == int(r.get("year", 2026))
            ).first()

            if not existing:
                rent = models.MonthlyRent(
                    house_id=new_h_id,
                    house_number=r.get("house_number", ""),
                    month=r.get("month", ""),
                    year=int(r.get("year", 2026)),
                    amount=float(r.get("amount", 0.0)),
                    status=r.get("status", "Paid"),
                    payment_date=parse_datetime(r.get("payment_date")),
                )
                db.add(rent)
        db.commit()

        # 4. Notices
        mongo_notices = list(mongo_db.notices.find())
        print(f"Migrating {len(mongo_notices)} notices...")
        for n in mongo_notices:
            existing = db.query(models.Notice).filter(models.Notice.title == n.get("title")).first()
            if not existing:
                notice = models.Notice(
                    title=n.get("title", ""),
                    content=n.get("content", ""),
                    date_posted=parse_datetime(n.get("date_posted")),
                    author_id=mongo_user_id_map.get(str(n.get("author_id")), str(n.get("author_id", ""))),
                )
                db.add(notice)
        db.commit()

        # 5. Complaints
        mongo_complaints = list(mongo_db.complaints.find())
        print(f"Migrating {len(mongo_complaints)} complaints...")
        for c in mongo_complaints:
            existing = db.query(models.Complaint).filter(models.Complaint.title == c.get("title")).first()
            if not existing:
                complaint = models.Complaint(
                    title=c.get("title", ""),
                    description=c.get("description", ""),
                    status=c.get("status", "Open"),
                    user_id=mongo_user_id_map.get(str(c.get("user_id")), str(c.get("user_id", ""))),
                    date_submitted=parse_datetime(c.get("date_submitted")),
                )
                db.add(complaint)
        db.commit()

        # 6. Bills
        mongo_bills = list(mongo_db.billing.find())
        print(f"Migrating {len(mongo_bills)} bills...")
        for b in mongo_bills:
            existing = db.query(models.Bill).filter(
                models.Bill.description == b.get("description"),
                models.Bill.amount == float(b.get("amount", 0.0))
            ).first()
            if not existing:
                bill = models.Bill(
                    user_id=mongo_user_id_map.get(str(b.get("user_id")), str(b.get("user_id", ""))),
                    amount=float(b.get("amount", 0.0)),
                    description=b.get("description", ""),
                    due_date=parse_datetime(b.get("due_date")),
                    status=b.get("status", "Pending"),
                )
                db.add(bill)
        db.commit()

        # 7. Visitors
        mongo_visitors = list(mongo_db.visitors.find())
        print(f"Migrating {len(mongo_visitors)} visitors...")
        for v in mongo_visitors:
            existing = db.query(models.Visitor).filter(
                models.Visitor.name == v.get("name"),
                models.Visitor.house_number == v.get("house_number")
            ).first()
            if not existing:
                visitor = models.Visitor(
                    name=v.get("name", ""),
                    phone=v.get("phone", ""),
                    house_number=v.get("house_number", ""),
                    purpose=v.get("purpose", ""),
                    entry_time=parse_datetime(v.get("entry_time")),
                    exit_time=parse_datetime(v.get("exit_time")) if v.get("exit_time") else None,
                    status=v.get("status", "Entered"),
                )
                db.add(visitor)
        db.commit()

        # 8. Staff
        mongo_staff = list(mongo_db.staff.find())
        print(f"Migrating {len(mongo_staff)} staff members...")
        for s in mongo_staff:
            existing = db.query(models.Staff).filter(models.Staff.name == s.get("name")).first()
            if not existing:
                staff = models.Staff(
                    name=s.get("name", ""),
                    role=s.get("role", ""),
                    phone=s.get("phone", ""),
                    shift=s.get("shift", ""),
                    status=s.get("status", "Active"),
                )
                db.add(staff)
        db.commit()

        # 9. MOM
        mongo_moms = list(mongo_db.mom.find())
        print(f"Migrating {len(mongo_moms)} MOM records...")
        for m in mongo_moms:
            existing = db.query(models.MOM).filter(models.MOM.title == m.get("title")).first()
            if not existing:
                mom = models.MOM(
                    title=m.get("title", ""),
                    content=m.get("content", ""),
                    meeting_date=parse_datetime(m.get("meeting_date")),
                    created_at=parse_datetime(m.get("created_at")),
                )
                db.add(mom)
        db.commit()

        # 10. Amenities
        mongo_amenities = list(mongo_db.amenities.find())
        print(f"Migrating {len(mongo_amenities)} amenities...")
        for a in mongo_amenities:
            existing = db.query(models.Amenity).filter(models.Amenity.name == a.get("name")).first()
            if not existing:
                amenity = models.Amenity(
                    name=a.get("name", ""),
                    description=a.get("description", ""),
                    location=a.get("location", ""),
                    is_available=a.get("is_available", True),
                )
                db.add(amenity)
        db.commit()

        # 11. Expenses
        mongo_expenses = list(mongo_db.expenses.find())
        print(f"Migrating {len(mongo_expenses)} expenses...")
        for e in mongo_expenses:
            existing = db.query(models.Expense).filter(models.Expense.title == e.get("title")).first()
            if not existing:
                expense = models.Expense(
                    title=e.get("title", ""),
                    amount=float(e.get("amount", 0.0)),
                    category=e.get("category", "General"),
                    expense_date=str(e.get("expense_date", "")),
                    description=e.get("description", ""),
                    created_by=str(e.get("created_by", "system")),
                    created_at=parse_datetime(e.get("created_at")),
                )
                db.add(expense)
        db.commit()

        # 12. Incomes
        mongo_incomes = list(mongo_db.incomes.find())
        print(f"Migrating {len(mongo_incomes)} incomes...")
        for i in mongo_incomes:
            existing = db.query(models.Income).filter(models.Income.title == i.get("title")).first()
            if not existing:
                income = models.Income(
                    title=i.get("title", ""),
                    amount=float(i.get("amount", 0.0)),
                    category=i.get("category", "General"),
                    income_date=str(i.get("income_date", "")),
                    description=i.get("description", ""),
                    created_by=str(i.get("created_by", "system")),
                    created_at=parse_datetime(i.get("created_at")),
                )
                db.add(income)
        db.commit()

        # 13. Committee Members
        mongo_committee = list(mongo_db.committee.find())
        print(f"Migrating {len(mongo_committee)} committee members...")
        for cm in mongo_committee:
            existing = db.query(models.CommitteeMember).filter(models.CommitteeMember.name == cm.get("name")).first()
            if not existing:
                member = models.CommitteeMember(
                    name=cm.get("name", ""),
                    designation=cm.get("role", cm.get("designation", "")),
                    phone=cm.get("phone", ""),
                    email=cm.get("email", ""),
                    photo_url=cm.get("photo_url", ""),
                    bio=cm.get("bio", ""),
                    order=int(cm.get("order", 99)),
                    published=bool(cm.get("published", True)),
                    created_at=parse_datetime(cm.get("created_at")),
                )
                db.add(member)
        db.commit()

        # 14. Contacts
        mongo_contacts = list(mongo_db.contacts.find())
        print(f"Migrating {len(mongo_contacts)} contacts...")
        for ct in mongo_contacts:
            existing = db.query(models.Contact).filter(models.Contact.name == ct.get("name")).first()
            if not existing:
                contact = models.Contact(
                    category=ct.get("category", ""),
                    name=ct.get("name", ""),
                    phone=ct.get("phone", ""),
                    email=ct.get("email", ""),
                    description=ct.get("notes", ct.get("description", "")),
                )
                db.add(contact)
        db.commit()

        # 15. Slides
        mongo_slides = list(mongo_db.slides.find())
        print(f"Migrating {len(mongo_slides)} slides...")
        for sl in mongo_slides:
            existing = db.query(models.Slide).filter(models.Slide.title == sl.get("title")).first()
            if not existing:
                slide = models.Slide(
                    title=sl.get("title", ""),
                    subtitle=sl.get("subtitle", ""),
                    image_url=sl.get("image_url", ""),
                    link=sl.get("link", ""),
                    order=int(sl.get("order", 0)),
                    active=bool(sl.get("active", True)),
                )
                db.add(slide)
        db.commit()

        # 16. News
        mongo_news = list(mongo_db.news.find())
        print(f"Migrating {len(mongo_news)} news items...")
        for nw in mongo_news:
            existing = db.query(models.News).filter(models.News.title == nw.get("title")).first()
            if not existing:
                news = models.News(
                    title=nw.get("title", ""),
                    content=nw.get("content", ""),
                    image_url=nw.get("image_url", ""),
                    category=nw.get("category", "general"),
                    published=bool(nw.get("published", True)),
                    date=nw.get("date", ""),
                    created_at=parse_datetime(nw.get("created_at")),
                )
                db.add(news)
        db.commit()

        # 17. Gallery
        mongo_gallery = list(mongo_db.gallery.find())
        print(f"Migrating {len(mongo_gallery)} gallery items...")
        for gl in mongo_gallery:
            existing = db.query(models.Gallery).filter(models.Gallery.title == gl.get("title")).first()
            if not existing:
                gallery = models.Gallery(
                    title=gl.get("title", ""),
                    image_url=gl.get("image_url", ""),
                    category=gl.get("category", "general"),
                    order=int(gl.get("order", 0)),
                    created_at=parse_datetime(gl.get("created_at")),
                )
                db.add(gallery)
        db.commit()

        print("🎉 Migration completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
