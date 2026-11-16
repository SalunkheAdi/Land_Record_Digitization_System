import zipfile
import os

zip_name = "12215890_AdityaSalunkhe_IntelligentLandRecordSystem.zip"

files_to_include = [
    "manage.py",
    "requirements.txt",
    "db.sqlite3",
    "vercel.json",
    "api/index.py",
    "build_files.sh",
    "PROJECT_REPORT.md",
    "README.md",
    "SRS_Intelligent_Land_Record_Digitization_System_CA2.pdf",
    "SRS_Intelligent_Land_Record_Digitization_System_INT253.pdf",
    "build_srs_report.py",
    "INT253_Assignment_Report_Intelligent_Land_Record_System.pdf",
    "check_all_functionality.py"
]

dirs_to_include = [
    "config",
    "records",
    "validation",
    "static",
    "staticfiles",
    "templates",
    "report_assets"
]

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
    # Add root files
    for f in files_to_include:
        if os.path.exists(f):
            zf.write(f, f)
            print(f"Added file: {f}")
            
    # Add directories recursively
    for d in dirs_to_include:
        for root, _, filenames in os.walk(d):
            for filename in filenames:
                if "__pycache__" in root or filename.endswith((".pyc", ".pyo")):
                    continue
                filepath = os.path.join(root, filename)
                arcname = os.path.relpath(filepath, ".")
                zf.write(filepath, arcname)

print(f"ZIP package created successfully: {zip_name} (Size: {os.path.getsize(zip_name) / 1024:.1f} KB)")
