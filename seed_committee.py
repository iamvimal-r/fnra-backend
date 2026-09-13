import os
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.database import engine, SessionLocal, Base
from app import models

# 1. Ensure tables are created
Base.metadata.create_all(bind=engine)

POSTER_PATH = "/home/vimal/Downloads/WhatsApp Image 2026-09-13 at 11.13.18.jpeg"
OUTPUT_DIR = "static/committee"


def crop_photos():
    """Crop all 21 committee members from the photo poster if poster exists."""
    if not os.path.exists(POSTER_PATH):
        print(f"⚠️ Poster file not found at {POSTER_PATH}, skipping cropping.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img = Image.open(POSTER_PATH)

    crops = {
        "sushamadevi": (375, 308, 545, 465),
        "r_p_nandaraj": (165, 308, 335, 465),
        "aneesh": (575, 308, 745, 465),
        "nalini_teacher": (140, 545, 285, 665),
        "valsala": (290, 545, 435, 665),
        "biju": (440, 545, 585, 665),
        "vimal": (590, 545, 735, 665),
        "ajith": (32, 715, 125, 815),
        "achu_vijayan": (146, 715, 239, 815),
        "prem_nath": (260, 715, 353, 815),
        "gopakumar": (374, 715, 467, 815),
        "bijosh": (488, 715, 581, 815),
        "sujitha": (602, 715, 695, 815),
        "kumar": (716, 715, 809, 815),
        "geethu": (32, 855, 125, 955),
        "viji": (146, 855, 239, 955),
        "madhu": (260, 855, 353, 955),
        "madhu_mohan": (374, 855, 467, 955),
        "madhu_mohan_2": (488, 855, 581, 955),
        "sreeja": (602, 855, 695, 955),
        "reshma": (716, 855, 809, 955),
    }

    for name, box in crops.items():
        cropped = img.crop(box)
        cropped.save(os.path.join(OUTPUT_DIR, f"{name}.jpg"))

    print(f"✂️  Successfully cropped {len(crops)} photos into '{OUTPUT_DIR}/'")


COMMITTEE_MEMBERS = [
    {
        "name": "സുഷമാദേവി (Sushamadevi)",
        "designation": "President",
        "photo_url": "/static/committee/sushamadevi.jpg",
        "bio": "President, Falcon Nagar Residence Association",
        "order": 1,
    },
    {
        "name": "ആർ.പി. നന്ദരാജ് (R. P. Nandaraj)",
        "designation": "Secretary",
        "photo_url": "/static/committee/r_p_nandaraj.jpg",
        "bio": "Secretary, Falcon Nagar Residence Association",
        "order": 2,
    },
    {
        "name": "അനീഷ് (Aneesh)",
        "designation": "Treasurer",
        "photo_url": "/static/committee/aneesh.jpg",
        "bio": "Treasurer, Falcon Nagar Residence Association",
        "order": 3,
    },
    {
        "name": "നളിനി ടീച്ചർ (Nalini Teacher)",
        "designation": "Joint Secretary",
        "photo_url": "/static/committee/nalini_teacher.jpg",
        "bio": "Joint Secretary, Falcon Nagar Residence Association",
        "order": 4,
    },
    {
        "name": "വത്സല (Valsala)",
        "designation": "Vice President",
        "photo_url": "/static/committee/valsala.jpg",
        "bio": "Vice President, Falcon Nagar Residence Association",
        "order": 5,
    },
    {
        "name": "ബിജു (Biju)",
        "designation": "Vice President",
        "photo_url": "/static/committee/biju.jpg",
        "bio": "Vice President, Falcon Nagar Residence Association",
        "order": 6,
    },
    {
        "name": "വിമൽ (Vimal)",
        "designation": "Joint Secretary",
        "photo_url": "/static/committee/vimal.jpg",
        "bio": "Joint Secretary, Falcon Nagar Residence Association",
        "order": 7,
    },
    {
        "name": "അജിത്ത് (Ajith)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/ajith.jpg",
        "bio": "Executive Committee Member",
        "order": 8,
    },
    {
        "name": "അച്ചു വിജയൻ (Achu Vijayan)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/achu_vijayan.jpg",
        "bio": "Executive Committee Member",
        "order": 9,
    },
    {
        "name": "പ്രേം നാഥ് (Prem Nath)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/prem_nath.jpg",
        "bio": "Executive Committee Member",
        "order": 10,
    },
    {
        "name": "ഗോപകുമാർ (Gopakumar)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/gopakumar.jpg",
        "bio": "Executive Committee Member",
        "order": 11,
    },
    {
        "name": "ബിജോഷ് (Bijosh)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/bijosh.jpg",
        "bio": "Executive Committee Member",
        "order": 12,
    },
    {
        "name": "സുജിത്ത (Sujitha)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/sujitha.jpg",
        "bio": "Executive Committee Member",
        "order": 13,
    },
    {
        "name": "കുമാർ (Kumar)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/kumar.jpg",
        "bio": "Executive Committee Member",
        "order": 14,
    },
    {
        "name": "ഗീതു (Geethu)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/geethu.jpg",
        "bio": "Executive Committee Member",
        "order": 15,
    },
    {
        "name": "വിജി (Viji)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/viji.jpg",
        "bio": "Executive Committee Member",
        "order": 16,
    },
    {
        "name": "മധു (Madhu)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/madhu.jpg",
        "bio": "Executive Committee Member",
        "order": 17,
    },
    {
        "name": "മധു മോഹൻ (Madhu Mohan)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/madhu_mohan.jpg",
        "bio": "Executive Committee Member",
        "order": 18,
    },
    {
        "name": "കെ. മധു മോഹൻ (K. Madhu Mohan)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/madhu_mohan_2.jpg",
        "bio": "Executive Committee Member",
        "order": 19,
    },
    {
        "name": "ശ്രീജ (Sreeja)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/sreeja.jpg",
        "bio": "Executive Committee Member",
        "order": 20,
    },
    {
        "name": "രേഷ്മ (Reshma)",
        "designation": "Executive Member",
        "photo_url": "/static/committee/reshma.jpg",
        "bio": "Executive Committee Member",
        "order": 21,
    },
]


def seed_committee(clear_existing=True):
    crop_photos()
    db = SessionLocal()
    try:
        print("🌱 Seeding FNRA Committee Members based on official flyer photo...")
        if clear_existing:
            db.query(models.CommitteeMember).delete()
            db.commit()

        members = []
        for item in COMMITTEE_MEMBERS:
            m = models.CommitteeMember(
                name=item["name"],
                designation=item["designation"],
                photo_url=item["photo_url"],
                bio=item["bio"],
                order=item["order"],
                published=True,
            )
            members.append(m)

        db.add_all(members)
        db.commit()
        print(f"✅ Successfully seeded {len(members)} FNRA Committee Members into Database!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_committee()
