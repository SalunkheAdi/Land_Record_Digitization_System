import re
from decimal import Decimal


class IntelligentValidationEngine:
    """
    Intelligent cadastral validation engine that performs automated heuristic,
    zoning, valuation, and geospatial sanity checks on land parcel records.
    """

    @classmethod
    def evaluate_parcel(cls, parcel):
        """
        Runs comprehensive validation checks against a LandParcel instance.
        Returns a dictionary with score, flags, checks, and determination.
        """
        score = 100
        anomalies = []
        checks = {}

        # 1. Survey Number & Title Deed Integrity
        survey_valid = bool(re.match(r'^[A-Z0-9\-/\.]+$', parcel.survey_number.strip(), re.I))
        checks['survey_number_format'] = {
            'passed': survey_valid,
            'details': 'Valid cadastral alphanumeric format' if survey_valid else 'Survey number contains irregular characters'
        }
        if not survey_valid:
            score -= 15
            anomalies.append('Survey number format violates standard cadastral syntax.')

        # 2. Coordinates Sanity Check
        coords_match = bool(re.search(r'\d+\.?\d*\s*[NS],\s*\d+\.?\d*\s*[EW]', parcel.gis_coordinates, re.I))
        checks['gis_coordinates'] = {
            'passed': coords_match,
            'details': 'Coordinates match standard GPS Centroid schema' if coords_match else 'Coordinates missing or formatted improperly'
        }
        if not coords_match:
            score -= 20
            anomalies.append('GPS centroid coordinates do not conform to standard geospatial representation.')

        # 3. Zoning & Area Threshold Check
        area = float(parcel.area_sq_meters)
        zoning_compliant = True
        zoning_detail = 'Area is within expected legal bounds for land type.'

        if parcel.land_type == 'RESIDENTIAL' and area > 15000:
            zoning_compliant = False
            zoning_detail = 'Residential parcel area exceeds standard municipal subdivision limits (15,000 sq m).'
            score -= 15
            anomalies.append(zoning_detail)
        elif parcel.land_type == 'AGRICULTURAL' and area < 200:
            zoning_compliant = False
            zoning_detail = 'Agricultural plot is suspiciously small (< 200 sq m), possible illegal land conversion.'
            score -= 15
            anomalies.append(zoning_detail)
        elif parcel.land_type == 'FOREST_GOVT' and parcel.market_valuation > Decimal('0.00'):
            zoning_detail = 'Government / Forest reserve designated with private valuation.'
            score -= 25
            anomalies.append(zoning_detail)

        checks['zoning_threshold'] = {
            'passed': zoning_compliant,
            'details': zoning_detail
        }

        # 4. Market Valuation vs Area Sanity Ratio
        rate_per_sqm = float(parcel.market_valuation) / max(area, 1.0)
        valuation_ok = True
        valuation_detail = f'Calculated rate: ₹{rate_per_sqm:,.2f} per sq. meter.'

        if rate_per_sqm < 5.0 and parcel.land_type != 'FOREST_GOVT':
            valuation_ok = False
            valuation_detail += ' Warning: Valuation appears suspiciously undervalued (< ₹5/sqm).'
            score -= 10
            anomalies.append('Valuation anomaly: Plot is significantly undervalued against circle rates.')
        elif rate_per_sqm > 500000.0:
            valuation_ok = False
            valuation_detail += ' Warning: Valuation rate is extraordinarily high (> ₹500,000/sqm).'
            score -= 10
            anomalies.append('Valuation anomaly: Rate significantly exceeds local municipal ceiling.')

        checks['valuation_sanity'] = {
            'passed': valuation_ok,
            'details': valuation_detail
        }

        # 5. Litigation / Dispute status
        if parcel.is_disputed:
            score -= 35
            anomalies.append('Active litigation or court stay order registered against this parcel.')
            checks['litigation_status'] = {
                'passed': False,
                'details': 'Active dispute flag is set.'
            }
        else:
            checks['litigation_status'] = {
                'passed': True,
                'details': 'No active litigation recorded in land tribunal.'
            }

        score = max(0, min(score, 100))

        if score >= 80 and not parcel.is_disputed:
            risk_level = 'LOW'
            determination = 'APPROVED'
        elif score >= 50 and not parcel.is_disputed:
            risk_level = 'MEDIUM'
            determination = 'CONDITIONAL'
        else:
            risk_level = 'HIGH'
            determination = 'REJECTED'

        return {
            'parcel_id': parcel.id,
            'survey_number': parcel.survey_number,
            'district': parcel.district,
            'owner': parcel.owner.full_name,
            'compliance_score': score,
            'risk_level': risk_level,
            'determination': determination,
            'checks': checks,
            'anomalies': anomalies,
            'summary': f"AI automated validation completed with a compliance score of {score}/100. Status: {determination}."
        }
