# Barrier EDI Application

Aplicație Django pentru gestionarea comenzilor și livrărilor între SAP și parteneri.

## Instalare
1. Creează venv: `python -m venv venv`
2. Activează: `venv\Scripts\activate`
3. Instalează: `pip install -r requirements.txt`
4. Creează `.env` pe baza fișierului `.env.example`
5. Migrează: `python manage.py migrate`
6. Creează superuser: `python manage.py createsuperuser`
7. Rulează: `python manage.py runserver`

## Acces
- Admin: `http://localhost:8000/admin/`
- Portal Parteneri: `http://localhost:8000/partners/login/`
- Comenzi (intern): `http://localhost:8000/orders/`

## Import comenzi SAP
```bash
python manage.py import_sap_orders
```

## Structură
- `orders`: Comenzi din SAP
- `partners`: Portal parteneri
- `deliveries`: Avize și validări
- `core`: Funcționalități comune


