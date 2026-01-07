"""
Tests for Phase 1 W-9 and 1099-NEC functionality.
"""

from datetime import datetime
import os

from app import app, db
from models import Company, Payee, Payment, TaxForm1099NEC, TaxFormW9
from services.tax_forms_service import (
    get_payment_totals,
    get_eligible_payees,
    generate_w9_pdf,
    generate_1099nec_pdf,
)


def setup_module(module):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


def setup_function(_):
    with app.app_context():
        db.create_all()


def teardown_function(_):
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_payment_aggregation_and_eligibility():
    with app.app_context():
        company = Company(name='Company A')
        db.session.add(company)
        db.session.commit()

        payee = Payee(company_id=company.id, legal_name='Payee One')
        payee.set_tin('123-45-6789')
        db.session.add(payee)
        db.session.commit()

        payment = Payment(
            company_id=company.id,
            payee_id=payee.id,
            amount_cents=60000,
            paid_at=datetime(2025, 1, 15),
            category='contractor'
        )
        db.session.add(payment)
        db.session.commit()

        totals = get_payment_totals(company.id, 2025)
        assert totals[payee.id] == 60000

        eligible = get_eligible_payees(company.id, 2025)
        assert len(eligible) == 1
        assert eligible[0]['payee'].id == payee.id


def test_company_scoping_for_eligibility():
    with app.app_context():
        company_a = Company(name='Company A')
        company_b = Company(name='Company B')
        db.session.add_all([company_a, company_b])
        db.session.commit()

        payee_a = Payee(company_id=company_a.id, legal_name='Payee A')
        payee_a.set_tin('111-22-3333')
        payee_b = Payee(company_id=company_b.id, legal_name='Payee B')
        payee_b.set_tin('222-33-4444')
        db.session.add_all([payee_a, payee_b])
        db.session.commit()

        db.session.add_all([
            Payment(company_id=company_a.id, payee_id=payee_a.id, amount_cents=70000, paid_at=datetime(2025, 2, 1)),
            Payment(company_id=company_b.id, payee_id=payee_b.id, amount_cents=80000, paid_at=datetime(2025, 2, 1)),
        ])
        db.session.commit()

        eligible_a = get_eligible_payees(company_a.id, 2025)
        assert len(eligible_a) == 1
        assert eligible_a[0]['payee'].id == payee_a.id


def test_w9_pdf_generation_creates_file():
    with app.app_context():
        company = Company(name='Company A')
        db.session.add(company)
        db.session.commit()

        payee = Payee(company_id=company.id, legal_name='Payee One', address_line1='123 Main St')
        payee.set_tin('123-45-6789')
        db.session.add(payee)
        db.session.commit()

        form = generate_w9_pdf(company.id, payee.id)
        assert isinstance(form, TaxFormW9)
        assert form.pdf_path
        assert os.path.exists(form.pdf_path)


def test_1099nec_pdf_generation_creates_file():
    with app.app_context():
        company = Company(name='Company A')
        db.session.add(company)
        db.session.commit()

        payee = Payee(company_id=company.id, legal_name='Payee One', address_line1='123 Main St')
        payee.set_tin('123-45-6789')
        db.session.add(payee)
        db.session.commit()

        form = generate_1099nec_pdf(company.id, 2025, payee.id, 75000)
        assert isinstance(form, TaxForm1099NEC)
        assert form.pdf_path_copyb
        assert os.path.exists(form.pdf_path_copyb)


def test_tin_is_encrypted():
    with app.app_context():
        company = Company(name='Company A')
        db.session.add(company)
        db.session.commit()

        payee = Payee(company_id=company.id, legal_name='Payee One')
        payee.set_tin('123-45-6789')
        db.session.add(payee)
        db.session.commit()

        assert payee.tin_last4 == '6789'
        assert payee.tin_encrypted != '123456789'
