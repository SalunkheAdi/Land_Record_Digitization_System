# Intelligent Land Record Digitization and Validation System
**Course:** INT253 - Web Development in Python Using Django  
**Academic Task:** Project (Web Application) — 30 Marks  
**Framework:** Django 6.0.7 / Python 3.13.1  
**Database:** SQLite 3  

---

## 🌟 Overview
The **Intelligent Land Record Digitization and Validation System** is a complete, database-driven cadastral management and validation web portal. It facilitates digital land registration, title deed management, GIS centroid mapping, and automated intelligent heuristic audits to protect against land fraud, duplicate titles, and zoning violations.

## 🚀 Key Features & Rubric Highlights
1. **Dedicated Home Portal & Analytics Dashboard**:
   - `/`: Public-facing Home Page with cadastral search, metrics, core pillars, and featured verified holdings.
   - `/dashboard/`: Analytical operations center with aggregate metrics, status charts, and recent audits.
2. **Two Core Applications**:
   - `records`: Cadastral land parcel management, citizen landowner directory, and full CRUD operations.
   - `validation`: Intelligent heuristic audit engine, risk assessment, and fiscal compliance logs.
3. **URL Converters & Request Handling**:
   - 14 distinct URL routes utilizing `<slug:slug>`, `<int:pk>`, `<int:parcel_id>`, `<str:district>`, and regular expression `re_path(r'^audit/fiscal-year/(?P<year>20\d{2})/$')`.
   - Comprehensive GET & POST request handling with CSRF protection.
   - Search across survey numbers, title deeds, owners, and districts.
   - Filter by land use classification, digitization status, and risk level.
   - RESTful JSON validation endpoint (`/api/parcels/<slug>/validate/`).
   - Custom 404 (`404.html`) and 500 (`500.html`) error pages.
4. **Database & ORM Models**:
   - 3 relational models: `LandOwner`, `LandParcel`, and `ValidationAudit` with ForeignKeys, unique constraints, and status synchronization.
   - Custom ModelAdmin registration with search, filters, prepopulated slug fields, and fieldsets.
5. **Modern Natural UI & DTL**:
   - Clean base template inheritance (`templates/base.html`).
   - Organic, natural earth, forest, and stone palette in `static/css/style.css`.
   - Dynamic DTL variables, loops, conditions, and filters (`|floatformat`, `|date`, `|upper`).
   - Client-side live verification script in `static/js/main.js`.
6. **Testing & Code Quality**:
   - 12 unit test cases in `records/tests.py` and `validation/tests.py` (100% pass rate).
   - Clean, well-commented code throughout the codebase.

---

## ⚡ Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Populate Sample Data & Create Superuser
```bash
python manage.py seed_cadastre
```
*Creates 5 certified landowners, 6 land parcels, 5 historical audits, and an admin user:*
- **Username:** `admin`
- **Password:** `admin123`

### 4. Run the Development Server
```bash
python manage.py runserver
```
- Visit `http://127.0.0.1:8000/` for the Public Home Portal.
- Visit `http://127.0.0.1:8000/dashboard/` for the Analytics Dashboard.

### 5. Run Automated Tests
```bash
python manage.py test
```

---

## 📚 Documentation
For complete technical specifications, ER diagrams, URL to view mapping table, and viva explanations, see [PROJECT_REPORT.md](file:///d:/projects/Django/PROJECT_REPORT.md).
