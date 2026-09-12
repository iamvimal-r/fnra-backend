import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, SessionLocal, Base
from app import models, auth

# Create tables if not exist
Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    db_name = engine.url.database or "database"
    try:
        print(f"🌱 Seeding MySQL Database ({db_name})...")

        # 1. Users
        if db.query(models.User).count() == 0:
            print("  Seeding Users...")
            admin_user = models.User(
                name="FNRA Admin",
                username="admin",
                email="admin@fnra.org",
                hashed_password=auth.get_password_hash("AdminPassword123"),
                role="admin",
                profile_image=None,
            )
            resident_user = models.User(
                name="John Resident",
                username="john_res",
                email="john@fnra.org",
                hashed_password=auth.get_password_hash("UserPassword123"),
                role="resident",
                profile_image=None,
            )
            security_user = models.User(
                name="Gate Security",
                username="security",
                email="security@fnra.org",
                hashed_password=auth.get_password_hash("Security123"),
                role="security",
                profile_image=None,
            )
            db.add_all([admin_user, resident_user, security_user])
            db.commit()

        # 2. Houses
        if db.query(models.House).count() == 0:
            print("  Seeding Houses...")
            mock_houses = []
            for block in ["Block A", "Block B", "Block C", "Block D"]:
                for num in range(101, 106):
                    h_num = f"{block[-1]}-{num}"
                    mock_houses.append(
                        models.House(
                            house_number=h_num,
                            block=block,
                            owner_name=f"Resident {h_num}",
                            family_members=[
                                {"name": f"Family Member 1 ({h_num})", "relation": "Spouse"},
                                {"name": f"Family Member 2 ({h_num})", "relation": "Child"}
                            ],
                            status="Active"
                        )
                    )
            db.add_all(mock_houses)
            db.commit()

        # 3. Committee Members
        if db.query(models.CommitteeMember).count() == 0:
            print("  Seeding Committee Members...")
            members = [
                models.CommitteeMember(
                    name="K. Ramanathan",
                    designation="President",
                    phone="9847012345",
                    email="president@fnra.org",
                    photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300",
                    bio="Serving FNRA resident community for over 10 years.",
                    order=1,
                    published=True
                ),
                models.CommitteeMember(
                    name="S. Anita Nair",
                    designation="Secretary",
                    phone="9847054321",
                    email="secretary@fnra.org",
                    photo_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300",
                    bio="Managing society operations, communications and welfare activities.",
                    order=2,
                    published=True
                ),
                models.CommitteeMember(
                    name="M. Vijayakumar",
                    designation="Treasurer",
                    phone="9847098765",
                    email="treasurer@fnra.org",
                    photo_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300",
                    bio="Overseeing association finances, budgeting, and monthly fee collections.",
                    order=3,
                    published=True
                ),
            ]
            db.add_all(members)
            db.commit()

        # 4. Expenses
        if db.query(models.Expense).count() == 0:
            print("  Seeding Expenses...")
            expenses = [
                models.Expense(
                    title="Water Pump Repair",
                    amount=2500.0,
                    category="Maintenance",
                    expense_date="2026-05-10",
                    description="Replaced main capacitor and impeller seals.",
                    created_by="system",
                    created_at=datetime.utcnow()
                ),
                models.Expense(
                    title="Common Area Electricity Bill",
                    amount=4800.0,
                    category="Utilities",
                    expense_date="2026-05-12",
                    description="Electricity charges for streetlights and gate lighting.",
                    created_by="system",
                    created_at=datetime.utcnow()
                ),
                models.Expense(
                    title="Security Guards Salary",
                    amount=24000.0,
                    category="Salary",
                    expense_date="2026-05-15",
                    description="Monthly salaries for 2 gate security officers.",
                    created_by="system",
                    created_at=datetime.utcnow()
                ),
            ]
            db.add_all(expenses)
            db.commit()

        # 5. Incomes
        if db.query(models.Income).count() == 0:
            print("  Seeding Incomes...")
            incomes = [
                models.Income(
                    title="Community Hall Rental",
                    amount=5000.0,
                    category="Rentals",
                    income_date="2026-05-05",
                    description="Rental charges for block C family gathering.",
                    created_by="system",
                    created_at=datetime.utcnow()
                ),
                models.Income(
                    title="Donation for Sports Day",
                    amount=10000.0,
                    category="Donations",
                    income_date="2026-05-12",
                    description="Special donation received from resident in Block A.",
                    created_by="system",
                    created_at=datetime.utcnow()
                ),
            ]
            db.add_all(incomes)
            db.commit()

        # 6. Notices
        if db.query(models.Notice).count() == 0:
            print("  Seeding Notices...")
            notices = [
                models.Notice(
                    title="Annual General Body Meeting 2026",
                    content="The AGM of FNRA will be held on Sunday at 10:00 AM in the Community Hall.",
                    date_posted=datetime.utcnow(),
                    author_id="1"
                ),
                models.Notice(
                    title="Water Tank Cleaning Schedule",
                    content="Overhead water tanks in Block A & B will be cleaned tomorrow between 9 AM and 1 PM.",
                    date_posted=datetime.utcnow() - timedelta(days=2),
                    author_id="1"
                ),
            ]
            db.add_all(notices)
            db.commit()

        # 7. Contacts
        if db.query(models.Contact).count() == 0:
            print("  Seeding Emergency Contacts...")
            contacts = [
                models.Contact(
                    category="emergency",
                    name="Local Police Station",
                    phone="0471-2345678",
                    description="Nearest Police Station Emergency Line"
                ),
                models.Contact(
                    category="plumber",
                    name="Kumar Plumber",
                    phone="9847111222",
                    description="Association On-Call Plumber"
                ),
                models.Contact(
                    category="electrician",
                    name="Suresh Electrician",
                    phone="9847333444",
                    description="Association On-Call Electrician"
                ),
            ]
            db.add_all(contacts)
            db.commit()

        # 8. Slides
        if db.query(models.Slide).count() == 0:
            print("  Seeding CMS Carousel Slides...")
            slides = [
                models.Slide(
                    title="Welcome to Falcon Nagar",
                    subtitle="A vibrant, secure, and green residential community.",
                    image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200",
                    order=1,
                    active=True
                ),
                models.Slide(
                    title="Modern Facilities & Amenities",
                    subtitle="Community hall, children's park, and 24/7 security.",
                    image_url="https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=1200",
                    order=2,
                    active=True
                )
            ]
            db.add_all(slides)
            db.commit()

        # 9. Amenities
        if db.query(models.Amenity).count() == 0:
            print("  Seeding Amenities...")
            amenities = [
                models.Amenity(
                    name="Community Hall",
                    description="Air-conditioned hall for family events, meetings, and gatherings.",
                    location="Block C Ground Floor",
                    is_available=True
                ),
                models.Amenity(
                    name="Children's Play Park",
                    description="Outdoor play area with swings, slides, and seating benches.",
                    location="Central Lawn",
                    is_available=True
                ),
            ]
            db.add_all(amenities)
            db.commit()

        print("✅ Database seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
