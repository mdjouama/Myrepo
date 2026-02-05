from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class PayrollRates:
    """Taux appliqués sur le salaire brut (part employée)."""

    avs_ai_apg: float = 0.053
    ac: float = 0.011
    aanp: float = 0.01
    lpp: float = 0.0


@dataclass(frozen=True)
class WorkEntry:
    work_date: date
    hours: float


@dataclass(frozen=True)
class MonthlyPayslip:
    year: int
    month: int
    total_hours: float
    hourly_rate: float
    gross_salary: float
    vacation_allowance: float
    gross_with_vacation: float
    deductions: dict[str, float]
    total_deductions: float
    net_salary: float


def _round(value: float) -> float:
    return round(value, 2)


def compute_monthly_payslip(
    entries: Iterable[WorkEntry],
    *,
    year: int,
    month: int,
    hourly_rate: float,
    rates: PayrollRates,
    include_vacation_allowance: bool = True,
    vacation_allowance_rate: float = 0.0833,
) -> MonthlyPayslip:
    month_entries = [
        entry for entry in entries if entry.work_date.year == year and entry.work_date.month == month
    ]
    total_hours = sum(entry.hours for entry in month_entries)
    gross_salary = total_hours * hourly_rate
    vacation_allowance = gross_salary * vacation_allowance_rate if include_vacation_allowance else 0.0
    gross_with_vacation = gross_salary + vacation_allowance

    deductions = {
        "AVS/AI/APG": gross_with_vacation * rates.avs_ai_apg,
        "AC": gross_with_vacation * rates.ac,
        "AANP": gross_with_vacation * rates.aanp,
        "LPP": gross_with_vacation * rates.lpp,
    }
    deductions = {key: _round(value) for key, value in deductions.items()}
    total_deductions = _round(sum(deductions.values()))
    net_salary = _round(gross_with_vacation - total_deductions)

    return MonthlyPayslip(
        year=year,
        month=month,
        total_hours=_round(total_hours),
        hourly_rate=_round(hourly_rate),
        gross_salary=_round(gross_salary),
        vacation_allowance=_round(vacation_allowance),
        gross_with_vacation=_round(gross_with_vacation),
        deductions=deductions,
        total_deductions=total_deductions,
        net_salary=net_salary,
    )


def compute_annual_certificate(monthly_slips: Iterable[MonthlyPayslip]) -> dict[str, float | int]:
    slips = list(monthly_slips)
    if not slips:
        return {
            "year": 0,
            "total_hours": 0.0,
            "gross_salary": 0.0,
            "vacation_allowance": 0.0,
            "gross_with_vacation": 0.0,
            "total_deductions": 0.0,
            "net_salary": 0.0,
        }

    year = slips[0].year
    return {
        "year": year,
        "total_hours": _round(sum(s.total_hours for s in slips)),
        "gross_salary": _round(sum(s.gross_salary for s in slips)),
        "vacation_allowance": _round(sum(s.vacation_allowance for s in slips)),
        "gross_with_vacation": _round(sum(s.gross_with_vacation for s in slips)),
        "total_deductions": _round(sum(s.total_deductions for s in slips)),
        "net_salary": _round(sum(s.net_salary for s in slips)),
    }
