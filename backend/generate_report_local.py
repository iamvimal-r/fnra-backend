import os
import sys
import argparse
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from fpdf import FPDF

def main():
    parser = argparse.ArgumentParser(description="Generate Monthly Payment & Member Details PDF Report.")
    parser.add_argument("--year", type=int, default=2026, help="The year for the report (default: 2026)")
    parser.add_argument("--outdir", type=str, default=None, help="Output directory path (defaults to backend/reports)")
    args = parser.parse_args()

    # Load env variables from current directory (.env)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}. Trying system environment variables.")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment or .env file.")
        sys.exit(1)

    print(f"Connecting to database...")
    client = MongoClient(database_url)
    try:
        db = client.get_default_database()
    except Exception:
        db = client["residance_db"]

    year = args.year
    outdir = args.outdir or os.path.join(base_dir, "pdf")

    # Create output directory
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(outdir, f"monthly_report_{year}.pdf"))

    print(f"Fetching data for year {year}...")
    houses = list(db.houses.find())
    rents = list(db.rents.find({"year": year}))

    # Map rents by house_id
    rents_by_house = {}
    for r in rents:
        h_id = str(r.get("house_id", ""))
        if not h_id:
            continue
        if h_id not in rents_by_house:
            rents_by_house[h_id] = []
        rents_by_house[h_id].append({
            "month": r.get("month", ""),
            "amount": r.get("amount", 0),
            "status": r.get("status", "Pending")
        })

    report_data = []
    for h in houses:
        h_id = str(h["_id"])
        h_rents = rents_by_house.get(h_id, [])
        months_dict = {}
        for hr in h_rents:
            months_dict[hr["month"]] = {
                "amount": hr["amount"],
                "status": hr["status"]
            }

        report_data.append({
            "house_number": h.get("house_number", ""),
            "block": h.get("block", ""),
            "owner_name": h.get("owner_name", ""),
            "status": h.get("status", "Active"),
            "months": months_dict,
            "family_members": h.get("family_members", [])
        })

    # Sort by house number
    report_data.sort(key=lambda x: x["house_number"])

    # Calculate statistics
    total_paid = 0
    total_pending = 0
    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    for item in report_data:
        house_paid = 0
        house_pending = 0
        for m in months_list:
            m_data = item["months"].get(m)
            if m_data:
                if m_data["status"] == "Paid":
                    house_paid += m_data["amount"]
                else:
                    house_pending += m_data["amount"]
            else:
                house_pending += 50
        item["paid_amount"] = house_paid
        item["pending_amount"] = house_pending
        total_paid += house_paid
        total_pending += house_pending

    print(f"Generating PDF report...")
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)

    # Title Banner
    pdf.cell(0, 10, "FALCON NAGAR RESIDENTS ASSOCIATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Reg No: TVM/TC/1496/2015", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Registered Houses Directory / List - Year {year}", ln=True, align="C")
    pdf.ln(5)

    # Statistics Box
    rate = round((total_paid / (total_paid + total_pending)) * 100) if (total_paid + total_pending) > 0 else 0
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 277, 12, style="F")
    pdf.set_font("Helvetica", "", 9)
    stats_text = f"Total Registered Houses: {len(report_data)} | Total Paid: Rs. {total_paid} | Total Pending: Rs. {total_pending} | Collection Rate: {rate}%"
    pdf.cell(0, 12, stats_text, align="C")
    pdf.ln(15)

    # Table Header
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(26, 22, 37) # Dark Navy background (#1a1625)
    pdf.set_text_color(255, 255, 255)

    pdf.cell(10, 8, "Sl", border=1, align="C", fill=True)
    pdf.cell(20, 8, "House", border=1, align="C", fill=True)
    pdf.cell(25, 8, "Block", border=1, align="C", fill=True)
    pdf.cell(82, 8, "Owner & Family Details", border=1, align="C", fill=True)

    # Months columns
    pdf.set_font("Helvetica", "B", 7.5)
    month_shorthands = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m_short in month_shorthands:
        pdf.cell(9, 8, m_short, border=1, align="C", fill=True)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(16, 8, "Paid", border=1, align="C", fill=True)
    pdf.cell(16, 8, "Pending", border=1, align="C", fill=True)
    pdf.ln()

    # Table Body
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)

    for idx, item in enumerate(report_data):
        # Alternating row colors
        if idx % 2 == 1:
            pdf.set_fill_color(248, 250, 252) # Light blue-gray row background
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(10, 8, str(idx + 1), border=1, align="C", fill=True)

        h_num = item["house_number"].encode("latin-1", "replace").decode("latin-1")
        block_name = item["block"].encode("latin-1", "replace").decode("latin-1")
        pdf.cell(20, 8, h_num, border=1, align="C", fill=True)
        pdf.cell(25, 8, block_name, border=1, align="C", fill=True)

        owner = item["owner_name"] or "N/A"
        family = item.get("family_members", [])
        if family:
            family_names = ", ".join([f["name"] for f in family])
            details = f"{owner} ({family_names})"
        else:
            details = owner

        details = details.encode("latin-1", "replace").decode("latin-1")
        if len(details) > 42:
            details = details[:39] + "..."
        pdf.cell(82, 8, details, border=1, align="L", fill=True)

        # Months columns
        pdf.set_font("Helvetica", "B", 7.5)
        for m in months_list:
            m_data = item["months"].get(m)
            if m_data and m_data["status"] == "Paid":
                pdf.set_text_color(22, 163, 74) # green
                m_str = "P"
            else:
                pdf.set_text_color(220, 38, 38) # red
                m_str = "-"
            pdf.cell(9, 8, m_str, border=1, align="C", fill=True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(16, 8, f"Rs. {item['paid_amount']}", border=1, align="C", fill=True)
        pdf.cell(16, 8, f"Rs. {item['pending_amount']}", border=1, align="C", fill=True)
        pdf.ln()

    # Footer
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(100, 10, "* Legend: P = Paid | - = Pending", align="L")

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    current_date = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
    pdf.cell(0, 10, f"Report Generated on {current_date} | FNRA Resident Management System", align="R")

    # Output to local file
    pdf.output(out_path)
    print(f"\nSuccess! PDF Report saved locally at:\n{out_path}\n")

if __name__ == "__main__":
    main()
