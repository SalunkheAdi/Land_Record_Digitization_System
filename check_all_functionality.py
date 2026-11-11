"""
Comprehensive End-to-End System & Functionality Verification Script
Project: Intelligent Land Record Digitization and Validation System
INT253 - Web Development in Python Using Django
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.urls import reverse
from records.models import LandOwner, LandParcel
from validation.models import ValidationAudit
from validation.services import IntelligentValidationEngine

def run_audit():
    client = Client()
    print("=" * 75)
    print("  INTELLIGENT LAND RECORD SYSTEM - COMPLETE FUNCTIONALITY AUDIT")
    print("=" * 75)
    passed = 0
    total = 0

    def assert_check(name, condition, extra=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f" [PASS] {name} {extra}")
        else:
            print(f" [FAIL] {name} - FAILED! {extra}")

    # -------------------------------------------------------------
    # 1. ROOT & GENERAL VIEWS
    # -------------------------------------------------------------
    print("\n--- 1. Testing Core Navigation & General Views ---")
    
    # 1.1 Home View
    res = client.get(reverse('home'))
    assert_check("Home View ('/') Status 200", res.status_code == 200)
    assert_check("Home View Context contains 'featured_parcels'", 'featured_parcels' in res.context)
    assert_check("Home View renders records/home.html", 'records/home.html' in [t.name for t in res.templates])

    # 1.2 Dashboard View
    res = client.get(reverse('dashboard'))
    assert_check("Dashboard View ('/dashboard/') Status 200", res.status_code == 200)
    assert_check("Dashboard Context contains 'total_parcels'", 'total_parcels' in res.context)
    assert_check("Dashboard Context contains 'avg_score'", 'avg_score' in res.context)

    # -------------------------------------------------------------
    # 2. PARCEL LISTING, SEARCH & MULTI-FILTERING
    # -------------------------------------------------------------
    print("\n--- 2. Testing Parcel Search & Multi-Parameter Filter ---")
    
    # 2.1 Unfiltered list
    res = client.get(reverse('parcel_list'))
    assert_check("Parcel List View Status 200", res.status_code == 200)
    all_count = res.context['result_count']
    assert_check("Parcel List returns database records", all_count > 0, f"(Total: {all_count})")

    # 2.2 Keyword Search
    res_search = client.get(reverse('parcel_list'), {'q': 'Bengaluru'})
    assert_check("Search by Keyword 'Bengaluru' returns matching parcels", res_search.status_code == 200 and res_search.context['result_count'] > 0)

    # 2.3 Filter by Land Use Type
    res_type = client.get(reverse('parcel_list'), {'land_type': 'AGRICULTURAL'})
    assert_check("Filter by Land Type 'AGRICULTURAL' works", res_type.status_code == 200 and all(p.land_type == 'AGRICULTURAL' for p in res_type.context['parcels']))

    # 2.4 Filter by Status
    res_status = client.get(reverse('parcel_list'), {'status': 'VERIFIED'})
    assert_check("Filter by Status 'VERIFIED' works", res_status.status_code == 200 and all(p.digitization_status == 'VERIFIED' for p in res_status.context['parcels']))

    # -------------------------------------------------------------
    # 3. URL CONVERTERS (<slug>, <int>, <str>, re_path)
    # -------------------------------------------------------------
    print("\n--- 3. Testing Required URL Converters ---")
    
    sample_parcel = LandParcel.objects.first()
    assert_check("Sample Parcel exists in database", sample_parcel is not None)

    # 3.1 <slug:slug> Converter
    res_slug = client.get(reverse('parcel_detail', kwargs={'slug': sample_parcel.slug}))
    assert_check(f"Slug Converter <slug:{sample_parcel.slug}> Status 200", res_slug.status_code == 200)
    assert_check("Parcel Detail View context contains parcel", res_slug.context['parcel'].id == sample_parcel.id)

    # 3.2 <str:district> Converter
    res_str = client.get(reverse('parcels_by_district', kwargs={'district': sample_parcel.district}))
    assert_check(f"Str Converter <str:{sample_parcel.district}> Status 200", res_str.status_code == 200)
    assert_check("District View context has correct district", res_str.context['district'] == sample_parcel.district)

    # 3.3 <int:pk> Converter (Edit Form)
    res_int = client.get(reverse('parcel_update', kwargs={'pk': sample_parcel.pk}))
    assert_check(f"Int Converter <int:{sample_parcel.pk}> Status 200", res_int.status_code == 200)

    # 3.4 re_path regex Converter (Annual Fiscal Audits: r'^audit/fiscal-year/(?P<year>20\d{2})/$')
    res_re = client.get('/audit/fiscal-year/2024/')
    assert_check("re_path Regex (r'^audit/fiscal-year/2024/$') Status 200", res_re.status_code == 200)
    assert_check("re_path View passes fiscal_year=2024", res_re.context['fiscal_year'] == 2024)

    # 3.5 re_path invalid format returns 404
    res_re_invalid = client.get('/audit/fiscal-year/1999/')
    assert_check("re_path non-matching regex year (1999) returns 404", res_re_invalid.status_code == 404)

    # -------------------------------------------------------------
    # 4. JSON API ENDPOINT
    # -------------------------------------------------------------
    print("\n--- 4. Testing JSON Response API Endpoint ---")
    api_url = reverse('api_validate_parcel', kwargs={'slug': sample_parcel.slug})
    res_api = client.get(api_url)
    assert_check("JSON Validation Endpoint Status 200", res_api.status_code == 200)
    assert_check("Response Content-Type is 'application/json'", res_api['Content-Type'] == 'application/json')
    
    json_data = res_api.json()
    assert_check("JSON contains 'status': 'success'", json_data.get('status') == 'success')
    assert_check("JSON contains 'parcel' object", 'parcel' in json_data and json_data['parcel']['survey_number'] == sample_parcel.survey_number)
    assert_check("JSON contains 'validation_result'", 'validation_result' in json_data)
    assert_check("JSON contains compliance score (0-100)", 0 <= json_data['validation_result']['compliance_score'] <= 100)
    assert_check("JSON contains detailed rule checks", len(json_data['validation_result']['detailed_checks']) >= 4)

    # -------------------------------------------------------------
    # 5. COMPLETE CRUD OPERATIONS THROUGH ORM
    # -------------------------------------------------------------
    print("\n--- 5. Testing Complete CRUD Lifecycle ---")

    # 5.1 CREATE Land Owner via POST
    owner_post_data = {
        'first_name': 'Dev',
        'last_name': 'TestUser',
        'national_id': 'TEST-NID-CRUD-99',
        'email': 'dev.test@cadastre.in',
        'phone': '+91 91234 56789',
        'residential_address': 'Survey Nagar, Testing Zone',
    }
    res_owner = client.post(reverse('owner_create'), owner_post_data)
    assert_check("Owner Create POST redirects (302)", res_owner.status_code == 302)
    test_owner = LandOwner.objects.filter(national_id='TEST-NID-CRUD-99').first()
    assert_check("Owner record inserted into database via ORM", test_owner is not None)

    # 5.2 CREATE Land Parcel via POST (CREATE)
    parcel_post_data = {
        'owner': test_owner.id,
        'title_deed_number': 'TD-CRUD-99881',
        'survey_number': 'SY-CRUD-01',
        'district': 'Mysuru',
        'taluk': 'Mysuru South',
        'village': 'Chamundi Hills',
        'area_sq_meters': '2500.00',
        'land_type': 'RESIDENTIAL',
        'market_valuation': '12500000.00',
        'gis_coordinates': '12.3051 N, 76.6551 E',
        'is_disputed': False,
        'digitization_status': 'PENDING',
        'registered_date': '2024-03-20',
    }
    res_parcel_create = client.post(reverse('parcel_create'), parcel_post_data)
    assert_check("Parcel Create POST redirects (302)", res_parcel_create.status_code == 302)
    new_parcel = LandParcel.objects.filter(survey_number='SY-CRUD-01').first()
    assert_check("Parcel inserted into DB with auto-generated slug", new_parcel is not None and len(new_parcel.slug) > 0, f"(Slug: {new_parcel.slug if new_parcel else 'None'})")

    # 5.3 READ Land Parcel Detail (READ)
    res_read = client.get(reverse('parcel_detail', kwargs={'slug': new_parcel.slug}))
    assert_check("Parcel Read/Detail view renders newly created parcel", res_read.status_code == 200 and res_read.context['parcel'].survey_number == 'SY-CRUD-01')

    # 5.4 UPDATE Land Parcel via POST (UPDATE)
    parcel_update_data = {
        'owner': test_owner.id,
        'title_deed_number': new_parcel.title_deed_number,
        'survey_number': new_parcel.survey_number,
        'district': new_parcel.district,
        'taluk': new_parcel.taluk,
        'village': new_parcel.village,
        'area_sq_meters': '3000.00',  # Changed area from 2500 to 3000
        'land_type': new_parcel.land_type,
        'market_valuation': '15000000.00',  # Changed valuation
        'gis_coordinates': new_parcel.gis_coordinates,
        'is_disputed': False,
        'digitization_status': 'VERIFIED',
        'registered_date': str(new_parcel.registered_date),
    }
    res_update = client.post(reverse('parcel_update', kwargs={'pk': new_parcel.pk}), parcel_update_data)
    assert_check("Parcel Update POST redirects (302)", res_update.status_code == 302)
    new_parcel.refresh_from_db()
    assert_check("Parcel record area updated in DB to 3000.00", new_parcel.area_sq_meters == Decimal('3000.00'))

    # 5.5 RECORD Validation Inspection Audit via POST
    audit_post_data = {
        'parcel': new_parcel.id,
        'inspection_code': 'AUD-CRUD-TEST01',
        'inspector_name': 'Senior Surveyor Naidu',
        'inspection_date': '2024-04-01',
        'fiscal_year': 2024,
        'compliance_score': 95,
        'risk_level': 'LOW',
        'title_clarity_passed': True,
        'boundary_verification_passed': True,
        'zoning_compliance_passed': True,
        'encroachment_detected': False,
        'ai_anomaly_notes': 'Complete clean title confirmed.',
        'final_determination': 'APPROVED',
    }
    res_audit_post = client.post(reverse('validation_create', kwargs={'parcel_id': new_parcel.id}), audit_post_data)
    assert_check("Validation Audit POST redirects (302)", res_audit_post.status_code == 302)
    created_audit = ValidationAudit.objects.filter(inspection_code='AUD-CRUD-TEST01').first()
    assert_check("Validation Audit record inserted into DB", created_audit is not None)
    new_parcel.refresh_from_db()
    assert_check("Parcel status synchronized to 'VERIFIED' via audit signal", new_parcel.digitization_status == 'VERIFIED')

    # 5.6 DELETE Land Parcel via POST (DELETE)
    del_pk = new_parcel.pk
    res_delete = client.post(reverse('parcel_delete', kwargs={'pk': del_pk}))
    assert_check("Parcel Delete POST redirects to parcel list (302)", res_delete.status_code == 302)
    assert_check("Parcel successfully removed from database", not LandParcel.objects.filter(pk=del_pk).exists())
    # Clean up test owner
    test_owner.delete()

    # -------------------------------------------------------------
    # 6. ERROR HANDLING (404 and 500)
    # -------------------------------------------------------------
    print("\n--- 6. Testing Custom Error Handlers ---")
    
    from django.test.utils import override_settings

    # With DEBUG=False, Django invokes our custom handler404
    with override_settings(DEBUG=False):
        # 6.1 Non-existent URL
        res_404 = client.get('/non-existent-page-route-12345/')
        assert_check("Invalid URL returns HTTP 404", res_404.status_code == 404)
        assert_check("Custom 404.html template rendered", '404.html' in [t.name for t in res_404.templates])

        # 6.2 Non-existent parcel slug
        res_slug_404 = client.get('/parcel/completely-fabricated-slug-9999/')
        assert_check("Non-existent Parcel slug returns HTTP 404", res_slug_404.status_code == 404)

    # -------------------------------------------------------------
    # 7. DJANGO ADMIN PORTAL
    # -------------------------------------------------------------
    print("\n--- 7. Testing Django Admin Portal Registration ---")
    res_admin = client.get('/admin/login/')
    assert_check("Django Admin Login page accessible (Status 200)", res_admin.status_code == 200)

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print(f"  AUDIT SUMMARY: {passed} / {total} CHECKS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 75)
    
    return passed == total

if __name__ == '__main__':
    success = run_audit()
    sys.exit(0 if success else 1)
