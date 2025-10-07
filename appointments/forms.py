from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient, Appointment, Doctor, TimeSlot
from datetime import datetime, timedelta


class PatientRegistrationForm(UserCreationForm):
    """Form for patient registration"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date',
            'id': 'id_date_of_birth',
            'placeholder': 'YYYY-MM-DD'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3})
    )
    medical_history = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Medical History (Optional)', 'rows': 3})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create patient profile
            Patient.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                address=self.cleaned_data.get('address', ''),
                medical_history=self.cleaned_data.get('medical_history', '')
            )
        
        return user


class AppointmentForm(forms.ModelForm):
    """Form for booking appointments"""
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason', 'symptoms']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': datetime.now().strftime('%Y-%m-%d')}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for appointment'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your symptoms (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available doctors
        self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True)
        self.fields['doctor'].empty_label = "Select a Doctor"
        
        # Make required fields explicit
        self.fields['doctor'].required = True
        self.fields['appointment_date'].required = True
        self.fields['appointment_time'].required = True
        self.fields['reason'].required = True
        self.fields['symptoms'].required = False
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if not appointment_date:
            raise forms.ValidationError("Please select an appointment date.")
            
        if appointment_date < datetime.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        
        # Check if date is not more than 30 days in future
        max_date = datetime.now().date() + timedelta(days=30)
        if appointment_date > max_date:
            raise forms.ValidationError("Appointments can only be booked up to 30 days in advance.")
        
        return appointment_date
    
    def clean_appointment_time(self):
        appointment_time = self.cleaned_data.get('appointment_time')
        if not appointment_time:
            raise forms.ValidationError("Please select an appointment time.")
        return appointment_time
    
    def clean_doctor(self):
        doctor = self.cleaned_data.get('doctor')
        if not doctor:
            raise forms.ValidationError("Please select a doctor.")
        if not doctor.is_available:
            raise forms.ValidationError("Selected doctor is not available.")
        return doctor
    
    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason or not reason.strip():
            raise forms.ValidationError("Please provide a reason for the appointment.")
        return reason.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        
        if doctor and appointment_date and appointment_time:
            # Check hourly appointment limit (20 appointments per hour)
            from datetime import timedelta
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            hour_start = appointment_datetime.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            # Count appointments in this hour for this doctor
            hourly_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time__gte=hour_start.time(),
                appointment_time__lt=hour_end.time(),
                status__in=['pending', 'confirmed']
            )
            
            if self.instance.pk:
                hourly_appointments = hourly_appointments.exclude(pk=self.instance.pk)
            
            if hourly_appointments.count() >= 20:
                raise forms.ValidationError(
                    f"⚠️ ডাক্তার {doctor.name} এর {hour_start.strftime('%I:%M %p')} - {hour_end.strftime('%I:%M %p')} "
                    f"এর মধ্যে ইতিমধ্যে 20টি appointment বুক হয়ে গেছে। "
                    f"অন্য সময় বেছে নিন বা পরবর্তী ঘণ্টার জন্য চেষ্টা করুন।"
                )
        
        return cleaned_data


class PatientProfileForm(forms.ModelForm):
    """Form for updating patient profile"""
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Patient
        fields = ['phone', 'date_of_birth', 'address', 'medical_history']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        patient = super().save(commit=False)
        
        # Update user information
        if patient.user:
            patient.user.first_name = self.cleaned_data['first_name']
            patient.user.last_name = self.cleaned_data['last_name']
            patient.user.email = self.cleaned_data['email']
            if commit:
                patient.user.save()
        
        if commit:
            patient.save()
        
        return patient


class TimeSlotForm(forms.ModelForm):
    """Form for creating/editing doctor time slots"""
    class Meta:
        model = TimeSlot
        fields = ['weekday', 'start_time', 'end_time', 'is_available']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'weekday': 'Day of Week',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'is_available': 'Available',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time.')
        
        return cleaned_data
