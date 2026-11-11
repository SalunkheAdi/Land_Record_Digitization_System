from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import LandOwner, LandParcel


class CadastralRecordsTests(TestCase):
    """
    Test suite for Cadastral Records application covering views,
    URL converters (<slug>, <int>, <str>), GET/POST handling, and 404 errors.
    """

    def setUp(self):
        self.client = Client()
        self.owner = LandOwner.objects.create(
            first_name="Vikram",
            last_name="Aditya",
            national_id="NID-TEST-1001",
            email="vikram@test.gov.in",
            phone="+91 99999 88888",
            residential_address="Suite 100, Tech Park, Hyderabad"
        )
        self.parcel = LandParcel.objects.create(
            owner=self.owner,
            survey_number="SY-TEST-77A",
            title_deed_number="TD-TEST-9901",
            district="Hyderabad",
            taluk="Serilingampally",
            village="Gachibowli",
            area_sq_meters=Decimal("1500.00"),
            land_type="COMMERCIAL",
            market_valuation=Decimal("45000000.00"),
            gis_coordinates="17.4401 N, 78.3489 E",
            is_disputed=False,
            digitization_status="VERIFIED",
            registered_date="2023-05-10"
        )

    def test_01_home_view_status(self):
        """Test public home page responds with HTTP 200 and loads context metrics."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'records/home.html')
        self.assertIn('total_parcels', response.context)
        self.assertEqual(response.context['total_parcels'], 1)

    def test_01b_dashboard_view_status(self):
        """Test analytical dashboard view responds with HTTP 200 and loads metrics."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'records/dashboard.html')
        self.assertIn('total_parcels', response.context)
        self.assertEqual(response.context['total_parcels'], 1)

    def test_02_parcel_list_and_search_filter(self):
        """Test parcel list endpoint with search and filtering."""
        response = self.client.get(reverse('parcel_list'), {'q': 'SY-TEST'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'records/parcel_list.html')
        self.assertEqual(len(response.context['parcels']), 1)

        # Non-matching filter
        empty_response = self.client.get(reverse('parcel_list'), {'q': 'NONEXISTENT'})
        self.assertEqual(len(empty_response.context['parcels']), 0)

    def test_03_parcel_detail_slug_converter(self):
        """Test detail endpoint using <slug:slug> converter."""
        url = reverse('parcel_detail', kwargs={'slug': self.parcel.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'records/parcel_detail.html')
        self.assertEqual(response.context['parcel'].survey_number, "SY-TEST-77A")

    def test_04_parcel_create_post_request(self):
        """Test creating a new LandParcel via POST request (CRUD: Create)."""
        create_url = reverse('parcel_create')
        post_data = {
            'owner': self.owner.id,
            'survey_number': 'SY-NEW-88B',
            'title_deed_number': 'TD-NEW-7742',
            'district': 'Hyderabad',
            'taluk': 'Rajendranagar',
            'village': 'Bandlaguda',
            'area_sq_meters': '3200.00',
            'land_type': 'RESIDENTIAL',
            'market_valuation': '16000000.00',
            'gis_coordinates': '17.3616 N, 78.4747 E',
            'is_disputed': False,
            'digitization_status': 'PENDING',
            'registered_date': '2024-01-15',
        }
        response = self.client.post(create_url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirects to detail view
        self.assertTrue(LandParcel.objects.filter(survey_number='SY-NEW-88B').exists())

    def test_05_parcel_update_int_converter(self):
        """Test updating a parcel via POST using <int:pk> converter (CRUD: Update)."""
        edit_url = reverse('parcel_update', kwargs={'pk': self.parcel.pk})
        post_data = {
            'owner': self.owner.id,
            'survey_number': self.parcel.survey_number,
            'title_deed_number': self.parcel.title_deed_number,
            'district': self.parcel.district,
            'taluk': self.parcel.taluk,
            'village': self.parcel.village,
            'area_sq_meters': '1800.00',  # Changed area
            'land_type': self.parcel.land_type,
            'market_valuation': '54000000.00',  # Changed valuation
            'gis_coordinates': self.parcel.gis_coordinates,
            'is_disputed': False,
            'digitization_status': 'VERIFIED',
            'registered_date': str(self.parcel.registered_date),
        }
        response = self.client.post(edit_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.parcel.refresh_from_db()
        self.assertEqual(self.parcel.area_sq_meters, Decimal('1800.00'))

    def test_06_parcels_by_district_str_converter(self):
        """Test filtering parcels using <str:district> converter."""
        url = reverse('parcels_by_district', kwargs={'district': 'Hyderabad'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['district'], 'Hyderabad')
        self.assertContains(response, 'SY-TEST-77A')

    from django.test.utils import override_settings

    @override_settings(DEBUG=False)
    def test_07_custom_404_error_handling(self):
        """Test that invalid slug or non-existent path triggers 404 response using custom 404.html."""
        response = self.client.get('/parcel/non-existent-parcel-slug-9999/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
