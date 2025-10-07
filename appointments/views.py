from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Patient, Doctor, Appointment, Payment, TimeSlot
from .forms import PatientRegistrationForm, AppointmentForm, PatientProfileForm
from .zoom_service import create_appointment_meeting
from .bkash_service import BkashPaymentService, initiate_appointment_payment
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    """Home page view"""
    # If user is logged in and is admin/staff, redirect to admin panel
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
    
    doctors = Doctor.objects.filter(is_available=True)[:6]
    context = {
        'doctors': doctors,
        'total_doctors': Doctor.objects.filter(is_available=True).count(),
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
    }
    return render(request, 'appointments/home.html', context)


def register(request):
    """Patient registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the Patient Appointment System.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'appointments/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        # Redirect based on user type
        try:
            # Check if user is a doctor
            if hasattr(request.user, 'doctor'):
                return redirect('doctor_dashboard')
        except Doctor.DoesNotExist:
            pass
        
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check if user is a doctor
            try:
                if hasattr(user, 'doctor'):
                    messages.success(request, f'Welcome back, Dr. {user.doctor.name}!')
                    return redirect('doctor_dashboard')
            except Doctor.DoesNotExist:
                pass
            
            # Redirect based on user type
            if user.is_staff or user.is_superuser:
                messages.success(request, f'Welcome back, Admin {user.get_full_name()}!')
                return redirect('/admin/')
            else:
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'appointments/login.html')


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Patient dashboard view"""
    # Redirect admin/staff users to admin panel
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'Admin users should use the admin panel.')
        return redirect('/admin/')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        # Automatically create patient profile if not exists (only for non-admin users)
        patient = Patient.objects.create(
            user=request.user,
            phone='',  # User can update this in profile
        )
        messages.info(request, 'Profile created! Please update your contact information.')
    
    # Get patient's appointments
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')
    upcoming_appointments = appointments.filter(
        appointment_date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    )
    past_appointments = appointments.filter(
        appointment_date__lt=timezone.now().date()
    ) | appointments.filter(status__in=['completed', 'cancelled'])
    
    context = {
        'patient': patient,
        'appointments': appointments[:5],
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments[:5],
        'total_appointments': appointments.count(),
    }
    return render(request, 'appointments/dashboard.html', context)


@login_required
def book_appointment(request):
    """Book new appointment view"""
    # Redirect admin/staff users to admin panel
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Admin users cannot book appointments. Please use the admin panel to manage appointments.')
        return redirect('/admin/')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user, phone='')
        messages.info(request, 'Profile created! Please update your contact information in profile section.')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.amount = appointment.doctor.consultation_fee
            appointment.save()
            
            # Try to create Zoom meeting (non-blocking)
            try:
                meeting_info = create_appointment_meeting(appointment)
                if meeting_info:
                    # Already saved in create_appointment_meeting function
                    messages.success(request, 'Appointment booked successfully with Zoom link! Please proceed to payment.')
                else:
                    messages.warning(request, 'Appointment booked! Zoom link will be generated after payment. Please proceed to payment.')
            except Exception as e:
                messages.warning(request, 'Appointment booked! Zoom link will be created shortly. Please proceed to payment.')
            
            return redirect('appointment_detail', appointment_id=appointment.id)
        else:
            # Debug form errors - print to console for debugging
            print(f"Form validation failed for user {request.user.username}")
            print(f"Form errors: {form.errors}")
            print(f"Non-field errors: {form.non_field_errors}")
            print(f"Form data: {request.POST}")
            
            # Add specific error messages
            error_messages = []
            for field, errors in form.errors.items():
                if field == '__all__':
                    error_messages.extend(errors)
                else:
                    field_name = form.fields[field].label or field.replace('_', ' ').title()
                    for error in errors:
                        error_messages.append(f"{field_name}: {error}")
            
            if error_messages:
                for msg in error_messages:
                    messages.error(request, msg)
            else:
                messages.error(request, 'Please check all required fields and try again.')
    else:
        form = AppointmentForm()
    
    doctors = Doctor.objects.filter(is_available=True)
    return render(request, 'appointments/book_appointment.html', {'form': form, 'doctors': doctors})


