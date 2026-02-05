from datetime import date

from payroll import PayrollRates, WorkEntry, compute_annual_certificate, compute_monthly_payslip


def test_compute_monthly_payslip_basic():
    entries = [
        WorkEntry(date(2026, 1, 4), 4),
        WorkEntry(date(2026, 1, 11), 5),
    ]
    slip = compute_monthly_payslip(
        entries,
        year=2026,
        month=1,
        hourly_rate=30.0,
        rates=PayrollRates(avs_ai_apg=0.053, ac=0.011, aanp=0.01, lpp=0.0),
    )

    assert slip.total_hours == 9
    assert slip.gross_salary == 270
    assert slip.gross_with_vacation == 292.49
    assert slip.total_deductions == 21.64
    assert slip.net_salary == 270.85


def test_compute_annual_certificate():
    entries = [
        WorkEntry(date(2026, 1, 4), 4),
        WorkEntry(date(2026, 2, 4), 4),
    ]
    rates = PayrollRates()
    slips = [
        compute_monthly_payslip(entries, year=2026, month=1, hourly_rate=30, rates=rates),
        compute_monthly_payslip(entries, year=2026, month=2, hourly_rate=30, rates=rates),
    ]
    annual = compute_annual_certificate(slips)
    assert annual["year"] == 2026
    assert annual["total_hours"] == 8
    assert annual["gross_salary"] == 240
