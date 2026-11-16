import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("report_assets", exist_ok=True)

# -------------------------------------------------------------
# 1. GENERATE ER DIAGRAM IMAGE
# -------------------------------------------------------------
def make_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_facecolor('#F7F6F2')
    fig.patch.set_facecolor('#F7F6F2')

    # Title
    ax.text(5, 9.5, "Entity Relationship (ER) Diagram - Cadastral Database", 
            fontsize=15, fontweight='bold', color='#1B2820', ha='center')
    ax.text(5, 9.1, "Relational Schema with 1:N Foreign Keys, Unique Keys, and Domain Constraints", 
            fontsize=9.5, color='#507563', ha='center', style='italic')

    # Card 1: LAND_OWNER
    box1 = patches.FancyBboxPatch((0.4, 4.0), 2.7, 4.6, boxstyle="round,pad=0.15", 
                                  fc="#FFFFFF", ec="#2D4C3E", lw=2)
    ax.add_patch(box1)
    # Header
    hdr1 = patches.Rectangle((0.4, 8.0), 2.7, 0.6, fc="#1B2820", ec="none")
    ax.add_patch(hdr1)
    ax.text(1.75, 8.28, "LAND_OWNER", color="#FFFFFF", fontsize=11, fontweight='bold', ha='center')
    
    owner_fields = [
        ("id (PK)", "IntegerField", True),
        ("first_name", "CharField(60)", False),
        ("last_name", "CharField(60)", False),
        ("national_id (UK)", "CharField(20)", True),
        ("email", "EmailField", False),
        ("phone", "CharField(20)", False),
        ("residential_address", "TextField", False),
        ("created_at", "DateTimeField", False)
    ]
    y = 7.6
    for name, ftype, is_key in owner_fields:
        weight = 'bold' if is_key else 'normal'
        col = '#963A2C' if is_key else '#232724'
        ax.text(0.55, y, name, fontsize=8, fontweight=weight, color=col)
        ax.text(3.0, y, ftype, fontsize=7.5, color='#6B6F6A', ha='right')
        y -= 0.42

    # Card 2: LAND_PARCEL
    box2 = patches.FancyBboxPatch((3.65, 1.2), 2.7, 7.4, boxstyle="round,pad=0.15", 
                                  fc="#FFFFFF", ec="#2D4C3E", lw=2)
    ax.add_patch(box2)
    # Header
    hdr2 = patches.Rectangle((3.65, 8.0), 2.7, 0.6, fc="#2D4C3E", ec="none")
    ax.add_patch(hdr2)
    ax.text(5.0, 8.28, "LAND_PARCEL", color="#FFFFFF", fontsize=11, fontweight='bold', ha='center')

    parcel_fields = [
        ("id (PK)", "IntegerField", True),
        ("owner_id (FK)", "ForeignKey", True),
        ("survey_number (UK)", "CharField(50)", True),
        ("title_deed_number (UK)", "CharField(50)", True),
        ("slug (UK)", "SlugField(120)", True),
        ("district (Index)", "CharField(80)", False),
        ("taluk", "CharField(80)", False),
        ("village", "CharField(100)", False),
        ("area_sq_meters", "DecimalField(12,2)", False),
        ("land_type", "CharField(20)", False),
        ("market_valuation", "DecimalField(14,2)", False),
        ("gis_coordinates", "CharField(150)", False),
        ("is_disputed", "BooleanField", False),
        ("digitization_status", "CharField(25)", False),
        ("registered_date", "DateField", False),
        ("created_at", "DateTimeField", False)
    ]
    y = 7.6
    for name, ftype, is_key in parcel_fields:
        weight = 'bold' if is_key else 'normal'
        col = '#963A2C' if is_key else '#232724'
        ax.text(3.8, y, name, fontsize=8, fontweight=weight, color=col)
        ax.text(6.25, y, ftype, fontsize=7.5, color='#6B6F6A', ha='right')
        y -= 0.4

    # Card 3: VALIDATION_AUDIT
    box3 = patches.FancyBboxPatch((6.9, 2.5), 2.7, 6.1, boxstyle="round,pad=0.15", 
                                  fc="#FFFFFF", ec="#2D4C3E", lw=2)
    ax.add_patch(box3)
    # Header
    hdr3 = patches.Rectangle((6.9, 8.0), 2.7, 0.6, fc="#1B2820", ec="none")
    ax.add_patch(hdr3)
    ax.text(8.25, 8.28, "VALIDATION_AUDIT", color="#FFFFFF", fontsize=11, fontweight='bold', ha='center')

    audit_fields = [
        ("id (PK)", "IntegerField", True),
        ("parcel_id (FK)", "ForeignKey", True),
        ("inspection_code (UK)", "CharField(50)", True),
        ("inspector_name", "CharField(100)", False),
        ("inspection_date", "DateField", False),
        ("fiscal_year", "IntegerField", False),
        ("compliance_score", "IntegerField(0-100)", False),
        ("risk_level", "CharField(15)", False),
        ("title_clarity_passed", "BooleanField", False),
        ("boundary_verified", "BooleanField", False),
        ("zoning_passed", "BooleanField", False),
        ("encroachment_flag", "BooleanField", False),
        ("ai_anomaly_notes", "TextField", False),
        ("final_determination", "CharField(20)", False)
    ]
    y = 7.6
    for name, ftype, is_key in audit_fields:
        weight = 'bold' if is_key else 'normal'
        col = '#963A2C' if is_key else '#232724'
        ax.text(7.05, y, name, fontsize=8, fontweight=weight, color=col)
        ax.text(9.5, y, ftype, fontsize=7.5, color='#6B6F6A', ha='right')
        y -= 0.4

    # Relationship connectors
    # 1. Owner to Parcel (1 to N)
    ax.annotate("", xy=(3.65, 6.5), xytext=(3.1, 6.5),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#2D4C3E"))
    ax.text(3.38, 6.75, "1 : N", fontsize=9, fontweight='bold', color="#2D4C3E", ha='center')
    ax.text(3.38, 6.2, "owns", fontsize=8, style='italic', color="#6B6F6A", ha='center')

    # 2. Parcel to Audit (1 to N)
    ax.annotate("", xy=(6.9, 6.5), xytext=(6.35, 6.5),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#2D4C3E"))
    ax.text(6.62, 6.75, "1 : N", fontsize=9, fontweight='bold', color="#2D4C3E", ha='center')
    ax.text(6.62, 6.2, "audits", fontsize=8, style='italic', color="#6B6F6A", ha='center')

    # Legend / Constraints Note
    leg = patches.FancyBboxPatch((0.4, 0.4), 9.2, 0.65, boxstyle="round,pad=0.1", fc="#FFFFFF", ec="#C8D7CD", lw=1)
    ax.add_patch(leg)
    ax.text(0.6, 0.72, "Legend & Key Rules:", fontsize=8.5, fontweight='bold', color="#1B2820")
    ax.text(2.3, 0.72, "PK = Primary Key", fontsize=8, color="#963A2C", fontweight='bold')
    ax.text(3.8, 0.72, "FK = Foreign Key (CASCADE)", fontsize=8, color="#2D4C3E", fontweight='bold')
    ax.text(5.9, 0.72, "UK = Unique Constraint", fontsize=8, color="#8C631B", fontweight='bold')
    ax.text(7.9, 0.72, "Auto Status Synchronization", fontsize=8, color="#21593E", fontweight='bold')

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("report_assets/er_diagram.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("ER Diagram generated successfully.")

# -------------------------------------------------------------
# 2. GENERATE SYSTEM ARCHITECTURE DIAGRAM
# -------------------------------------------------------------
def make_arch_diagram():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_facecolor('#F7F6F2')
    fig.patch.set_facecolor('#F7F6F2')

    ax.text(5, 4.2, "System Architecture: Layered Cadastral Web Engine", 
            fontsize=13, fontweight='bold', color='#1B2820', ha='center')

    layers = [
        ("Client / Browser Layer", ["Citizen Portal (HTML5/DTL)", "Bootstrap 5 + CSS3 (Natural Palette)", "AJAX Live Heuristic Fetcher (JS)", "Admin Shortcut (Ctrl+Shift+1)"], 0.3),
        ("Web Routing & WSGI Layer", ["Vercel Serverless / Gunicorn WSGI", "config/urls.py Router", "URL Converters: int, str, slug", "Regex Pattern: re_path(audit FY)"], 2.8),
        ("Application & Heuristic Layer", ["records App (CRUD & Dashboards)", "validation App (Audit Logs)", "Intelligent Heuristic Engine", "RESTful JSON API Endpoint"], 5.3),
        ("Data & Persistence Layer", ["Django ORM QuerySet Engine", "SQLite / Cloud PostgreSQL", "WhiteNoise Compressed Static", "Auto-Sync Signals & Constraints"], 7.8)
    ]

    for title, items, x in layers:
        box = patches.FancyBboxPatch((x, 0.5), 2.0, 3.2, boxstyle="round,pad=0.1", fc="#FFFFFF", ec="#2D4C3E", lw=1.5)
        ax.add_patch(box)
        hdr = patches.Rectangle((x, 3.1), 2.0, 0.6, fc="#2D4C3E", ec="none")
        ax.add_patch(hdr)
        ax.text(x + 1.0, 3.38, title, color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')
        
        y = 2.7
        for item in items:
            ax.text(x + 0.12, y, "• " + item, fontsize=7.2, color="#232724")
            y -= 0.6

    # Arrows between layers
    for x in [2.35, 4.85, 7.35]:
        ax.annotate("", xy=(x + 0.4, 2.1), xytext=(x, 2.1),
                    arrowprops=dict(arrowstyle="<|-|>", lw=2, color="#8FAEA0"))

    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 4.6)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("report_assets/system_architecture.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("Architecture Diagram generated successfully.")

# -------------------------------------------------------------
# 3. GENERATE HEURISTIC AUDIT WORKFLOW DIAGRAM
# -------------------------------------------------------------
def make_workflow_diagram():
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=300)
    ax.set_facecolor('#F7F6F2')
    fig.patch.set_facecolor('#F7F6F2')

    ax.text(5, 2.9, "Intelligent Cadastral Validation & Verification Pipeline", 
            fontsize=12.5, fontweight='bold', color='#1B2820', ha='center')

    steps = [
        ("Step 1: Ingestion", "Deed Registration & Owner Enrollment", "Citizen info, Survey No, Title Deed reference recorded.", "#1B2820"),
        ("Step 2: Spatial Check", "GPS Centroid & Area Validation", "Regex syntax verification on GPS coords & area bounds.", "#2D4C3E"),
        ("Step 3: AI Heuristics", "Zoning & Circle Rate Ratios", "Evaluates subdivision limits & valuation sanity ratios.", "#386950"),
        ("Step 4: Statutory Seal", "Revenue Officer Determination", "Score 0-100 & Determination (Approved / Disputed).", "#21593E")
    ]

    x_positions = [0.4, 2.8, 5.2, 7.6]
    for i, ((step, title, desc, color), x) in enumerate(zip(steps, x_positions)):
        box = patches.FancyBboxPatch((x, 0.4), 2.05, 2.1, boxstyle="round,pad=0.1", fc="#FFFFFF", ec=color, lw=1.8)
        ax.add_patch(box)
        hdr = patches.Rectangle((x, 1.95), 2.05, 0.55, fc=color, ec="none")
        ax.add_patch(hdr)
        ax.text(x + 1.025, 2.22, step, color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')
        ax.text(x + 1.025, 1.65, title, color=color, fontsize=7.8, fontweight='bold', ha='center')
        ax.text(x + 1.025, 1.05, desc, color="#4D524D", fontsize=7, ha='center', wrap=True)

        if i < 3:
            ax.annotate("", xy=(x + 2.4, 1.45), xytext=(x + 2.1, 1.45),
                        arrowprops=dict(arrowstyle="-|>", lw=2, color="#2D4C3E"))

    ax.set_xlim(0, 10.1)
    ax.set_ylim(0, 3.3)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("report_assets/workflow_pipeline.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("Workflow Diagram generated successfully.")

# -------------------------------------------------------------
# 4. GENERATE UI PAGE SNAPSHOTS (MOCKUP COMPILATION)
# -------------------------------------------------------------
def make_ui_snapshots():
    fig, axes = plt.subplots(3, 2, figsize=(10, 8.5), dpi=300)
    fig.patch.set_facecolor('#F7F6F2')

    screens = [
        ("1. Public Cadastral Home Portal ('/')", [
            ("Top Navigation", "GeoCadastre Emblem • Home • Dashboard • Parcels • Audits • Owners"),
            ("Hero Section", "Intelligent Land Record Digitization & Validation System"),
            ("Quick Search Bar", "[ Search Survey No / Deed ID / Citizen Name / Village ] [ Verify Record ]"),
            ("Registry Metrics", "Parcels: 6 | Clean Titles: 3 | Certified Owners: 5 | Active Districts: 5"),
            ("Architectural Pillars", "Cadastral Digitization • Automated Heuristics • Dispute Tracking • Audits")
        ], '#1B2820'),
        
        ("2. Analytical Operational Dashboard ('/dashboard/')", [
            ("KPI Metric Cards", "Total: 6 Parcels | Pending: 1 | Litigation/Disputed: 2 | Avg Score: 74.6%"),
            ("Recent Land Units", "SY-104-2B (Bengaluru Urban) • SY-208-4A • SY-55-1C • SY-99-DISP"),
            ("District Density", "Bengaluru Urban: 2 | Ludhiana: 1 | Ahmedabad: 1 | South Delhi: 1"),
            ("Recent Audit Logs", "AUD-2024-BLR01 (96%) • AUD-2024-BLR02 (92%) • AUD-2024-DEL09 (35%)")
        ], '#2D4C3E'),

        ("3. Parcel Registry with Search & Filters ('/parcels/')", [
            ("Multi-Param Filter", "Search Query + Land Use (Agri/Resi) + Status (Verified/Pending) + District"),
            ("Records Table", "Survey No, Title Deed, Owner Name, District/Taluk, Area m², Valuation, Status"),
            ("Direct Actions", "[ Dossier View ] [ Edit Parcel (int:pk) ] [ Perform Official Audit ]"),
            ("Status Badges", "Verified (Green) • Pending (Ochre) • Disputed (Terracotta Clay)")
        ], '#386950'),

        ("4. Parcel Dossier & Live AI Validation ('/parcel/<slug>/')", [
            ("Cadastral Header", "Survey SY-104-2B • Deed TD-KA-2022-8841 • Registered: Apr 15, 2022"),
            ("Cadastral Specs", "Area: 2,400 m² (0.593 Acres) • Valuation: ₹48,000,000 • Centroid: 13.0358 N, 77.5970 E"),
            ("Registered Owner", "Anand Venkatesh • Citizen ID: IND-KA-551024 • Whitefield, Bengaluru"),
            ("Live AI Engine Box", "[ Run Live Verification ] -> Checks Regex, Centroid, Zoning, Circle Rates"),
            ("Audit Trail", "Inspection AUD-2024-BLR01 • Inspector K. S. Rao • Score 96/100 • Low Risk")
        ], '#21593E'),

        ("5. Official Inspection Audit Submission ('/validation/inspect/<id>/')", [
            ("Automated Heuristics", "Pre-computed Compliance Score (96/100) & Risk Category (LOW)"),
            ("Checkpoints Verified", "Title Deed Clarity [✓] • GIS Centroid [✓] • Zoning Compliant [✓]"),
            ("Official Audit Form", "Officer Name, Audit Reference, Fiscal Cycle (2024), Detailed Notes"),
            ("Determination Seal", "Approved (Auto-sets parcel to Verified) / Rejected (Auto-disputes)")
        ], '#507563'),

        ("6. Annual Fiscal Audit Report (re_path: '/audit/fiscal-year/2024/')", [
            ("Regex Route Pattern", "r'^audit/fiscal-year/(?P<year>20\\d{2})/$'"),
            ("Fiscal Cycle KPIs", "Audits in FY 2024: 3 | Approved: 2 | Conditional: 0 | Rejected: 1"),
            ("Mean Health Score", "FY 2024 Aggregate Compliance Index: 74.3%"),
            ("Audits Logged Table", "AUD-2024-BLR01 (96%) • AUD-2024-BLR02 (92%) • AUD-2024-DEL09 (35% Fail)")
        ], '#1B2820'),
    ]

    for ax, (title, items, border_col) in zip(axes.flatten(), screens):
        ax.set_facecolor('#FFFFFF')
        box = patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.03", 
                                      fc="#FFFFFF", ec=border_col, lw=1.5)
        ax.add_patch(box)
        hdr = patches.Rectangle((0.05, 0.8), 0.9, 0.15, fc=border_col, ec="none")
        ax.add_patch(hdr)
        ax.text(0.5, 0.87, title, color="#FFFFFF", fontsize=8.5, fontweight='bold', ha='center')

        y = 0.72
        for heading, desc in items:
            ax.text(0.1, y, heading + ":", fontsize=7.2, fontweight='bold', color=border_col)
            ax.text(0.1, y - 0.05, desc, fontsize=6.5, color="#353A36", wrap=True)
            y -= 0.13

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    plt.suptitle("Cadastral Web Application Working Page Layouts & User Interfaces", 
                 fontsize=13, fontweight='bold', color='#1B2820', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("report_assets/ui_snapshots.png", bbox_inches='tight', dpi=300)
    plt.close()
    print("UI Snapshots graphic generated successfully.")

make_er_diagram()
make_arch_diagram()
make_workflow_diagram()
make_ui_snapshots()
