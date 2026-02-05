# Application paie employée de maison (Suisse)

Cette application Streamlit permet de :

- Saisir les jours et heures de travail.
- Calculer une fiche de paie mensuelle (brut, cotisations, net).
- Générer un récapitulatif annuel pour préparer le certificat de salaire.

## Lancer l'application

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
pytest -q
```

## Remarque légale

Les taux et règles suisses peuvent évoluer et dépendent de la situation exacte (canton, assurances, LPP, etc.).
Vérifiez toujours les chiffres avant émission officielle.
