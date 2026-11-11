from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from records.models import LandOwner, LandParcel
from validation.models import ValidationAudit


class ValidationAppTests(TestCase):
    """
    Test suite for Validation application testing JSON response endpoints,
    re_path regex patterns, audit logging, and automated status synchronization.
    """

    def setUp(self):
        self.client = Client()
        self.owner = LandOwner.objects.create(
            first_name="Anita",
            last_name="Roy",
            national_id="NID-TEST-VAL-01",
            phone="+91 97777 66666",
            residential_address="Kolkata, West Bengal"
        )
        self.parcel = LandParcel.objects.create(
            owner=self.owner,
            survey_number="SY-VAL-555",
            title_deed_number="TD-VAL-888",
            district="Kolkata",
            taluk="Alipore",
            village="New Town",
            area_sq_meters=Decimal("800.00"),
            land_type="RESIDENTIAL",
            market_valuation=Decimal("12000000.00"),
            gis_coordinates="22.5726 N, 88.3639 E",
            is_disputed=False,
            digitization_status="PENDING",
            registered_date="2023-02-14"
        )
        self.audit = ValidationAudit.objects.create(
            parcel=self.parcel,
            inspection_code="AUD-2024-TEST99",
            inspector_name="Inspector S. Das",
            inspection_date="2024-04-10",
            fiscal_year=2024,
            compliance_score=94,
            risk_level="LOW",
            title_clarity_passed=True,
            boundary_verification_passed=True,
            zoning_compliance_passed=True,
            encroachment_detected=False,
            ai_anomaly_notes="Title and boundaries validated without errors.",
            final_determination="APPROVED"
        )

    def test_01_api_returns_json_response(self):
        """Test API endpoint returns JSON response meeting the rubric requirement."""
        url = reverse('api_validate_parcel', kwargs={'slug': self.parcel.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('parcel', json_data)
        self.assertIn('validation_result', json_data)
        self.assertEqual(json_data['parcel']['survey_number'], 'SY-VAL-555')
        self.assertIn('compliance_score', json_data['validation_result'])
        self.assertIn('risk_level', json_data['validation_result'])

    def test_02_re_path_fiscal_audit_summary(self):
        r"""Test re_path regex pattern ^audit/fiscal-year/(?P<year>20\d{2})/$."""
        url = '/audit/fiscal-year/2024/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'validation/fiscal_audit_summary.html')
        self.assertEqual(response.context['fiscal_year'], 2024)
        self.assertEqual(response.context['total_audits'], 1)
        self.assertEqual(response.context['approved_count'], 1)

    def test_03_re_path_invalid_fiscal_year_404(self):
        """Test that a non-matching regex year (e.g. 1999 or non-digits) fails the regex and returns 404."""
        response = self.client.get('/audit/fiscal-year/1999/')
        self.assertEqual(response.status_code, 404)

        invalid_response = self.client.get('/audit/fiscal-year/year2024/')
        self.assertEqual(invalid_response.status_code, 404)

    def test_04_validation_audit_creation_post(self):
        """Test creating an audit via POST and verifying status synchronization on parcel."""
        post_url = reverse('validation_create', kwargs={'parcel_id': self.parcel.id})
        post_data = {
            'parcel': self.parcel.id,
            'inspection_code': 'AUD-2024-POST-01',
            'inspector_name': 'Chief Surveyor Ray',
            'inspection_date': '2024-06-01',
            'fiscal_year': 2024,
            'compliance_score': 90,
            'risk_level': 'LOW',
            'title_clarity_passed': True,
            'boundary_verification_passed': True,
            'zoning_compliance_passed': True,
            'encroachment_detected': False,
            'ai_anomaly_notes': 'Verified clean title.',
            'final_determination': 'APPROVED'
        }
        response = self.client.post(post_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ValidationAudit.objects.filter(inspection_code='AUD-2024-POST-01').exists())

        # Verify parcel status synced to VERIFIED
        self.parcel.refresh_from_db()
        self.assertEqual(self.parcel.digitization_status, 'VERIFIED')
