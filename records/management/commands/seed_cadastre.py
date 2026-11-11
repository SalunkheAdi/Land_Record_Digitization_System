import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from records.models import LandOwner, LandParcel
from validation.models import ValidationAudit

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with realistic Cadastral Land Owners, Parcels, and Validation Audits'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Cadastral Database Seeder...")

        # 1. Superuser Creation
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@cadastre.gov.in', 'admin123')
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / admin123"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Clear existing records to ensure clean reproducible demo
        ValidationAudit.objects.all().delete()
        LandParcel.objects.all().delete()
        LandOwner.objects.all().delete()

        # 3. Create Certified Land Owners
        owners_data = [
            {
                'first_name': 'Ramesh',
                'last_name': 'Patel',
                'national_id': 'IND-GJ-774921',
                'email': 'ramesh.patel@cadastre-user.in',
                'phone': '+91 98250 12345',
                'residential_address': 'Plot 42, Shanti Niketan Society, Ahmedabad, Gujarat'
            },
            {
                'first_name': 'Dr. Sunita',
                'last_name': 'Sharma',
                'national_id': 'IND-DL-883109',
                'email': 'sunita.sharma@research.ac.in',
                'phone': '+91 98110 56789',
                'residential_address': 'House 14B, Green Park Extension, New Delhi'
            },
            {
                'first_name': 'Anand',
                'last_name': 'Venkatesh',
                'national_id': 'IND-KA-551024',
                'email': 'anand.v@techcorp.in',
                'phone': '+91 98450 99887',
                'residential_address': 'Flat 304, Palm Meadows, Whitefield, Bengaluru, Karnataka'
            },
            {
                'first_name': 'Gurpreet',
                'last_name': 'Singh',
                'national_id': 'IND-PB-332901',
                'email': 'gurpreet.farm@agrosoil.in',
                'phone': '+91 98720 44556',
                'residential_address': 'Village Raikot, Ludhiana District, Punjab'
            },
            {
                'first_name': 'Priyanka',
                'last_name': 'Nair',
                'national_id': 'IND-KL-902187',
                'email': 'priyanka.nair@coastal.org',
                'phone': '+91 94470 66778',
                'residential_address': 'Riverview Villa, Aluva, Ernakulam, Kerala'
            }
        ]

        owners = {}
        for o in owners_data:
            owner = LandOwner.objects.create(**o)
            owners[o['national_id']] = owner
            self.stdout.write(f"  + Created Owner: {owner.full_name}")

        # 4. Create Land Parcels
        parcels_data = [
            {
                'owner': owners['IND-KA-551024'],
                'survey_number': 'SY-104-2B',
                'title_deed_number': 'TD-KA-2022-8841',
                'district': 'Bengaluru Urban',
                'taluk': 'Bengaluru North',
                'village': 'Hebbal Kempapura',
                'area_sq_meters': Decimal('2400.00'),
                'land_type': 'RESIDENTIAL',
                'market_valuation': Decimal('48000000.00'),
                'gis_coordinates': '13.0358 N, 77.5970 E',
                'is_disputed': False,
                'digitization_status': 'VERIFIED',
                'registered_date': '2022-04-15',
            },
            {
                'owner': owners['IND-KA-551024'],
                'survey_number': 'SY-208-4A',
                'title_deed_number': 'TD-KA-2023-4109',
                'district': 'Bengaluru Urban',
                'taluk': 'Bengaluru East',
                'village': 'Whitefield IT Zone',
                'area_sq_meters': Decimal('6500.00'),
                'land_type': 'COMMERCIAL',
                'market_valuation': Decimal('195000000.00'),
                'gis_coordinates': '12.9698 N, 77.7499 E',
                'is_disputed': False,
                'digitization_status': 'VERIFIED',
                'registered_date': '2023-01-20',
            },
            {
                'owner': owners['IND-PB-332901'],
                'survey_number': 'SY-55-1C',
                'title_deed_number': 'TD-PB-2020-1920',
                'district': 'Ludhiana',
                'taluk': 'Raikot',
                'village': 'Bassian',
                'area_sq_meters': Decimal('40468.60'), # 10 acres
                'land_type': 'AGRICULTURAL',
                'market_valuation': Decimal('32000000.00'),
                'gis_coordinates': '30.6521 N, 75.6022 E',
                'is_disputed': False,
                'digitization_status': 'VERIFIED',
                'registered_date': '2020-11-10',
            },
            {
                'owner': owners['IND-GJ-774921'],
                'survey_number': 'SY-312-9X',
                'title_deed_number': 'TD-GJ-2024-0091',
                'district': 'Ahmedabad',
                'taluk': 'Daskroi',
                'village': 'Sanand Industrial Cluster',
                'area_sq_meters': Decimal('18000.00'),
                'land_type': 'INDUSTRIAL',
                'market_valuation': Decimal('90000000.00'),
                'gis_coordinates': '22.9868 N, 72.3789 E',
                'is_disputed': False,
                'digitization_status': 'PENDING',
                'registered_date': '2024-02-18',
            },
            {
                'owner': owners['IND-DL-883109'],
                'survey_number': 'SY-99-DISP',
                'title_deed_number': 'TD-DL-2021-3312',
                'district': 'South Delhi',
                'taluk': 'Hauz Khas',
                'village': 'Mehrauli Heritage Belt',
                'area_sq_meters': Decimal('1200.00'),
                'land_type': 'RESIDENTIAL',
                'market_valuation': Decimal('36000000.00'),
                'gis_coordinates': '28.5244 N, 77.1855 E',
                'is_disputed': True,
                'digitization_status': 'DISPUTED',
                'registered_date': '2021-08-05',
            },
            {
                'owner': owners['IND-KL-902187'],
                'survey_number': 'SY-401-ECO',
                'title_deed_number': 'TD-KL-2023-7762',
                'district': 'Ernakulam',
                'taluk': 'Aluva',
                'village': 'Periyar Riverside',
                'area_sq_meters': Decimal('3500.00'),
                'land_type': 'AGRICULTURAL',
                'market_valuation': Decimal('17500000.00'),
                'gis_coordinates': '10.1076 N, 76.3516 E',
                'is_disputed': False,
                'digitization_status': 'FLAGGED',
                'registered_date': '2023-09-12',
            }
        ]

        parcels = {}
        for p in parcels_data:
            parcel = LandParcel.objects.create(**p)
            parcels[p['survey_number']] = parcel
            self.stdout.write(f"  + Created Parcel: {parcel.survey_number} in {parcel.district}")

        # 5. Create Cadastral Validation Audits
        audits_data = [
            {
                'parcel': parcels['SY-104-2B'],
                'inspection_code': 'AUD-2024-BLR01',
                'inspector_name': 'Inspector K. S. Rao',
                'inspection_date': '2024-03-10',
                'fiscal_year': 2024,
                'compliance_score': 96,
                'risk_level': 'LOW',
                'title_clarity_passed': True,
                'boundary_verification_passed': True,
                'zoning_compliance_passed': True,
                'encroachment_detected': False,
                'ai_anomaly_notes': 'All cadastral coordinates verified against satellite telemetry. Centroid and boundaries match revenue map perfectly.',
                'final_determination': 'APPROVED',
            },
            {
                'parcel': parcels['SY-208-4A'],
                'inspection_code': 'AUD-2024-BLR02',
                'inspector_name': 'Inspector Deepa Menon',
                'inspection_date': '2024-05-22',
                'fiscal_year': 2024,
                'compliance_score': 92,
                'risk_level': 'LOW',
                'title_clarity_passed': True,
                'boundary_verification_passed': True,
                'zoning_compliance_passed': True,
                'encroachment_detected': False,
                'ai_anomaly_notes': 'Commercial IT corridor clearance verified. Title deed succession authenticated across 30-year lineage.',
                'final_determination': 'APPROVED',
            },
            {
                'parcel': parcels['SY-55-1C'],
                'inspection_code': 'AUD-2025-LDH01',
                'inspector_name': 'Surveyor Harbhajan Singh',
                'inspection_date': '2025-01-14',
                'fiscal_year': 2025,
                'compliance_score': 88,
                'risk_level': 'LOW',
                'title_clarity_passed': True,
                'boundary_verification_passed': True,
                'zoning_compliance_passed': True,
                'encroachment_detected': False,
                'ai_anomaly_notes': 'Canal boundary buffer observed. Soil survey and agricultural landholding within ceiling act regulations.',
                'final_determination': 'APPROVED',
            },
            {
                'parcel': parcels['SY-99-DISP'],
                'inspection_code': 'AUD-2024-DEL09',
                'inspector_name': 'Sub-Registrar V. K. Bansal',
                'inspection_date': '2024-08-30',
                'fiscal_year': 2024,
                'compliance_score': 35,
                'risk_level': 'HIGH',
                'title_clarity_passed': False,
                'boundary_verification_passed': False,
                'zoning_compliance_passed': True,
                'encroachment_detected': True,
                'ai_anomaly_notes': 'CRITICAL ANOMALY: Overlapping boundary claim with adjacent ASI heritage buffer zone. Civil court stay order ongoing.',
                'final_determination': 'REJECTED',
            },
            {
                'parcel': parcels['SY-401-ECO'],
                'inspection_code': 'AUD-2025-KL04',
                'inspector_name': 'Officer Thomas Mathew',
                'inspection_date': '2025-04-18',
                'fiscal_year': 2025,
                'compliance_score': 68,
                'risk_level': 'MEDIUM',
                'title_clarity_passed': True,
                'boundary_verification_passed': False,
                'zoning_compliance_passed': True,
                'encroachment_detected': False,
                'ai_anomaly_notes': 'River setback distance requires re-demarcation by district irrigation engineer before full clearance.',
                'final_determination': 'CONDITIONAL',
            }
        ]

        for a in audits_data:
            audit = ValidationAudit.objects.create(**a)
            self.stdout.write(f"  + Created Audit: {audit.inspection_code} for {audit.parcel.survey_number}")

        self.stdout.write(self.style.SUCCESS(
            f"\nCadastre Database populated successfully with {LandOwner.objects.count()} Owners, {LandParcel.objects.count()} Parcels, and {ValidationAudit.objects.count()} Audits!"
        ))