@login_required
def appointment_detail(request, appointment_id):
    """Appointment detail view"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def appointment_list(request):
    """List all appointments for the patient"""
    # Redirect admin/staff users to admin panel
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'Please use the admin panel to view all appointments.')
        return redirect('/admin/appointments/appointment/')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user, phone='')
        messages.info(request, 'Profile created!')
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)
    
    context = {
        'appointments': appointments,
        'status_filter': status,
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    
    if appointment.status in ['completed', 'cancelled']:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('dashboard')
    
    return render(request, 'appointments/cancel_appointment.html', {'appointment': appointment})


@login_required
def profile(request):
    """Patient profile view"""
    # Redirect admin/staff users to admin panel
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, 'Admin users should use the admin panel.')
        return redirect('/admin/')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        patient = Patient.objects.create(user=request.user, phone='')
        messages.info(request, 'Profile created! Please fill in your details.')
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = PatientProfileForm(instance=patient)
    
    return render(request, 'appointments/profile.html', {'form': form, 'patient': patient})


@login_required
def initiate_payment(request, appointment_id):
    """Initiate bKash payment for appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    
    if appointment.payment_status == 'paid':
        messages.info(request, 'Payment already completed for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    # Create or get payment record
    payment, created = Payment.objects.get_or_create(
        appointment=appointment,
        defaults={
            'amount': appointment.amount,
            'payment_method': 'bkash',
            'status': 'pending'
        }
    )
    
    context = {
        'appointment': appointment,
        'payment': payment,
    }
    return render(request, 'appointments/payment.html', context)


@login_required
def process_bkash_payment(request, appointment_id):
    """Process bKash payment - TEST MODE (for demo without credentials)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    # Check if user has patient profile
    if not hasattr(request.user, 'patient'):
        return JsonResponse({'success': False, 'message': 'Patient profile not found'})
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    
    if appointment.payment_status == 'paid':
        return JsonResponse({'success': False, 'message': 'Payment already completed'})
    
    try:
        # TEST MODE: Simulate payment without bKash credentials
        # In production, uncomment the real bKash integration below
        
        # Create payment record
        import uuid
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.amount,
            payment_method='bkash',
            payment_id=f'TEST_{uuid.uuid4().hex[:10]}',
            status='pending'
        )
        
        # Simulate bKash redirect URL (for testing)
        # In real scenario, this would be bKash payment page
        test_payment_url = f'/payment/callback/?paymentID={payment.payment_id}&status=success'
        
        return JsonResponse({
            'success': True,
            'bkash_url': test_payment_url,
            'payment_id': payment.payment_id,
            'test_mode': True
        })
        
        # REAL bKash INTEGRATION (uncomment when you have credentials):
        # result = initiate_appointment_payment(appointment)
        # if result and result.get('success'):
        #     payment = Payment.objects.create(
        #         appointment=appointment,
        #         amount=appointment.amount,
        #         payment_method='bkash',
        #         payment_id=result.get('payment_id'),
        #         status='pending'
        #     )
        #     return JsonResponse({
        #         'success': True,
        #         'bkash_url': result.get('bkash_url'),
        #         'payment_id': result.get('payment_id')
        #     })
        # else:
        #     return JsonResponse({
        #         'success': False,
        #         'message': result.get('message', 'Payment initiation failed')
        #     })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@csrf_exempt
def payment_callback(request):
    """bKash payment callback - TEST MODE"""
    if request.method == 'GET':
        payment_id = request.GET.get('paymentID')
        status = request.GET.get('status')
        
        if status == 'success' and payment_id:
            try:
                payment = Payment.objects.get(payment_id=payment_id)
                
                # TEST MODE: Auto-complete payment without bKash API
                import uuid
                payment.status = 'completed'
                payment.transaction_id = f'TRX_{uuid.uuid4().hex[:10]}'
                payment.bkash_transaction_id = payment.transaction_id
                payment.payment_date = timezone.now()
                payment.save()
                
                # Update appointment payment status
                payment.appointment.payment_status = 'paid'
                payment.appointment.status = 'confirmed'
                payment.appointment.save()
                
                # Create Zoom meeting if not exists
                if not payment.appointment.zoom_join_url:
                    try:
                        meeting_info = create_appointment_meeting(payment.appointment)
                        if meeting_info:
                            messages.success(request, 'Payment successful! Your appointment is confirmed and Zoom meeting link is ready.')
                        else:
                            messages.warning(request, 'Payment successful! However, Zoom link creation failed. Please contact support.')
                    except Exception as zoom_error:
                        messages.warning(request, f'Payment successful! Zoom link will be created shortly.')
                else:
                    messages.success(request, 'Payment successful! Your appointment is confirmed.')
                
                return redirect('payment_success', appointment_id=payment.appointment.id)
                
                # REAL bKash INTEGRATION (uncomment when you have credentials):
                # bkash_service = BkashPaymentService()
                # result = bkash_service.execute_payment(payment_id)
                # 
                # if result and result.get('success'):
                #     payment.status = 'completed'
                #     payment.transaction_id = result.get('transaction_id')
                #     payment.bkash_transaction_id = result.get('transaction_id')
                #     payment.payment_date = timezone.now()
                #     payment.save()
                #     
                #     payment.appointment.payment_status = 'paid'
                #     payment.appointment.status = 'confirmed'
                #     payment.appointment.save()
                #     
                #     messages.success(request, 'Payment successful! Your appointment is confirmed.')
                #     return redirect('appointment_detail', appointment_id=payment.appointment.id)
                # else:
                #     payment.status = 'failed'
                #     payment.save()
                #     messages.error(request, 'Payment execution failed. Please try again.')
                #     return redirect('initiate_payment', appointment_id=payment.appointment.id)
            
            except Payment.DoesNotExist:
                messages.error(request, 'Payment record not found.')
                return redirect('dashboard')
        
        elif status == 'cancel':
            messages.warning(request, 'Payment cancelled.')
            return redirect('dashboard')
        
        else:
            messages.error(request, 'Payment failed.')
            return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def payment_success(request, appointment_id):
    """Payment success page"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    payment = Payment.objects.filter(appointment=appointment, status='completed').first()
    
    context = {
        'appointment': appointment,
        'payment': payment,
    }
    return render(request, 'appointments/payment_success.html', context)


def doctors_list(request):
    """List all available doctors"""
    doctors = Doctor.objects.filter(is_available=True)
    
    # Filter by specialization if provided
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)
    
    context = {
        'doctors': doctors,
        'specializations': Doctor.objects.values_list('specialization', flat=True).distinct(),
    }
    return render(request, 'appointments/doctors_list.html', context)


