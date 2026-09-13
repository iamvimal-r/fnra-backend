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
    {"house_number": "125", "block": "Block C", "owner_name": "Jyothi (ജ്യോതി)", "status": "Active"},
    {"house_number": "126", "block": "Block C", "owner_name": "Vinila (വിനില)", "status": "Active"},
    {"house_number": "127", "block": "Block C", "owner_name": "Thulasi (തുളസി)", "status": "Active"},
    {"house_number": "128", "block": "Block C", "owner_name": "Thankamani (തങ്കമണി)", "status": "Active"},
    {"house_number": "129", "block": "Block C", "owner_name": "Shobha (ശോഭ)", "status": "Active"},
    {"house_number": "130", "block": "Block C", "owner_name": "Nandakumar (നന്ദകുമാർ)", "status": "Active"},
    {"house_number": "131", "block": "Block C", "owner_name": "Bijosh (ബിജോഷ്)", "status": "Active"},
    {"house_number": "132", "block": "Block C", "owner_name": "Reshma (രേഷ്മ)", "status": "Active"},
    {"house_number": "133", "block": "Block C", "owner_name": "Nithin (നിധിൻ)", "status": "Active"},
    {"house_number": "134", "block": "Block C", "owner_name": "Gopakrishnan (ഗോപികൃഷ്ണൻ)", "status": "Active"},
    {"house_number": "135", "block": "Block C", "owner_name": "Balu (ബാലു)", "status": "Active"},
    {"house_number": "136", "block": "Block C", "owner_name": "KSRTC Wing (KSRTC വിങ്)", "status": "Active"},
    {"house_number": "137", "block": "Block C", "owner_name": "Shiju (ഷിജു)", "status": "Active"},
    {"house_number": "138", "block": "Block C", "owner_name": "Vikraman (വിക്രമൻ)", "status": "Active"},
    {"house_number": "139", "block": "Block C", "owner_name": "Shiny (ഷൈനി)", "status": "Active"},
    {"house_number": "140", "block": "Block C", "owner_name": "Rented House (വാടക വീട്)", "status": "Active"},
    {"house_number": "141", "block": "Block C", "owner_name": "Leelamma (ലീലമ്മ)", "status": "Active"},
    {"house_number": "142", "block": "Block C", "owner_name": "Kumar (കുമാർ)", "status": "Active"},
    {"house_number": "143", "block": "Block C", "owner_name": "Shiju (ഷിജു)", "status": "Active"},
    {"house_number": "144", "block": "Block C", "owner_name": "Sheeba (ഷീബ)", "status": "Active"},
    {"house_number": "145", "block": "Block C", "owner_name": "Shashi Home (ശശി)", "status": "NC"},
    {"house_number": "146", "block": "Block C", "owner_name": "Sheeja (ഷീജ)", "status": "NC"},
    {"house_number": "147", "block": "Block C", "owner_name": "Anil A Veedu (അനിൽ A വീട്)", "status": "Active"},
    {"house_number": "148", "block": "Block C", "owner_name": "Madhu Auto (മധു ഓട്ടോ)", "status": "NC"},
    {"house_number": "149", "block": "Block C", "owner_name": "Unni Kottaram (ഉണ്ണി കൊട്ടാരം)", "status": "Active"},
    {"house_number": "150", "block": "Block C", "owner_name": "CRP", "status": "Active"},
    {"house_number": "151", "block": "Block C", "owner_name": "Anita Veedu (അനിത വീട്)", "status": "Active"},
    {"house_number": "152", "block": "Block C", "owner_name": "Kamalamma (കമലമ്മ)", "status": "NC"},
    {"house_number": "153", "block": "Block C", "owner_name": "Binu (ബിനു)", "status": "Active"},
    {"house_number": "154", "block": "Block C", "owner_name": "Rakesh (രാകേഷ്)", "status": "Active"},
    {"house_number": "155", "block": "Block C", "owner_name": "Unni (ഉണ്ണി)", "status": "Active"},
    {"house_number": "156", "block": "Block C", "owner_name": "Shamnad (ഷംനാദ്)", "status": "Active"},
    {"house_number": "157", "block": "Block C", "owner_name": "Akhil (അഖിൽ)", "status": "Active"},
    {"house_number": "158", "block": "Block C", "owner_name": "Sujitha (സുജിത്ത)", "status": "Active"},
    {"house_number": "159", "block": "Block C", "owner_name": "Vasudevan Nair (വാസുദേവൻ നായർ)", "status": "Active"},
    {"house_number": "160", "block": "Block C", "owner_name": "Soumi (സൗമി)", "status": "Active"},
    {"house_number": "161", "block": "Block C", "owner_name": "Kuttan (കുട്ടൻ)", "status": "Active"},
    {"house_number": "162", "block": "Block C", "owner_name": "Vishakh (വിശാഖ്)", "status": "Active"},
    {"house_number": "163", "block": "Block C", "owner_name": "Shyama Veedu (ശ്യാമ വീട്)", "status": "Active"},
    {"house_number": "164", "block": "Block C", "owner_name": "Sudheesh Veedu (സുധീഷ് വീട്)", "status": "Active"},
    {"house_number": "165", "block": "Block C", "owner_name": "Omana Side (ഓമന side)", "status": "Active"},
    {"house_number": "166", "block": "Block C", "owner_name": "Kunnumpuram (കുന്നുമ്പുറം)", "status": "Active"},
    {"house_number": "167", "block": "Block C", "owner_name": "Deepa (ദീപ)", "status": "Active"},
    {"house_number": "168", "block": "Block C", "owner_name": "Anita Auto Driver (അനിത ഓട്ടോ ഡ്രൈവർ)", "status": "Active"},
    {"house_number": "169", "block": "Block C", "owner_name": "Anita (അനിത)", "status": "Active"},
    {"house_number": "170", "block": "Block C", "owner_name": "Anita Opp (അനിത Opp)", "status": "Active"},
]

def seed_houses():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("🌱 Seeding Houses data (102-170) into MySQL...")
        count_added = 0
        count_updated = 0

        for item in HOUSES_DATA:
            existing = db.query(models.House).filter(models.House.house_number == item["house_number"]).first()
            if existing:
                existing.owner_name = item["owner_name"]
                existing.block = item["block"]
                existing.status = item.get("status", "Active")
                count_updated += 1
            else:
                house = models.House(
                    house_number=item["house_number"],
                    block=item["block"],
                    owner_name=item["owner_name"],
                    family_members=[],
                    status=item.get("status", "Active")
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
