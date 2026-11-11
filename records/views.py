from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from .models import LandParcel, LandOwner
from .forms import LandParcelForm, LandOwnerForm
from validation.models import ValidationAudit


def home_view(request):
    """
    Public Home Page: Welcome portal introducing the Cadastral Land Record
    Digitization and Validation System, featuring high-level metrics,
    quick title search, key system capabilities, and verified parcel spotlights.
    """
    total_parcels = LandParcel.objects.count()
    verified_parcels = LandParcel.objects.filter(digitization_status='VERIFIED').count()
    total_owners = LandOwner.objects.count()
    active_districts = LandParcel.objects.values('district').distinct().count()
    total_audits = ValidationAudit.objects.count()
    
    featured_parcels = LandParcel.objects.filter(
        digitization_status='VERIFIED'
    ).select_related('owner').order_by('-market_valuation')[:4]
    
    all_districts = LandParcel.objects.values_list('district', flat=True).distinct().order_by('district')[:8]
    
    context = {
        'total_parcels': total_parcels,
        'verified_parcels': verified_parcels,
        'total_owners': total_owners,
        'active_districts': active_districts,
        'total_audits': total_audits,
        'featured_parcels': featured_parcels,
        'all_districts': all_districts,
    }
    return render(request, 'records/home.html', context)


def dashboard_view(request):
    """
    Landing dashboard displaying system analytics, cadastral metrics,
    digitization health scores, and recent parcels.
    """
    total_parcels = LandParcel.objects.count()
    verified_parcels = LandParcel.objects.filter(digitization_status='VERIFIED').count()
    pending_parcels = LandParcel.objects.filter(digitization_status='PENDING').count()
    disputed_parcels = LandParcel.objects.filter(Q(digitization_status='DISPUTED') | Q(is_disputed=True)).count()
    
    total_valuation = LandParcel.objects.aggregate(total=Sum('market_valuation'))['total'] or 0
    total_area = LandParcel.objects.aggregate(total=Sum('area_sq_meters'))['total'] or 0
    total_owners = LandOwner.objects.count()
    total_audits = ValidationAudit.objects.count()
    avg_score = ValidationAudit.objects.aggregate(avg=Avg('compliance_score'))['avg'] or 0

    recent_parcels = LandParcel.objects.select_related('owner').order_by('-created_at')[:6]
    recent_audits = ValidationAudit.objects.select_related('parcel').order_by('-created_at')[:5]

    district_stats = LandParcel.objects.values('district').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'total_parcels': total_parcels,
        'verified_parcels': verified_parcels,
        'pending_parcels': pending_parcels,
        'disputed_parcels': disputed_parcels,
        'total_valuation': total_valuation,
        'total_area': total_area,
        'total_owners': total_owners,
        'total_audits': total_audits,
        'avg_score': round(avg_score, 1),
        'recent_parcels': recent_parcels,
        'recent_audits': recent_audits,
        'district_stats': district_stats,
    }
    return render(request, 'records/dashboard.html', context)


def parcel_list_view(request):
    """
    List view with comprehensive multi-parameter search and filtering.
    Handles GET requests.
    """
    queryset = LandParcel.objects.select_related('owner').all()
    
    # Query parameters
    query = request.GET.get('q', '').strip()
    land_type = request.GET.get('land_type', '').strip()
    status = request.GET.get('status', '').strip()
    district = request.GET.get('district', '').strip()

    if query:
        queryset = queryset.filter(
            Q(survey_number__icontains=query) |
            Q(title_deed_number__icontains=query) |
            Q(village__icontains=query) |
            Q(district__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query) |
            Q(owner__national_id__icontains=query)
        )

    if land_type:
        queryset = queryset.filter(land_type=land_type)

    if status:
        queryset = queryset.filter(digitization_status=status)

    if district:
        queryset = queryset.filter(district__iexact=district)

    # Unique districts for the dropdown filter
    all_districts = LandParcel.objects.values_list('district', flat=True).distinct().order_by('district')

    context = {
        'parcels': queryset,
        'query': query,
        'selected_land_type': land_type,
        'selected_status': status,
        'selected_district': district,
        'all_districts': all_districts,
        'land_type_choices': LandParcel.LAND_TYPE_CHOICES,
        'status_choices': LandParcel.STATUS_CHOICES,
        'result_count': queryset.count(),
    }
    return render(request, 'records/parcel_list.html', context)


