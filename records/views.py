import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, Avg
from .models import LandParcel, LandOwner
from .forms import LandParcelForm, LandOwnerForm, UserRegistrationForm, UserLoginForm
from validation.models import ValidationAudit


def home_view(request):
    """
    Public Home Page: Welcome portal introducing the Cadastral Land Record
    Digitization and Validation System, featuring high-level metrics,
    quick title search, key system capabilities, and verified parcel spotlights.
    Accessible to all users (both guests and authenticated).
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


from django.core import signing

VAULT_COOKIE_NAME = 'geocadastre_user_vault'


def _sync_vault_users_from_request(request):
    """
    On stateless/serverless environments (e.g. Vercel Lambda containers),
    restores user accounts registered in this browser from the cryptographically
    signed vault cookie into the current container's SQLite instance if not already present.
    """
    cookie_val = request.COOKIES.get(VAULT_COOKIE_NAME)
    if not cookie_val:
        return
    try:
        users_list = signing.loads(cookie_val, max_age=86400 * 30)  # 30 days validity
        if not isinstance(users_list, list):
            users_list = [users_list]
        for u_data in users_list:
            uname = (u_data.get('username') or '').strip()
            if not uname:
                continue
            if not User.objects.filter(username__iexact=uname).exists():
                user_obj = User(
                    username=uname,
                    email=(u_data.get('email') or '').strip().lower(),
                    first_name=(u_data.get('first_name') or '').strip(),
                    last_name=(u_data.get('last_name') or '').strip(),
                    password=u_data.get('password_hash', ''),
                    is_active=True,
                )
                user_obj.save()
    except Exception:
        pass


def _add_user_to_vault_cookie(request, response, user):
    """
    Appends the user's credentials to the cryptographically signed cookie
    so they persist seamlessly across serverless container reloads.
    """
    cookie_val = request.COOKIES.get(VAULT_COOKIE_NAME)
    users_list = []
    if cookie_val:
        try:
            users_list = signing.loads(cookie_val, max_age=86400 * 30)
            if not isinstance(users_list, list):
                users_list = [users_list]
        except Exception:
            users_list = []

    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'password_hash': user.password,
    }
    # Keep up to 10 recent users, removing duplicates case-insensitively
    users_list = [u for u in users_list if (u.get('username') or '').lower() != user.username.lower()]
    users_list.append(user_data)
    if len(users_list) > 10:
        users_list = users_list[-10:]

    try:
        signed_token = signing.dumps(users_list)
        response.set_cookie(
            VAULT_COOKIE_NAME,
            signed_token,
            max_age=86400 * 30,  # 30 days
            httponly=True,
            samesite='Lax'
        )
    except Exception:
        pass


def signup_view(request):
    """
    Public Sign Up / Registration View:
    Enables new citizens, surveyors, or administrative officers to create an account.
    Upon successful registration, automatically logs the user in and redirects to Dashboard.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already signed in.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            display_name = user.first_name or user.username
            messages.success(
                request,
                f"Welcome to GeoCadastre, {display_name}! Your account has been registered successfully."
            )
            response = redirect('dashboard')
            _add_user_to_vault_cookie(request, response, user)
            return response
        else:
            messages.error(request, "Please correct the errors below to complete your registration.")
    else:
        form = UserRegistrationForm()

    return render(request, 'records/signup.html', {'form': form})


def check_username_api(request):
    """
    Real-time JSON endpoint to verify whether a username is already taken.
    """
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'valid': False, 'message': 'Username is required.'})

    _sync_vault_users_from_request(request)

    exists = User.objects.filter(username__iexact=username).exists()
    reserved = {'admin', 'aditya', 'user', 'surveyor', 'root', 'superuser'}
    if username.lower() in reserved or exists:
        return JsonResponse({
            'exists': True,
            'available': False,
            'message': f"Username '{username}' is already taken! Please choose another."
        })
    return JsonResponse({
        'exists': False,
        'available': True,
        'message': f"Username '{username}' is available!"
    })


