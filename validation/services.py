import re
import io
import base64
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFilter, ImageStat
from records.models import LandParcel


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


class AILandPredictionService:
    """
    Computer Vision and Cadastral Heuristic Service for predicting
    land health score, safety status, vegetation density, built-up encroachment,
    and boundary demarcations from uploaded aerial / satellite land imagery.
    """

    @classmethod
    def get_sample_preset_image(cls, preset_type='clean_agricultural'):
        """
        Synthesizes a realistic simulated aerial cadastral land image as a Base64 data URI.
        Provides instant 1-click testing for evaluators without requiring image uploads.
        """
        img = Image.new('RGB', (480, 360), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)

        if preset_type == 'clean_agricultural':
            # Lush agricultural parcel with organized crop lines and canal
            # Base green fields
            draw.rectangle([0, 0, 480, 360], fill=(46, 125, 50))
            # Crop rows
            for y in range(20, 340, 25):
                draw.line([(30, y), (450, y)], fill=(56, 142, 60), width=8)
            # Golden harvesting strip
            draw.rectangle([60, 60, 200, 160], fill=(180, 150, 60))
            # Irrigation canal
            draw.line([(240, 20), (240, 340)], fill=(33, 150, 243), width=12)
            # Clean Cadastral Boundary (White/Cyan demarcation)
            draw.rectangle([30, 20, 450, 340], outline=(255, 255, 255), width=3)
            # Demarcation Corner Markers
            for cx, cy in [(30, 20), (450, 20), (450, 340), (30, 340)]:
                draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=(255, 215, 0), outline=(255, 255, 255))

        elif preset_type == 'ecological_wetland':
            # Natural wetland / conservation land
            draw.rectangle([0, 0, 480, 360], fill=(30, 80, 45))
            # Large natural water reservoir
            draw.ellipse([80, 60, 380, 300], fill=(21, 101, 192))
            draw.ellipse([140, 100, 320, 260], fill=(13, 71, 161))
            # Natural vegetation buffers
            for x in range(30, 450, 40):
                draw.ellipse([x, 280, x+35, 340], fill=(46, 125, 50))
            # Natural boundary outline
            draw.rectangle([40, 30, 440, 330], outline=(129, 199, 132), width=2)

        elif preset_type == 'disputed_encroached':
            # Dry soil with unauthorized concrete buildings, irregular encroachment & red dispute markers
            draw.rectangle([0, 0, 480, 360], fill=(160, 130, 95))
            # Distressed dry patches
            draw.rectangle([40, 40, 220, 180], fill=(140, 110, 80))
            # Unauthorized concrete structures (Grey blocks)
            draw.rectangle([100, 80, 190, 160], fill=(120, 125, 130), outline=(80, 80, 80), width=2)
            draw.rectangle([220, 140, 320, 240], fill=(135, 140, 145), outline=(70, 70, 70), width=2)
            draw.rectangle([330, 90, 410, 170], fill=(110, 115, 120), outline=(60, 60, 60), width=2)
            # Asphalt/concrete path slicing parcel
            draw.line([(40, 320), (440, 60)], fill=(90, 90, 90), width=16)
            # Irregular Jagged Encroachment lines (Red alert boundaries)
            draw.line([(30, 30), (280, 45), (260, 180), (450, 210), (430, 330), (30, 330), (30, 30)], fill=(220, 53, 69), width=4)
            # Red warning flag points
            for ex, ey in [(280, 45), (260, 180), (450, 210)]:
                draw.ellipse([ex-9, ey-9, ex+9, ey+9], fill=(220, 53, 69), outline=(255, 255, 255))
        else:
            # Neutral terrain
            draw.rectangle([0, 0, 480, 360], fill=(70, 130, 70))
            draw.rectangle([40, 30, 440, 330], outline=(255, 255, 255), width=2)

        # Buffer to Base64 JPEG
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=88)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{b64}"

    @classmethod
    def _parse_image_input(cls, image_input):
        """
        Normalizes image_input from UploadedFile, Base64 data URI, or raw bytes into a PIL Image.
        Returns (pil_image, base64_data_uri).
        """
        if not image_input:
            raise ValueError("No image input provided for land prediction.")

        pil_img = None
        data_uri = ""

        # Case 1: UploadedFile (has .read())
        if hasattr(image_input, 'read'):
            raw_bytes = image_input.read()
            pil_img = Image.open(io.BytesIO(raw_bytes)).convert('RGB')
            b64_str = base64.b64encode(raw_bytes).decode('utf-8')
            # Determine mime
            data_uri = f"data:image/jpeg;base64,{b64_str}"

        # Case 2: String (Base64 data URI or plain Base64)
        elif isinstance(image_input, str):
            if image_input.startswith('data:image'):
                data_uri = image_input
                b64_clean = image_input.split(',', 1)[1]
            else:
                b64_clean = image_input
                data_uri = f"data:image/jpeg;base64,{b64_clean}"
            raw_bytes = base64.b64decode(b64_clean)
            pil_img = Image.open(io.BytesIO(raw_bytes)).convert('RGB')

        # Case 3: Raw bytes
        elif isinstance(image_input, (bytes, bytearray)):
            pil_img = Image.open(io.BytesIO(image_input)).convert('RGB')
            b64_str = base64.b64encode(image_input).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{b64_str}"

        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert('RGB')
            buf = io.BytesIO()
            pil_img.save(buf, format='JPEG', quality=85)
            b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
            data_uri = f"data:image/jpeg;base64,{b64_str}"
        else:
            raise ValueError("Unsupported image format.")

        return pil_img, data_uri

    @classmethod
    def predict_land(cls, image_input, survey_number, custom_land_type=None, custom_district=None, user=None):
        """
        Executes end-to-end AI Land Prediction:
        1. Analyzes satellite/aerial pixel spectrum: vegetation index, built-up structure density, soil/water ratio.
        2. Performs edge detection to assess cadastral boundary demarcation clarity.
        3. Cross-references the survey number against the database of registered parcels for title and dispute integrity.
        4. Calculates the composite Land Health Score (0-100), Land Safety Status (SAFE/MODERATE/UNSAFE),
           and detailed diagnostic metrics.
        """
        survey_number = (survey_number or '').strip().upper()
        if not survey_number:
            survey_number = "SY-UNREG-01"

        pil_img, data_uri = cls._parse_image_input(image_input)

        # Resize to standard analysis resolution (200x200 = 40,000 pixels) for fast deterministic processing
        analysis_img = pil_img.resize((200, 200))
        pixels = list(analysis_img.getdata())
        total_pixels = len(pixels)

        green_count = 0
        builtup_count = 0
        soil_water_count = 0
        dispute_red_count = 0

        for r, g, b in pixels:
            # Vegetation / Canopy detection (Excess Green Index: 2*G - R - B > 15, or G is dominant)
            if (g > r and g > b and g > 60) or ((2 * g - r - b) > 15):
                green_count += 1
            # Built-up / Concrete / Asphalt detection (Neutral tones, low chroma variation, moderate-to-high brightness)
            elif abs(r - g) < 22 and abs(g - b) < 22 and abs(r - b) < 22 and 70 <= (r + g + b) // 3 <= 210:
                builtup_count += 1
            # Red / Orange dispute marker flags or critical anomaly pixels
            elif r > 160 and g < 90 and b < 90:
                dispute_red_count += 1
            else:
                soil_water_count += 1

        veg_ratio = round((green_count / total_pixels) * 100.0, 1)
        builtup_ratio = round((builtup_count / total_pixels) * 100.0, 1)
        soil_water_ratio = round((soil_water_count / total_pixels) * 100.0, 1)

        # Edge analysis for boundary demarcation clarity
        edge_img = analysis_img.convert('L').filter(ImageFilter.FIND_EDGES)
        edge_stat = ImageStat.Stat(edge_img)
        edge_stddev = edge_stat.stddev[0]

        if edge_stddev > 32:
            boundary_clarity = "High Clarity - Demarcated"
            clarity_penalty = 0
        elif edge_stddev > 18:
            boundary_clarity = "Moderate Clarity - Soft Demarcation"
            clarity_penalty = -5
        else:
            boundary_clarity = "Diffused / Irregular Demarcation"
            clarity_penalty = -12

        # Cross-reference with registered LandParcel database
        matched_parcel = LandParcel.objects.filter(survey_number__iexact=survey_number).first()
        anomalies = []

        # Baseline Land Health Score (Starts at 88 pts)
        score = 88
        score += clarity_penalty

        # Heuristic 1: Cadastral Survey Number Syntax
        syntax_valid = bool(re.match(r'^[A-Z0-9\-/\.]+$', survey_number, re.I))
        if not syntax_valid:
            score -= 15
            anomalies.append(f"Survey number '{survey_number}' contains non-standard characters violating cadastral regex.")

        # Heuristic 2: Vegetation Canopy vs Soil Balance
        if veg_ratio >= 40:
            score += 7  # High biological & agricultural fertility
        elif veg_ratio < 10 and builtup_ratio < 25:
            score -= 8  # Barren / soil erosion vulnerability
            anomalies.append("Low vegetation canopy (<10%): High erosion / barren soil profile detected.")

        # Heuristic 3: Built-up encroachment detection
        if builtup_ratio > 35:
            score -= 18
            anomalies.append(f"Significant structural built-up / encroachment detected ({builtup_ratio}% land cover).")
        elif builtup_ratio > 20:
            score -= 8
            anomalies.append(f"Partial structural development ({builtup_ratio}%) identified on imagery.")

        # Heuristic 4: Red dispute marker or severe anomaly check
        if dispute_red_count > 10:
            score -= 35
            anomalies.append("Visual boundary dispute flags / irregular demarcation lines detected in imagery analysis.")

        # Heuristic 5: Cadastral Database Cross-Verification (Annual Log Alignment)
        if matched_parcel:
            if matched_parcel.is_disputed or matched_parcel.digitization_status == 'DISPUTED':
                score -= 35
                anomalies.append(f"CRITICAL DISPUTE: Active tribunal stay order registered against parcel {matched_parcel.survey_number}.")
            elif matched_parcel.digitization_status == 'FLAGGED':
                score -= 15
                anomalies.append(f"Parcel {matched_parcel.survey_number} is flagged for zoning or coordinate review in cadastral registry.")
            elif matched_parcel.digitization_status == 'VERIFIED':
                score += 5  # Bonus for verified clean title
        else:
            # Unregistered parcel notice
            anomalies.append(f"Survey number '{survey_number}' is not yet digitized in the official land records registry (Evaluated via Satellite Heuristics).")

        # Clamp Health Score strictly within [5, 100]
        final_score = max(5, min(100, int(round(score))))

        # Determine Safety Status & Determination
        if final_score >= 80 and not (matched_parcel and matched_parcel.is_disputed):
            safety_status = 'SAFE'
            risk_category = 'Low Risk - Clean Demarcated Land'
            determination = 'APPROVED'
        elif final_score >= 50 and not (matched_parcel and matched_parcel.is_disputed):
            safety_status = 'MODERATE'
            risk_category = 'Medium Risk - Minor Anomaly / Review Advised'
            determination = 'CONDITIONAL'
        else:
            safety_status = 'UNSAFE'
            risk_category = 'High Risk - Critical Discrepancy / Encroachment'
            determination = 'REJECTED'

        # Diagnostic Summary
        summary = (
            f"AI Land Prediction completed for Survey No '{survey_number}'. "
            f"Calculated Land Health Score: {final_score}/100 ({safety_status}). "
            f"Land Cover Composition: {veg_ratio}% Vegetation Canopy, {builtup_ratio}% Built-up Density, {soil_water_ratio}% Soil/Hydrological. "
            f"Boundary Assessment: {boundary_clarity}. Determination: {determination}."
        )

        return {
            'survey_number': survey_number,
            'parcel': matched_parcel,
            'image_data': data_uri,
            'predicted_health_score': final_score,
            'safety_status': safety_status,
            'risk_category': risk_category,
            'determination': determination,
            'vegetation_ratio': veg_ratio,
            'builtup_ratio': builtup_ratio,
            'soil_water_ratio': soil_water_ratio,
            'boundary_clarity': boundary_clarity,
            'anomalies': anomalies,
            'ai_analysis_summary': summary,
            'user': user
        }

