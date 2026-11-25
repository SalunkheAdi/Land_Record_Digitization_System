from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from records.models import LandParcel


class ValidationAudit(models.Model):
    """
    Model representing an intelligent audit and validation inspection 
    for a registered cadastral land parcel.
    """
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk - Clean Title'),
        ('MEDIUM', 'Medium Risk - Minor Anomaly'),
        ('HIGH', 'High Risk - Critical Discrepancy'),
    ]

    DETERMINATION_CHOICES = [
        ('APPROVED', 'Approved & Verified in Cadastre'),
        ('CONDITIONAL', 'Conditional Approval - Additional Survey Required'),
        ('REJECTED', 'Rejected - High Encroachment / Title Conflict'),
    ]

    parcel = models.ForeignKey(
        LandParcel,
        on_delete=models.CASCADE,
        related_name="validations",
        verbose_name="Subject Land Parcel"
    )
    inspection_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Inspection / Audit ID",
        help_text="Unique audit reference identifier e.g. AUD-2024-9102"
    )
    inspector_name = models.CharField(
        max_length=100,
        verbose_name="Assigned Cadastral Officer / Validator"
    )
    inspection_date = models.DateField(
        default=timezone.now,
        verbose_name="Inspection Date"
    )
    fiscal_year = models.IntegerField(
        default=2024,
        validators=[MinValueValidator(2000), MaxValueValidator(2099)],
        verbose_name="Audit Fiscal Year",
        help_text="Four-digit fiscal audit year e.g., 2024, 2025"
    )
    compliance_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="AI Compliance Health Score (0-100)",
        help_text="Aggregated validation score calculated by algorithm"
    )
    risk_level = models.CharField(
        max_length=15,
        choices=RISK_LEVEL_CHOICES,
        default='LOW',
        verbose_name="Assessed Risk Level"
    )
    title_clarity_passed = models.BooleanField(
        default=True,
        verbose_name="Title Deed Clarity Verified"
    )
    boundary_verification_passed = models.BooleanField(
        default=True,
        verbose_name="GIS Centroid & Boundary Validated"
    )
    zoning_compliance_passed = models.BooleanField(
        default=True,
        verbose_name="Zoning Classification Compliant"
    )
    encroachment_detected = models.BooleanField(
        default=False,
        verbose_name="Encroachment / Overlap Detected"
    )
    ai_anomaly_notes = models.TextField(
        verbose_name="AI Heuristic & Inspector Audit Notes",
        help_text="Detailed validation findings, boundary discrepancies, and legal remarks"
    )
    final_determination = models.CharField(
        max_length=20,
        choices=DETERMINATION_CHOICES,
        default='APPROVED',
        verbose_name="Final Validation Determination"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Audit Log Timestamp")

    class Meta:
        verbose_name = "Validation Audit"
        verbose_name_plural = "Validation Audits"
        ordering = ['-inspection_date', '-created_at']

    def __str__(self):
        return f"{self.inspection_code} - {self.parcel.survey_number} ({self.get_final_determination_display()})"

    def save(self, *args, **kwargs):
        # Synchronize parcel status upon saving validation determination
        super().save(*args, **kwargs)
        if self.final_determination == 'APPROVED':
            self.parcel.digitization_status = 'VERIFIED'
            self.parcel.is_disputed = False
        elif self.final_determination == 'REJECTED':
            self.parcel.digitization_status = 'DISPUTED'
            self.parcel.is_disputed = True
        elif self.final_determination == 'CONDITIONAL':
            self.parcel.digitization_status = 'FLAGGED'
        self.parcel.save(update_fields=['digitization_status', 'is_disputed'])


class LandPrediction(models.Model):
    """
    Model representing an AI Satellite & Aerial Imagery Land Health Prediction.
    Evaluates land health score, safety status, vegetation density,
    built-up encroachment, and boundary demarcation.
    """
    SAFETY_CHOICES = [
        ('SAFE', 'Safe - Low Risk Clean Land'),
        ('MODERATE', 'Moderate Risk - Minor Discrepancy / Caution'),
        ('UNSAFE', 'Unsafe - Critical Encroachment / High Risk'),
    ]

    survey_number = models.CharField(
        max_length=100,
        verbose_name="Cadastral Survey Number",
        help_text="Survey identifier e.g., SY-104-2B"
    )
    parcel = models.ForeignKey(
        LandParcel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predictions",
        verbose_name="Linked Registered Parcel"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Requested User"
    )
    image_data = models.TextField(
        verbose_name="Uploaded Land Image (Base64)",
        help_text="Base64 encoded data URI of the uploaded land/satellite image"
    )
    predicted_health_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="AI Health Score (0-100)"
    )
    safety_status = models.CharField(
        max_length=20,
        choices=SAFETY_CHOICES,
        default='SAFE',
        verbose_name="Land Safety Status"
    )
    risk_category = models.CharField(
        max_length=50,
        default='Low Risk - Clean Title',
        verbose_name="Risk Category"
    )
    determination = models.CharField(
        max_length=20,
        default='APPROVED',
        verbose_name="Determination"
    )
    vegetation_ratio = models.FloatField(
        default=0.0,
        verbose_name="Vegetation Canopy Ratio (%)"
    )
    builtup_ratio = models.FloatField(
        default=0.0,
        verbose_name="Built-up / Structure Density (%)"
    )
    soil_water_ratio = models.FloatField(
        default=0.0,
        verbose_name="Soil & Hydrological Ratio (%)"
    )
    boundary_clarity = models.CharField(
        max_length=50,
        default='High Clarity - Demarcated',
        verbose_name="Boundary Demarcation Clarity"
    )
    ai_analysis_summary = models.TextField(
        verbose_name="AI Diagnostic Summary"
    )
    audit_logged = models.BooleanField(
        default=False,
        verbose_name="Logged into Annual Audits"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Prediction Timestamp"
    )

    class Meta:
        verbose_name = "AI Land Prediction"
        verbose_name_plural = "AI Land Predictions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.survey_number} - {self.safety_status} ({self.predicted_health_score}%)"
