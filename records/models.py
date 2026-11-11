from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator
from decimal import Decimal


class LandOwner(models.Model):
    """
    Model representing a certified citizen or legal entity owning land.
    """
    first_name = models.CharField(max_length=60, verbose_name="First Name")
    last_name = models.CharField(max_length=60, verbose_name="Last Name")
    national_id = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="National ID / Aadhaar Hash",
        help_text="Unique citizen identifier or tax registration number"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Contact Email")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")
    residential_address = models.TextField(verbose_name="Residential Address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Registration Timestamp")

    class Meta:
        verbose_name = "Land Owner"
        verbose_name_plural = "Land Owners"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def parcel_count(self):
        return self.parcels.count()


class LandParcel(models.Model):
    """
    Core Model representing a digitized cadastral land parcel parcel record.
    """
    LAND_TYPE_CHOICES = [
        ('AGRICULTURAL', 'Agricultural'),
        ('RESIDENTIAL', 'Residential'),
        ('COMMERCIAL', 'Commercial'),
        ('INDUSTRIAL', 'Industrial'),
        ('FOREST_GOVT', 'Government / Forest Reserve'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Validation'),
        ('VERIFIED', 'Digitized & Verified'),
        ('FLAGGED', 'Flagged for Discrepancy'),
        ('DISPUTED', 'Under Legal Dispute'),
    ]

    owner = models.ForeignKey(
        LandOwner, 
        on_delete=models.CASCADE, 
        related_name="parcels",
        verbose_name="Registered Owner"
    )
    title_deed_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Title Deed Reference",
        help_text="Official deed document reference (e.g. TD-2024-8831)"
    )
    survey_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Cadastral Survey Number",
        help_text="Survey number allocated in government cadastral map (e.g. SY-104-2B)"
    )
    slug = models.SlugField(
        max_length=120, 
        unique=True, 
        blank=True,
        verbose_name="URL Slug Identifier"
    )
    district = models.CharField(max_length=80, db_index=True, verbose_name="District / Region")
    taluk = models.CharField(max_length=80, verbose_name="Taluk / Subdivision")
    village = models.CharField(max_length=100, verbose_name="Village / Locality")
    
    area_sq_meters = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name="Area (Sq. Meters)",
        help_text="Cadastral plot area in square meters"
    )
    land_type = models.CharField(
        max_length=20, 
        choices=LAND_TYPE_CHOICES, 
        default='RESIDENTIAL',
        verbose_name="Land Use Classification"
    )
    market_valuation = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estimated Market Valuation (INR)"
    )
    gis_coordinates = models.CharField(
        max_length=150, 
        default="12.9716 N, 77.5946 E",
        verbose_name="GIS Centroid Coordinates",
        help_text="Format: Latitude, Longitude (e.g. 12.9716 N, 77.5946 E)"
    )
    is_disputed = models.BooleanField(
        default=False, 
        verbose_name="Litigation / Dispute Flag",
        help_text="Check if parcel has active injunction or dispute"
    )
    digitization_status = models.CharField(
        max_length=25, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name="Validation & Digitization Status"
    )
    registered_date = models.DateField(verbose_name="Official Deed Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Digitized At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")

    class Meta:
        verbose_name = "Land Parcel"
        verbose_name_plural = "Land Parcels"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate clean unique slug from survey number or title deed
            base_slug = slugify(f"{self.district}-{self.survey_number}")
            slug = base_slug
            counter = 1
            while LandParcel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.survey_number} ({self.village}, {self.district})"

    def get_absolute_url(self):
        return reverse('parcel_detail', kwargs={'slug': self.slug})

    @property
    def area_in_acres(self):
        """Convert square meters to acres (1 acre = 4046.86 sq meters)"""
        return round(float(self.area_sq_meters) / 4046.86, 3)

    @property
    def latest_validation(self):
        return self.validations.first()
