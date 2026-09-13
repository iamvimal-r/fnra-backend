import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.database import engine, SessionLocal, Base
from app import models

HOUSES_DATA = [
    {"house_number": "102", "block": "Block C", "owner_name": "Anirudhan Vakeel (അനിരുദ്ധൻ വക്കീൽ)", "status": "Active"},
    {"house_number": "103", "block": "Block C", "owner_name": "Aneesh K.G (അനീഷ് K G)", "status": "Active"},
    {"house_number": "104", "block": "Block C", "owner_name": "Sagar (സാഗർ)", "status": "Active"},
    {"house_number": "105", "block": "Block C", "owner_name": "Shan (ഷാൻ)", "status": "Active"},
    {"house_number": "106", "block": "Block C", "owner_name": "Jayasree (ജയശ്രീ)", "status": "Active"},
    {"house_number": "107", "block": "Block C", "owner_name": "Raghunathan Nair (രഘുനാഥൻ നായർ)", "status": "Active"},
    {"house_number": "108", "block": "Block C", "owner_name": "Ramamruthan (രാമാമൃതൻ)", "status": "Active"},
    {"house_number": "109", "block": "Block C", "owner_name": "Raveendran Nair (രവീന്ദ്രൻ നായർ)", "status": "Active"},
    {"house_number": "110", "block": "Block C", "owner_name": "Rahul (രാഹുൽ)", "status": "Active"},
    {"house_number": "111", "block": "Block C", "owner_name": "Suni (സുനി)", "status": "Active"},
    {"house_number": "112", "block": "Block C", "owner_name": "Shaiju (ഷൈജു)", "status": "Active"},
    {"house_number": "113", "block": "Block C", "owner_name": "Shaini (ഷൈനി)", "status": "Active"},
    {"house_number": "114", "block": "Block C", "owner_name": "New Home", "status": "Active"},
    {"house_number": "115", "block": "Block C", "owner_name": "Mithun (മിഥുൻ)", "status": "Active"},
    {"house_number": "116", "block": "Block C", "owner_name": "Viju (വിജു)", "status": "Active"},
    {"house_number": "117", "block": "Block C", "owner_name": "Rupesh - Chapathi Company (രൂപേഷ് ചപ്പാത്തി കമ്പനി)", "status": "Active"},
    {"house_number": "118", "block": "Block C", "owner_name": "Shivaraj (ശിവരാജ്)", "status": "Active"},
    {"house_number": "119", "block": "Block C", "owner_name": "Subhagan (സുഭഗൻ)", "status": "Active"},
    {"house_number": "120", "block": "Block C", "owner_name": "Saritha (സരിത)", "status": "Active"},
    {"house_number": "121", "block": "Block C", "owner_name": "Lalithamma (ലളിതമ്മ)", "status": "Active"},
    {"house_number": "122", "block": "Block C", "owner_name": "Gopakrishnan (ഗോപികൃഷ്ണൻ)", "status": "Active"},
    {"house_number": "123", "block": "Block B", "owner_name": "Vimal (വിമൽ)", "status": "Active"},
    {"house_number": "124", "block": "Block C", "owner_name": "Madhusoodhanan (മധുസൂദനൻ)", "status": "Active"},
    {"house_number": "125", "block": "Block C", "owner_name": "Sarada Amma (ശാരദ അമ്മ)", "status": "Active"},
]

def seed_houses():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print(f"🌱 Seeding {len(HOUSES_DATA)} Houses into MySQL...")
        count_added = 0
        count_updated = 0

        for item in HOUSES_DATA:
            existing = db.query(models.House).filter(models.House.house_number == item["house_number"]).first()
            if existing:
                existing.owner_name = item["owner_name"]
                existing.block = item["block"]
                count_updated += 1
            else:
                house = models.House(
                    house_number=item["house_number"],
                    block=item["block"],
                    owner_name=item["owner_name"],
                    family_members=[],
                    status="Active"
                )
                db.add(house)
                count_added += 1

        db.commit()
        print(f"✅ Houses seeding complete! Added: {count_added}, Updated: {count_updated}, Total: {len(HOUSES_DATA)}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding houses: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_houses()