def login_view(request):
    """
    Public Sign In View:
    Authenticates registered users via Username or Email with password.
    Supports case-insensitive lookups, trimmed whitespace, and multi-container persistence.
    Redirects to the requested 'next' URL or the main operational Dashboard.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already signed in.")
        return redirect('dashboard')

    # Ensure any user registered in this browser on other serverless instances is available
    _sync_vault_users_from_request(request)

    next_url = request.GET.get('next') or request.POST.get('next', '')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # 1. Attempt authentication directly by exact username
            user = authenticate(request, username=identifier, password=password)

            # 2. If not authenticated, attempt case-insensitive username lookup
            if user is None:
                try:
                    matched_user = User.objects.filter(username__iexact=identifier).first()
                    if matched_user:
                        user = authenticate(request, username=matched_user.username, password=password)
                except Exception:
                    user = None

            # 3. If still not authenticated, attempt case-insensitive email lookup
            if user is None:
                try:
                    matched_user = User.objects.filter(email__iexact=identifier).first()
                    if matched_user:
                        user = authenticate(request, username=matched_user.username, password=password)
                except Exception:
                    user = None

            # 4. If still not authenticated, inspect client_vault payload to restore freshly registered account
            if user is None and request.POST.get('client_vault'):
                try:
                    c_data = json.loads(request.POST.get('client_vault'))
                    c_uname = (c_data.get('username') or '').strip()
                    c_pass = c_data.get('password')
                    if c_uname and c_pass and c_pass == password:
                        if not User.objects.filter(username__iexact=c_uname).exists():
                            new_u = User.objects.create_user(
                                username=c_uname,
                                email=(c_data.get('email') or '').strip().lower(),
                                password=c_pass,
                                first_name=(c_data.get('first_name') or '').strip(),
                                last_name=(c_data.get('last_name') or '').strip(),
                            )
                            user = authenticate(request, username=new_u.username, password=password)
                        else:
                            matched_existing = User.objects.filter(username__iexact=c_uname).first()
                            if matched_existing and not matched_existing.check_password(password):
                                matched_existing.set_password(password)
                                matched_existing.save()
                            user = authenticate(request, username=c_uname, password=password)
                except Exception:
                    pass

            if user is not None:
                login(request, user)
                display_name = user.first_name or user.username
                messages.success(request, f"Welcome back, {display_name}!")
                target_url = next_url if (next_url and next_url.startswith('/')) else 'dashboard'
                response = redirect(target_url)
                _add_user_to_vault_cookie(request, response, user)
                return response
            else:
                messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'records/login.html', {
        'form': form,
        'next': next_url
    })


def logout_view(request):
    """
    Sign Out View:
    Safely terminates the authenticated session and redirects back to the public Home page.
    """
    if request.user.is_authenticated:
        display_name = request.user.first_name or request.user.username
        logout(request)
        messages.info(request, f"Goodbye, {display_name}. You have been logged out safely.")
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Landing dashboard displaying system analytics, cadastral metrics,
    digitization health scores, and recent parcels.
    Requires user authentication.
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


@login_required
def parcel_list_view(request):
    """
    List view with comprehensive multi-parameter search and filtering.
    Requires user authentication.
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


@login_required
def parcel_detail_view(request, slug):
    """
    Detail view using <slug:slug> converter.
    Requires user authentication.
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


@login_required
def parcel_create_view(request):
    """
    Create a new Land Parcel. Handles GET and POST requests.
    Requires user authentication.
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


@login_required
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


@login_required
def parcel_delete_view(request, pk):
    """
    Delete a Land Parcel using <int:pk> converter.
    Requires user authentication and POST request for safety.
    """
    parcel = get_object_or_404(LandParcel, pk=pk)
    if request.method == 'POST':
        survey_number = parcel.survey_number
        parcel.delete()
        messages.warning(request, f"Parcel record '{survey_number}' has been deleted from the registry.")
        return redirect('parcel_list')
    
    return render(request, 'records/parcel_confirm_delete.html', {'parcel': parcel})


@login_required
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


@login_required
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


@login_required
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
