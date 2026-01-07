"""Services for W-9 and 1099-NEC generation."""
from __future__ import annotations

from datetime import datetime
import io
import os
import logging
from typing import Dict, List


from app import db
from models import Payee, Payment, TaxFormW9, TaxForm1099NEC, TaxFormEvent

logger = logging.getLogger(__name__)

TAX_TEMPLATE_DIR = os.path.join("static", "tax_forms", "templates")
TAX_OUTPUT_DIR = os.path.join("static", "tax_forms", "generated")


def ensure_dirs():
    os.makedirs(TAX_TEMPLATE_DIR, exist_ok=True)
    os.makedirs(TAX_OUTPUT_DIR, exist_ok=True)


def get_payment_totals(company_id: int, year: int) -> Dict[int, int]:
    totals = {}
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    rows = (
        db.session.query(Payment.payee_id, db.func.sum(Payment.amount_cents))
        .filter(
            Payment.company_id == company_id,
            Payment.paid_at >= start,
            Payment.paid_at < end
        )
        .group_by(Payment.payee_id)
        .all()
    )
    for payee_id, amount in rows:
        totals[payee_id] = int(amount or 0)
    return totals


def get_eligible_payees(company_id: int, year: int, threshold_cents: int = 60000) -> List[dict]:
    totals = get_payment_totals(company_id, year)
    payees = Payee.query.filter_by(company_id=company_id).all()
    eligible = []
    for payee in payees:
        total = totals.get(payee.id, 0)
        if total >= threshold_cents:
            eligible.append({
                "payee": payee,
                "total_cents": total
            })
    return eligible


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _draw_overlay(data: dict) -> io.BytesIO:
    content_lines = []
    for item in data.values():
        value = _escape_pdf_text(item["value"])
        content_lines.append(f"BT /F1 10 Tf {item['x']} {item['y']} Td ({value}) Tj ET")
    content = "\n".join(content_lines)
    content_bytes = content.encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
                   b"/Resources << /Font << /F1 5 0 R >> >> >> endobj\n")
    objects.append(f"4 0 obj << /Length {len(content_bytes)} >> stream\n{content}\nendstream endobj\n".encode("utf-8"))
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    xref_positions = []
    output = bytearray(b"%PDF-1.4\n")
    for obj in objects:
        xref_positions.append(len(output))
        output.extend(obj)
    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects)+1}\n".encode("utf-8"))
    output.extend(b"0000000000 65535 f \n")
    for pos in xref_positions:
        output.extend(f"{pos:010d} 00000 n \n".encode("utf-8"))
    output.extend(b"trailer << /Size %d /Root 1 0 R >>\n" % (len(objects)+1))
    output.extend(b"startxref\n")
    output.extend(str(xref_start).encode("utf-8") + b"\n%%EOF\n")

    packet = io.BytesIO(output)
    packet.seek(0)
    return packet


def _write_overlay(overlay_stream: io.BytesIO, output_path: str):
    with open(output_path, "wb") as output_file:
        output_file.write(overlay_stream.getvalue())


def generate_w9_pdf(company_id: int, payee_id: int) -> TaxFormW9:
    ensure_dirs()
    payee = Payee.query.filter_by(company_id=company_id, id=payee_id).first_or_404()
    template_path = os.path.join(TAX_TEMPLATE_DIR, "w9_template.pdf")
    if not os.path.exists(template_path):
        raise FileNotFoundError("W-9 template PDF not found")

    tin = payee.get_tin()
    overlay_data = {
        "legal_name": {"x": 72, "y": 700, "value": payee.legal_name},
        "business_name": {"x": 72, "y": 680, "value": payee.business_name or ""},
        "address": {"x": 72, "y": 660, "value": payee.address_line1 or ""},
        "city_state_zip": {"x": 72, "y": 640, "value": " ".join(filter(None, [payee.city, payee.state, payee.postal_code]))},
        "tin": {"x": 400, "y": 620, "value": tin},
    }
    overlay_stream = _draw_overlay(overlay_data)
    output_name = f"w9_{company_id}_{payee_id}.pdf"
    output_path = os.path.join(TAX_OUTPUT_DIR, output_name)
    _write_overlay(overlay_stream, output_path)

    form = TaxFormW9.query.filter_by(company_id=company_id, payee_id=payee_id).first()
    if not form:
        form = TaxFormW9(company_id=company_id, payee_id=payee_id)
        db.session.add(form)
    form.status = "final"
    form.pdf_path = output_path
    payee.w9_status = "final"
    db.session.commit()
    return form


def generate_1099nec_pdf(company_id: int, year: int, payee_id: int, total_cents: int) -> TaxForm1099NEC:
    ensure_dirs()
    payee = Payee.query.filter_by(company_id=company_id, id=payee_id).first_or_404()
    template_path = os.path.join(TAX_TEMPLATE_DIR, "1099nec_copyb_template.pdf")
    if not os.path.exists(template_path):
        raise FileNotFoundError("1099-NEC template PDF not found")

    tin = payee.get_tin()
    overlay_data = {
        "payee_name": {"x": 72, "y": 700, "value": payee.legal_name},
        "payee_address": {"x": 72, "y": 680, "value": payee.address_line1 or ""},
        "payee_city_state": {"x": 72, "y": 660, "value": " ".join(filter(None, [payee.city, payee.state, payee.postal_code]))},
        "payee_tin": {"x": 400, "y": 640, "value": tin},
        "box1": {"x": 400, "y": 600, "value": f"{total_cents / 100:.2f}"},
    }
    overlay_stream = _draw_overlay(overlay_data)
    output_name = f"1099nec_{company_id}_{year}_{payee_id}.pdf"
    output_path = os.path.join(TAX_OUTPUT_DIR, output_name)
    _write_overlay(overlay_stream, output_path)

    form = TaxForm1099NEC.query.filter_by(company_id=company_id, year=year, payee_id=payee_id).first()
    if not form:
        form = TaxForm1099NEC(company_id=company_id, year=year, payee_id=payee_id)
        db.session.add(form)
    form.box1_amount_cents = total_cents
    form.pdf_path_copyb = output_path
    db.session.commit()
    return form


def record_tax_form_event(company_id: int, form_type: str, form_id: int, event_type: str, actor_user_id: int | None,
                          request_id: str | None, meta: dict | None = None):
    event = TaxFormEvent(
        company_id=company_id,
        form_type=form_type,
        form_id=form_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        request_id=request_id,
        meta_json=meta or {}
    )
    db.session.add(event)
    db.session.commit()