def parcel_detail_view(request, slug):
    """
    Detail view using <slug:slug> converter.
    Handles 404 errors via get_object_or_404.
    """
    parcel = get_object_or_404(
        LandParcel.objects.select_related('owner').prefetch_related('validations'),
        slug=slug
    )
    audits = parcel.validations.all().order_by('-inspection_date')
    context = {
        'parcel': parcel,
        'audits': audits,
    }
    return render(request, 'records/parcel_detail.html', context)


def parcel_create_view(request):
    """
    Create a new Land Parcel. Handles GET and POST requests.
    """
    if request.method == 'POST':
        form = LandParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save()
            messages.success(
                request, 
                f"Land Parcel '{parcel.survey_number}' registered and digitized successfully!"
            )
            return redirect('parcel_detail', slug=parcel.slug)
        else:
            messages.error(request, "Please correct the errors in the form submission below.")
    else:
        form = LandParcelForm()

    return render(request, 'records/parcel_form.html', {
        'form': form,
        'action_title': 'Digitize New Land Parcel'
    })


def parcel_update_view(request, pk):
    """
    Update an existing Land Parcel using <int:pk> converter.
    Handles GET and POST requests.
    """
    parcel = get_object_or_404(LandParcel, pk=pk)
    if request.method == 'POST':
        form = LandParcelForm(request.POST, instance=parcel)
        if form.is_valid():
            parcel = form.save()
            messages.success(
                request, 
                f"Land Parcel record '{parcel.survey_number}' updated successfully."
            )
            return redirect('parcel_detail', slug=parcel.slug)
        else:
            messages.error(request, "Please check the form for validation errors.")
    else:
        form = LandParcelForm(instance=parcel)

    return render(request, 'records/parcel_form.html', {
        'form': form,
        'parcel': parcel,
        'action_title': f"Modify Parcel Record - {parcel.survey_number}"
    })


def parcel_delete_view(request, pk):
    """
    Delete a Land Parcel using <int:pk> converter.
    Requires POST request for safety.
    """
    parcel = get_object_or_404(LandParcel, pk=pk)
    if request.method == 'POST':
        survey_number = parcel.survey_number
        parcel.delete()
        messages.warning(request, f"Parcel record '{survey_number}' has been deleted from the registry.")
        return redirect('parcel_list')
    
    return render(request, 'records/parcel_confirm_delete.html', {'parcel': parcel})


def parcels_by_district_view(request, district):
    """
    Filtered view displaying parcels for a specific district using <str:district> converter.
    """
    parcels = LandParcel.objects.filter(district__iexact=district).select_related('owner')
    context = {
        'district': district,
        'parcels': parcels,
        'result_count': parcels.count()
    }
    return render(request, 'records/district_parcels.html', context)


def owner_list_view(request):
    """
    List of registered landowners with their parcel portfolios.
    """
    owners = LandOwner.objects.prefetch_related('parcels').all()
    query = request.GET.get('q', '').strip()
    if query:
        owners = owners.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(national_id__icontains=query) |
            Q(phone__icontains=query)
        )
    return render(request, 'records/owner_list.html', {
        'owners': owners,
        'query': query
    })


def owner_create_view(request):
    """
    Register a new Land Owner. Handles GET and POST requests.
    """
    if request.method == 'POST':
        form = LandOwnerForm(request.POST)
        if form.is_valid():
            owner = form.save()
            messages.success(request, f"Citizen '{owner.full_name}' successfully enrolled into Land Owner Registry.")
            return redirect('owner_list')
        else:
            messages.error(request, "Failed to register owner. Please check the fields.")
    else:
        form = LandOwnerForm()

    return render(request, 'records/owner_form.html', {
        'form': form,
        'action_title': 'Register Certified Land Owner'
    })


def custom_404_view(request, exception=None):
    """
    Custom 404 error page handler.
    """
    return render(request, '404.html', {'path': request.path}, status=404)


def custom_500_view(request):
    """
    Custom 500 error page handler.
    """
    return render(request, '500.html', status=500)