def doctor_detail(request, doctor_id):
    """Doctor detail view"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    time_slots = TimeSlot.objects.filter(doctor=doctor, is_available=True)
    
    context = {
        'doctor': doctor,
        'time_slots': time_slots,
    }
    return render(request, 'appointments/doctor_detail.html', context)


@login_required
def generate_zoom_link(request, appointment_id):
    """Manually generate Zoom link for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user.patient)
    
    # Only generate if payment is completed
    if appointment.payment_status != 'paid':
        messages.error(request, 'Please complete payment first to generate Zoom link.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    # Check if already has Zoom link
    if appointment.zoom_join_url:
        messages.info(request, 'Zoom link already exists for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    # Generate Zoom link
    try:
        meeting_info = create_appointment_meeting(appointment)
        if meeting_info:
            messages.success(request, '✅ Zoom meeting link generated successfully! You can now join the meeting.')
        else:
            messages.error(request, '⚠️ Zoom API is currently unavailable. Our team has been notified. Your appointment is confirmed, and we will send you the meeting link via email/SMS shortly. You can also contact support for immediate assistance.')
    except Exception as e:
        messages.error(request, '⚠️ Unable to generate Zoom link at this moment. Please contact support or try again later. Your appointment is still confirmed.')
    
    return redirect('appointment_detail', appointment_id=appointment.id)


# AJAX endpoints
@login_required
def get_available_slots(request, doctor_id, date):
    """Get available time slots for a doctor on a specific date"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        appointment_date = datetime.strptime(date, '%Y-%m-%d').date()
        weekday = appointment_date.weekday()
        
        # Get doctor's time slots for this weekday
        time_slots = TimeSlot.objects.filter(
            doctor=doctor,
            weekday=weekday,
            is_available=True
        )
        
        # Get already booked appointments
        booked_times = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=['pending', 'confirmed']
        ).values_list('appointment_time', flat=True)
        
        available_slots = []
        for slot in time_slots:
            if slot.start_time not in booked_times:
                available_slots.append({
                    'time': slot.start_time.strftime('%H:%M'),
                    'display': slot.start_time.strftime('%I:%M %p')
                })
        
        return JsonResponse({'slots': available_slots})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Doctor Dashboard Views
@login_required
def doctor_dashboard(request):
    """Doctor dashboard view - shows all appointments"""
    # Check if user is a doctor or staff
    doctor = None
    
    # Check if user has associated doctor profile
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
    # Otherwise check if admin/staff user
    elif request.user.is_staff:
        # Get doctor ID from query parameter or session
        doctor_id = request.GET.get('doctor_id') or request.session.get('selected_doctor_id')
        
        if not doctor_id:
            # If no doctor selected, show doctor selection page
            doctors = Doctor.objects.filter(is_available=True)
            return render(request, 'appointments/select_doctor.html', {'doctors': doctors})
        
        # Save selected doctor in session
        request.session['selected_doctor_id'] = doctor_id
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            messages.error(request, 'Doctor not found.')
            return redirect('home')
    else:
        messages.error(request, 'You do not have permission to access doctor dashboard.')
        return redirect('home')
    
    if not doctor:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    # Get all appointments for this doctor
    all_appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
    
    # Today's appointments
    today = timezone.now().date()
    todays_appointments = all_appointments.filter(appointment_date=today)
    
    # Upcoming appointments (future dates)
    upcoming_appointments = all_appointments.filter(
        appointment_date__gte=today,
        status__in=['pending', 'confirmed']
    ).exclude(appointment_date=today)[:10]
    
    # Past appointments
    past_appointments = all_appointments.filter(
        appointment_date__lt=today
    ) | all_appointments.filter(status__in=['completed', 'cancelled'])
    
    # Calculate hourly appointment statistics for today
    from datetime import datetime, timedelta
    hourly_stats = []
    if todays_appointments.exists():
        # Group today's appointments by hour
        for hour in range(8, 20):  # 8 AM to 8 PM
            hour_start = datetime.combine(today, datetime.min.time().replace(hour=hour))
            hour_end = hour_start + timedelta(hours=1)
            
            hour_appointments = todays_appointments.filter(
                appointment_time__gte=hour_start.time(),
                appointment_time__lt=hour_end.time(),
                status__in=['pending', 'confirmed']
            ).count()
            
            status = "Available"
            if hour_appointments >= 20:
                status = "FULL (20/20)"
            elif hour_appointments >= 15:
                status = f"Almost Full ({hour_appointments}/20)"
            elif hour_appointments > 0:
                status = f"Booked ({hour_appointments}/20)"
            
            hourly_stats.append({
                'hour': f"{hour:02d}:00 - {hour+1:02d}:00",
                'count': hour_appointments,
                'status': status,
                'is_full': hour_appointments >= 20,
                'is_almost_full': hour_appointments >= 15
            })

    context = {
        'doctor': doctor,
        'total_appointments': all_appointments.count(),
        'today_appointments': todays_appointments.count(),
        'todays_list': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': all_appointments.filter(status='completed').count(),
        'past_appointments': past_appointments[:10],
        'hourly_stats': hourly_stats,
    }
    
    return render(request, 'appointments/doctor_dashboard.html', context)


@login_required
def doctor_appointment_detail(request, appointment_id):
    """Doctor view for appointment details"""
    # Check if user is a doctor or staff
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # If doctor user, verify this is their appointment
    if hasattr(request.user, 'doctor'):
        if appointment.doctor != request.user.doctor:
            messages.error(request, 'You can only view your own appointments.')
            return redirect('doctor_dashboard')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/doctor_appointment_detail.html', context)


@login_required
def doctor_complete_appointment(request, appointment_id):
    """Mark appointment as completed"""
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # If doctor user, verify this is their appointment
    if hasattr(request.user, 'doctor'):
        if appointment.doctor != request.user.doctor:
            messages.error(request, 'You can only manage your own appointments.')
            return redirect('doctor_dashboard')
    appointment.status = 'completed'
    appointment.save()
    
    messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} marked as completed.')
    return redirect('doctor_appointment_detail', appointment_id=appointment.id)


@login_required
def doctor_confirm_appointment(request, appointment_id):
    """Confirm pending appointment"""
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # If doctor user, verify this is their appointment
    if hasattr(request.user, 'doctor'):
        if appointment.doctor != request.user.doctor:
            messages.error(request, 'You can only manage your own appointments.')
            return redirect('doctor_dashboard')
    appointment.status = 'confirmed'
    appointment.save()
    
    messages.success(request, f'Appointment with {appointment.patient.user.get_full_name()} confirmed.')
    return redirect('doctor_appointment_detail', appointment_id=appointment.id)


@login_required
def doctor_patients_list(request):
    """List all patients who have appointments with this doctor"""
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    # Get doctor
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
    else:
        doctor_id = request.session.get('selected_doctor_id')
        if not doctor_id:
            return redirect('doctor_dashboard')
        doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Get unique patients
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')
    patient_ids = appointments.values_list('patient_id', flat=True).distinct()
    patients = Patient.objects.filter(id__in=patient_ids)
    
    context = {
        'doctor': doctor,
        'patients': patients,
    }
    
    return render(request, 'appointments/doctor_patients_list.html', context)


@login_required
def doctor_schedule(request):
    """Manage doctor schedule"""
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    # Get doctor
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
    else:
        doctor_id = request.session.get('selected_doctor_id')
        if not doctor_id:
            return redirect('doctor_dashboard')
        doctor = get_object_or_404(Doctor, id=doctor_id)
    
    time_slots = TimeSlot.objects.filter(doctor=doctor).order_by('weekday', 'start_time')
    
    # Handle POST request for adding new time slot
    if request.method == 'POST':
        from .forms import TimeSlotForm
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.doctor = doctor
            time_slot.save()
            messages.success(request, 'Time slot added successfully!')
            return redirect('doctor_schedule')
    else:
        from .forms import TimeSlotForm
        form = TimeSlotForm()
    
    context = {
        'doctor': doctor,
        'time_slots': time_slots,
        'form': form,
    }
    
    return render(request, 'appointments/doctor_schedule.html', context)


@login_required
def delete_time_slot(request, slot_id):
    """Delete a time slot"""
    if not (hasattr(request.user, 'doctor') or request.user.is_staff):
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    # Get doctor
    if hasattr(request.user, 'doctor'):
        doctor = request.user.doctor
    else:
        doctor_id = request.session.get('selected_doctor_id')
        if not doctor_id:
            return redirect('doctor_dashboard')
        doctor = get_object_or_404(Doctor, id=doctor_id)
    
    time_slot = get_object_or_404(TimeSlot, id=slot_id, doctor=doctor)
    time_slot.delete()
    messages.success(request, 'Time slot deleted successfully!')
    return redirect('doctor_schedule')


def get_doctor_time_slots(request, doctor_id):
    """Get time slots for a specific doctor (AJAX endpoint)"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    time_slots = TimeSlot.objects.filter(doctor=doctor, is_available=True).order_by('weekday', 'start_time')
    
    slots_data = []
    for slot in time_slots:
        slots_data.append({
            'id': slot.id,
            'weekday': slot.weekday,
            'weekday_name': slot.get_weekday_display(),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
        })
    
    return JsonResponse({'slots': slots_data})


@login_required
def doctor_profile(request):
    """Doctor profile edit"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')
    
    doctor_id = request.session.get('selected_doctor_id')
    if not doctor_id:
        return redirect('doctor_dashboard')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'appointments/doctor_profile.html', context)
