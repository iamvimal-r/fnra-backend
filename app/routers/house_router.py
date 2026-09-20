from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Annotated
from app import schemas, auth, database, models
from datetime import datetime
from fpdf import FPDF

router = APIRouter()

# ── Houses ────────────────────────────────────────────────────────────────────

@router.post("/houses", response_model=schemas.HouseResponse)
def register_house(
    house: schemas.HouseCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    existing = db.query(models.House).filter(models.House.house_number == house.house_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="House number already registered")

    new_house = models.House(
        house_number=house.house_number,
        house_name=getattr(house, "house_name", "") or "",
        block=house.block,
        owner_name=house.owner_name,
        family_members=[fm.dict() for fm in house.family_members],
        status=house.status or "Active",
    )
    db.add(new_house)
    db.commit()
    db.refresh(new_house)
    
    return {
        "_id": str(new_house.id),
        "house_number": new_house.house_number,
        "house_name": new_house.house_name or "",
        "block": new_house.block,
        "owner_name": new_house.owner_name,
        "family_members": new_house.family_members or [],
        "association_fee": 50.0,
        "status": new_house.status,
        "last_payment_date": None,
        "last_payment_month": "No payments yet",
    }


@router.get("/houses/public", response_model=list[schemas.HouseResponse])
def get_public_houses(
    db: Session = Depends(database.get_db),
):
    """Public endpoint for retrieving house directory listing (no auth required)."""
    houses = db.query(models.House).all()
    result = []
    for h in houses:
        result.append({
            "_id": str(h.id),
            "house_number": h.house_number,
            "house_name": getattr(h, "house_name", "") or "",
            "block": h.block,
            "owner_name": h.owner_name,
            "family_members": h.family_members or [],
            "association_fee": 50.0,
            "status": h.status,
            "last_payment_date": None,
            "last_payment_month": "No payments yet",
        })
    return result


@router.get("/houses", response_model=list[schemas.HouseResponse])
def get_all_houses(
    db: Session = Depends(database.get_db),
):
    houses = db.query(models.House).all()
    result = []
    for h in houses:
        last_payment = db.query(models.MonthlyRent).filter(models.MonthlyRent.house_id == str(h.id)).order_by(models.MonthlyRent.payment_date.desc()).first()
        if last_payment:
            l_date = last_payment.payment_date
            l_month = f"{last_payment.month} {last_payment.year}"
        else:
            l_date = None
            l_month = "No payments yet"

        result.append({
            "_id": str(h.id),
            "house_number": h.house_number,
            "house_name": getattr(h, "house_name", "") or "",
            "block": h.block,
            "owner_name": h.owner_name,
            "family_members": h.family_members or [],
            "association_fee": 50.0,
            "status": h.status,
            "last_payment_date": l_date,
            "last_payment_month": l_month,
        })
    return result


@router.put("/houses/{house_id}/fee")
def update_house_fee(
    house_id: str,
    fee_update: schemas.AssociationFeeUpdate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    return {"message": "Association fee updated successfully"}


@router.put("/houses/{house_id}/family")
def update_family_members(
    house_id: str,
    data: dict,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        hid = int(house_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="House not found")

    house = db.query(models.House).filter(models.House.id == hid).first()
    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    house.family_members = data.get("family_members", [])
    db.commit()
    return {"message": "Family members updated successfully"}


@router.put("/houses/{house_id}")
def update_house(
    house_id: str,
    house_data: schemas.HouseCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        hid = int(house_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="House not found")

    existing = db.query(models.House).filter(models.House.id == hid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="House not found")

    existing.house_number = house_data.house_number
    existing.house_name = getattr(house_data, "house_name", "") or ""
    existing.block = house_data.block
    existing.owner_name = house_data.owner_name
    if house_data.status:
        existing.status = house_data.status
    existing.family_members = [fm.dict() for fm in house_data.family_members]
    db.commit()
    return {"message": "House updated successfully"}


@router.delete("/houses/{house_id}")
def delete_house(
    house_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        hid = int(house_id)
    except ValueError:
        return {"message": "House deleted successfully"}

    house = db.query(models.House).filter(models.House.id == hid).first()
    if house:
        db.delete(house)
        db.commit()
    return {"message": "House deleted successfully"}


@router.get("/dashboard")
def get_dashboard(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    notices_count = db.query(models.Notice).count()
    if getattr(current_user, "role", None) == "admin":
        complaints_count = db.query(models.Complaint).filter(models.Complaint.status.in_(["Open", "In Progress"])).count()
    else:
        complaints_count = db.query(models.Complaint).filter(models.Complaint.user_id == str(current_user.id), models.Complaint.status.in_(["Open", "In Progress"])).count()
        
    return {
        "role": getattr(current_user, "role", "resident"),
        "message": f"Welcome, {getattr(current_user, 'name', 'User')}!",
        "stats": {
            "notices": notices_count,
            "complaints": complaints_count,
            "balance": 0
        }
    }


# ── Monthly Rent/Fee Payments ─────────────────────────────────────────────────

@router.get("/houses/rent/summary")
def get_rent_summary(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    rents = db.query(models.MonthlyRent).all()
    total = sum(r.amount or 0.0 for r in rents)
    paid = sum(r.amount or 0.0 for r in rents if r.status == "Paid")
    return {
        "total_amount": total,
        "paid_amount": paid,
        "pending_amount": total - paid
    }


@router.get("/houses/rent/tbk")
def get_monthly_rents_tbk(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    tbk_records = db.query(models.MonthlyRentTBK).order_by(models.MonthlyRentTBK.posted_date.desc()).limit(200).all()
    return [
        {
            "id": r.id,
            "rent_id": r.rent_id,
            "house_id": r.house_id,
            "house_number": r.house_number,
            "month": r.month,
            "year": r.year,
            "amount": r.amount,
            "status": r.status,
            "payment_date": r.payment_date,
            "operation": r.operation,
            "posted_by": r.posted_by,
            "posted_date": r.posted_date,
        }
        for r in tbk_records
    ]


@router.post("/houses/{house_id}/rent", response_model=schemas.MonthlyRentResponse)
def add_house_rent(
    house_id: str,
    rent: schemas.MonthlyRentCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        hid = int(house_id)
        house = db.query(models.House).filter(models.House.id == hid).first()
    except ValueError:
        house = None

    house_number = house.house_number if house else ""

    # Check if a rent record for this house_id, month, and year already exists
    existing_rent = db.query(models.MonthlyRent).filter(
        models.MonthlyRent.house_id == house_id,
        models.MonthlyRent.month == rent.month,
        models.MonthlyRent.year == rent.year
    ).first()

    if existing_rent:
        existing_rent.amount = rent.amount
        existing_rent.status = rent.status
        existing_rent.payment_date = datetime.utcnow()
        if house_number and not existing_rent.house_number:
            existing_rent.house_number = house_number
        db.commit()
        db.refresh(existing_rent)
        r = existing_rent
    else:
        r = models.MonthlyRent(
            house_id=house_id,
            house_number=house_number,
            month=rent.month,
            year=rent.year,
            amount=rent.amount,
            status=rent.status,
            payment_date=datetime.utcnow(),
        )
        db.add(r)
        db.commit()
        db.refresh(r)

    return {
        "_id": str(r.id),
        "house_id": r.house_id,
        "house_number": r.house_number,
        "month": r.month,
        "year": r.year,
        "amount": r.amount,
        "status": r.status,
        "payment_date": r.payment_date,
    }


@router.get("/houses/{house_id}/rent", response_model=list[schemas.MonthlyRentResponse])
def get_house_rent_history(
    house_id: str,
    db: Session = Depends(database.get_db),
):
    rents = db.query(models.MonthlyRent).filter(models.MonthlyRent.house_id == house_id).order_by(models.MonthlyRent.payment_date.desc()).all()

    try:
        hid = int(house_id)
        house = db.query(models.House).filter(models.House.id == hid).first()
    except ValueError:
        house = None

    house_number = house.house_number if house else ""

    return [
        {
            "_id": str(r.id),
            "house_id": r.house_id,
            "house_number": r.house_number or house_number,
            "month": r.month,
            "year": r.year,
            "amount": r.amount,
            "status": r.status,
            "payment_date": r.payment_date,
        }
        for r in rents
    ]


@router.put("/houses/rent/{rent_id}")
def update_house_rent(
    rent_id: str,
    rent: schemas.MonthlyRentCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        rid = int(rent_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Payment not found")

    r = db.query(models.MonthlyRent).filter(models.MonthlyRent.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Payment not found")

    r.month = rent.month
    r.year = rent.year
    r.amount = rent.amount
    r.status = rent.status
    db.commit()
    return {"message": "Payment updated"}


@router.delete("/houses/rent/{rent_id}")
def delete_house_rent(
    rent_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        rid = int(rent_id)
    except ValueError:
        return {"message": "Payment deleted"}

    r = db.query(models.MonthlyRent).filter(models.MonthlyRent.id == rid).first()
    if r:
        db.delete(r)
        db.commit()
    return {"message": "Payment deleted"}


@router.get("/houses/reports/monthly")
def get_monthly_report(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    year: int = 2026,
    db: Session = Depends(database.get_db),
):
    houses = db.query(models.House).all()
    rents = db.query(models.MonthlyRent).filter(models.MonthlyRent.year == year).all()
    
    rents_by_house = {}
    for r in rents:
        h_id = str(r.house_id or "")
        if not h_id:
            continue
        if h_id not in rents_by_house:
            rents_by_house[h_id] = []
        rents_by_house[h_id].append({
            "month": r.month or "",
            "amount": r.amount or 0,
            "status": r.status or "Pending"
        })
        
    report_data = []
    for h in houses:
        h_id = str(h.id)
        h_rents = rents_by_house.get(h_id, [])
        months_dict = {}
        for hr in h_rents:
            months_dict[hr["month"]] = {
                "amount": hr["amount"],
                "status": hr["status"]
            }
            
        report_data.append({
            "house_id": h_id,
            "house_number": h.house_number or "",
            "block": h.block or "",
            "owner_name": h.owner_name or "",
            "status": h.status or "Active",
            "association_fee": 50.0,
            "months": months_dict,
            "family_members": h.family_members or []
        })
        
    report_data.sort(key=lambda x: x["house_number"])
    return report_data


@router.get("/houses/list/pdf")
@router.get("/houses/reports/monthly/pdf")
def export_monthly_report_pdf(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    year: int = 2026,
    db: Session = Depends(database.get_db),
):
    houses = db.query(models.House).all()
    rents = db.query(models.MonthlyRent).filter(models.MonthlyRent.year == year).all()
    
    rents_by_house = {}
    for r in rents:
        h_id = str(r.house_id or "")
        if not h_id:
            continue
        if h_id not in rents_by_house:
            rents_by_house[h_id] = []
        rents_by_house[h_id].append({
            "month": r.month or "",
            "amount": r.amount or 0,
            "status": r.status or "Pending"
        })
        
    report_data = []
    for h in houses:
        h_id = str(h.id)
        h_rents = rents_by_house.get(h_id, [])
        months_dict = {}
        for hr in h_rents:
            months_dict[hr["month"]] = {
                "amount": hr["amount"],
                "status": hr["status"]
            }
            
        report_data.append({
            "house_number": h.house_number or "",
            "block": h.block or "",
            "owner_name": h.owner_name or "",
            "status": h.status or "Active",
            "months": months_dict,
            "family_members": h.family_members or []
        })
        
    report_data.sort(key=lambda x: x["house_number"])

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

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    pdf.cell(0, 10, "FALCON NAGAR RESIDENTS ASSOCIATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Reg No: TVM/TC/1496/2015", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Registered Houses Directory / List - Year {year}", ln=True, align="C")
    pdf.ln(5)

    rate = round((total_paid / (total_paid + total_pending)) * 100) if (total_paid + total_pending) > 0 else 0
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 277, 12, style="F")
    pdf.set_font("Helvetica", "", 9)
    stats_text = f"Total Registered Houses: {len(report_data)} | Total Paid: Rs. {total_paid} | Total Pending: Rs. {total_pending} | Collection Rate: {rate}%"
    pdf.cell(0, 12, stats_text, align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(26, 22, 37)
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(10, 8, "Sl", border=1, align="C", fill=True)
    pdf.cell(20, 8, "House", border=1, align="C", fill=True)
    pdf.cell(25, 8, "Block", border=1, align="C", fill=True)
    pdf.cell(82, 8, "Owner & Family Details", border=1, align="C", fill=True)
    
    pdf.set_font("Helvetica", "B", 7.5)
    month_shorthands = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m_short in month_shorthands:
        pdf.cell(9, 8, m_short, border=1, align="C", fill=True)
        
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(16, 8, "Paid", border=1, align="C", fill=True)
    pdf.cell(16, 8, "Pending", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    
    for idx, item in enumerate(report_data):
        if idx % 2 == 1:
            pdf.set_fill_color(248, 250, 252)
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
            family_names = ", ".join([f["name"] for f in family if isinstance(f, dict) and "name" in f])
            details = f"{owner} ({family_names})"
        else:
            details = owner
            
        details = details.encode("latin-1", "replace").decode("latin-1")
        if len(details) > 42:
            details = details[:39] + "..."
        pdf.cell(82, 8, details, border=1, align="L", fill=True)
        
        pdf.set_font("Helvetica", "B", 7.5)
        for m in months_list:
            m_data = item["months"].get(m)
            if m_data and m_data["status"] == "Paid":
                pdf.set_text_color(22, 163, 74)
                m_str = "P"
            else:
                pdf.set_text_color(220, 38, 38)
                m_str = "-"
            pdf.cell(9, 8, m_str, border=1, align="C", fill=True)
            
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(16, 8, f"Rs. {item['paid_amount']}", border=1, align="C", fill=True)
        pdf.cell(16, 8, f"Rs. {item['pending_amount']}", border=1, align="C", fill=True)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(100, 10, "* Legend: P = Paid | - = Pending", align="L")
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    current_date = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
    pdf.cell(0, 10, f"Report Generated on {current_date} | FNRA Resident Management System", align="R")

    pdf_bytes = bytes(pdf.output())
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=fnra_houses_list.pdf"
        }
    )
