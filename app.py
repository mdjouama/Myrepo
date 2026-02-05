from __future__ import annotations

from datetime import date, datetime
import json

import pandas as pd
import streamlit as st

from payroll import PayrollRates, WorkEntry, compute_annual_certificate, compute_monthly_payslip

st.set_page_config(page_title="Paie ménage - Suisse", layout="wide")

st.title("💼 Gestion des heures et paie - Employée de maison (Suisse)")
st.caption(
    "Application simple pour saisir les jours travaillés, générer une fiche de paie mensuelle et un récapitulatif annuel."
)

with st.sidebar:
    st.header("Paramètres")
    hourly_rate = st.number_input("Taux horaire (CHF)", min_value=0.0, value=30.0, step=0.5)

    include_vac = st.checkbox("Ajouter indemnité vacances (8.33%)", value=True)
    vac_rate = st.number_input("Taux indemnité vacances", min_value=0.0, max_value=1.0, value=0.0833, step=0.0001)

    st.subheader("Cotisations employée")
    rates = PayrollRates(
        avs_ai_apg=st.number_input("AVS/AI/APG", min_value=0.0, max_value=1.0, value=0.053, step=0.001),
        ac=st.number_input("AC", min_value=0.0, max_value=1.0, value=0.011, step=0.001),
        aanp=st.number_input("AANP", min_value=0.0, max_value=1.0, value=0.01, step=0.001),
        lpp=st.number_input("LPP", min_value=0.0, max_value=1.0, value=0.0, step=0.001),
    )

st.subheader("1) Saisie des jours travaillés")
default_rows = [
    {"date": date.today().isoformat(), "heures": 4.0},
]

df = st.data_editor(
    pd.DataFrame(st.session_state.get("entries", default_rows)),
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "heures": st.column_config.NumberColumn("Heures", min_value=0.0, step=0.5),
    },
    key="editor",
)

st.session_state["entries"] = df.to_dict(orient="records")

entries: list[WorkEntry] = []
for row in st.session_state["entries"]:
    raw_date = row.get("date")
    hours = float(row.get("heures") or 0)
    if not raw_date:
        continue
    if isinstance(raw_date, str):
        parsed_date = datetime.fromisoformat(raw_date).date()
    elif isinstance(raw_date, pd.Timestamp):
        parsed_date = raw_date.date()
    elif isinstance(raw_date, date):
        parsed_date = raw_date
    else:
        continue

    entries.append(WorkEntry(work_date=parsed_date, hours=hours))

if not entries:
    st.info("Ajoutez au moins une ligne de travail pour calculer la paie.")
    st.stop()

all_dates = sorted({e.work_date for e in entries})
min_date = all_dates[0]
max_date = all_dates[-1]

st.subheader("2) Fiche de paie mensuelle")
col1, col2 = st.columns(2)
with col1:
    selected_year = st.number_input("Année", min_value=2000, max_value=2100, value=max_date.year)
with col2:
    selected_month = st.number_input("Mois", min_value=1, max_value=12, value=max_date.month)

slip = compute_monthly_payslip(
    entries,
    year=int(selected_year),
    month=int(selected_month),
    hourly_rate=hourly_rate,
    rates=rates,
    include_vacation_allowance=include_vac,
    vacation_allowance_rate=vac_rate,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Heures", f"{slip.total_hours:.2f}")
metric_cols[1].metric("Brut (CHF)", f"{slip.gross_salary:.2f}")
metric_cols[2].metric("Cotisations (CHF)", f"{slip.total_deductions:.2f}")
metric_cols[3].metric("Net à payer (CHF)", f"{slip.net_salary:.2f}")

st.write("### Détail cotisations")
st.table(pd.DataFrame([slip.deductions]).T.rename(columns={0: "Montant CHF"}))

monthly_json = json.dumps(
    {
        "year": slip.year,
        "month": slip.month,
        "total_hours": slip.total_hours,
        "hourly_rate": slip.hourly_rate,
        "gross_salary": slip.gross_salary,
        "vacation_allowance": slip.vacation_allowance,
        "gross_with_vacation": slip.gross_with_vacation,
        "deductions": slip.deductions,
        "total_deductions": slip.total_deductions,
        "net_salary": slip.net_salary,
    },
    indent=2,
)
st.download_button("Télécharger la fiche mensuelle (JSON)", monthly_json, file_name="fiche_paie_mensuelle.json")

st.subheader("3) Certificat de salaire annuel (récapitulatif)")
year_for_certificate = st.number_input(
    "Année du certificat", min_value=2000, max_value=2100, value=max_date.year, key="year_cert"
)

monthly_slips = [
    compute_monthly_payslip(
        entries,
        year=int(year_for_certificate),
        month=m,
        hourly_rate=hourly_rate,
        rates=rates,
        include_vacation_allowance=include_vac,
        vacation_allowance_rate=vac_rate,
    )
    for m in range(1, 13)
]
annual = compute_annual_certificate(monthly_slips)

summary_df = pd.DataFrame(
    [
        ["Heures totales", annual["total_hours"]],
        ["Salaire brut total", annual["gross_salary"]],
        ["Indemnités vacances", annual["vacation_allowance"]],
        ["Brut + vacances", annual["gross_with_vacation"]],
        ["Total déductions", annual["total_deductions"]],
        ["Net total", annual["net_salary"]],
    ],
    columns=["Champ", "Montant CHF"],
)
st.table(summary_df)

st.download_button(
    "Télécharger le certificat annuel (JSON)",
    json.dumps(annual, indent=2),
    file_name=f"certificat_salaire_{int(year_for_certificate)}.json",
)

st.warning(
    "⚠️ Cette application est un outil d'aide. Vérifiez toujours les taux applicables à votre canton/assurance et les exigences légales suisses en vigueur."
)
