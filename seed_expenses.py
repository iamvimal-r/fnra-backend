import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, SessionLocal, Base
from app import models

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed_expenses():
    db = SessionLocal()
    try:
        mock_expenses = [
            {
                "title": "Water Pump Repair",
                "amount": 2500.0,
                "category": "Maintenance",
                "expense_date": "2026-05-10",
                "description": "Replaced the main capacitor and impeller seals.",
                "created_by": "system",
            },
            {
                "title": "Common Area Electricity Bill",
                "amount": 4800.0,
                "category": "Utilities",
                "expense_date": "2026-05-12",
                "description": "Electricity charges for block A & B streetlights and gates.",
                "created_by": "system",
            },
            {
                "title": "Security Guards Wages",
                "amount": 24000.0,
                "category": "Salary",
                "expense_date": "2026-05-15",
                "description": "Monthly salaries for security staff (2 guards).",
                "created_by": "system",
            },
            {
                "title": "Falcon Sports Tournament",
                "amount": 15000.0,
                "category": "Events",
                "expense_date": "2026-05-18",
                "description": "Falcon Nagar community cricket event prizes and catering.",
                "created_by": "system",
            },
            {
                "title": "Gate Office Stationery",
                "amount": 750.0,
                "category": "Other",
                "expense_date": "2026-05-20",
                "description": "Registers, pens, receipt books and stamp pads for the gate counter.",
                "created_by": "system",
            }
        ]

        count = 0
        for exp in mock_expenses:
            existing = db.query(models.Expense).filter(models.Expense.title == exp["title"]).first()
            if not existing:
                new_exp = models.Expense(
                    title=exp["title"],
                    amount=exp["amount"],
                    category=exp["category"],
                    expense_date=exp["expense_date"],
                    description=exp["description"],
                    created_by=exp["created_by"],
                    created_at=datetime.utcnow()
                )
                db.add(new_exp)
                count += 1
        
        db.commit()
        print(f"Successfully seeded {count} mock expenses into MySQL fnra_db!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_expenses()
