from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, Doctor, Appointment, Payment, TimeSlot


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'phone', 'get_email', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Details', {
            'fields': ('phone', 'address', 'date_of_birth')
        }),
        ('Medical Information', {
            'fields': ('medical_history',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Patient Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'get_username', 'consultation_fee', 'phone', 'is_available', 'created_at']
    search_fields = ['name', 'specialization', 'email', 'user__username']
    list_filter = ['is_available', 'specialization', 'created_at']
    list_editable = ['is_available', 'consultation_fee']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',),
            'description': 'Link this doctor to a user account for login access. Leave blank if not needed.'
        }),
        ('Personal Information', {
            'fields': ('name', 'specialization', 'email', 'phone')
        }),
        ('Professional Details', {
            'fields': ('qualification', 'experience_years', 'bio', 'consultation_fee', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return '-'
    get_username.short_description = 'Username'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_doctor_name', 'appointment_date', 'appointment_time', 'status', 'payment_status', 'has_zoom_link', 'amount', 'created_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__name']
    list_filter = ['status', 'payment_status', 'appointment_date', 'created_at']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['zoom_meeting_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Patient & Doctor Info', {
            'fields': ('patient', 'doctor')
        }),
        ('Appointment Details', {
            'fields': ('appointment_date', 'appointment_time', 'reason', 'symptoms', 'status', 'amount')
        }),
        ('Zoom Meeting (Manual Entry if API fails)', {
            'fields': ('zoom_meeting_id', 'zoom_join_url', 'zoom_start_url', 'zoom_password'),
            'classes': ('collapse',),
            'description': 'You can manually enter Zoom meeting links here if API is not working.'
        }),
        ('Payment', {
            'fields': ('payment_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.name}"
    get_doctor_name.short_description = 'Doctor'
    
    def has_zoom_link(self, obj):
        return bool(obj.zoom_join_url)
    has_zoom_link.short_description = 'Zoom Link'
    has_zoom_link.boolean = True
    
    actions = ['generate_zoom_link', 'mark_as_confirmed', 'mark_as_completed']
    
    def generate_zoom_link(self, request, queryset):
        from .zoom_service import create_appointment_meeting
        count = 0
        failed = 0
        for appointment in queryset:
            if not appointment.zoom_meeting_id:
                try:
                    meeting_info = create_appointment_meeting(appointment)
                    if meeting_info:
                        count += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
        
        if count > 0:
            self.message_user(request, f"✅ Zoom links generated for {count} appointment(s)")
        if failed > 0:
            self.message_user(request, f"⚠️ Failed to generate links for {failed} appointment(s). Check Zoom credentials or add links manually.", level='warning')
    generate_zoom_link.short_description = "Generate Zoom Meeting Links"
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} appointment(s) marked as confirmed")
    mark_as_confirmed.short_description = "Mark as Confirmed"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} appointment(s) marked as completed")
    mark_as_completed.short_description = "Mark as Completed"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_appointment_date', 'amount', 'payment_method', 'status', 'transaction_id', 'payment_date', 'created_at']
    search_fields = ['appointment__patient__user__first_name', 'appointment__patient__user__last_name', 'transaction_id', 'bkash_transaction_id']
    list_filter = ['status', 'payment_method', 'payment_date', 'created_at']
    readonly_fields = ['transaction_id', 'bkash_transaction_id', 'payment_id', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        return obj.appointment.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'
    
    def get_appointment_date(self, obj):
        return obj.appointment.appointment_date
    get_appointment_date.short_description = 'Appointment Date'


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'get_weekday', 'start_time', 'end_time', 'is_available']
    search_fields = ['doctor__name']
    list_filter = ['weekday', 'is_available', 'doctor']
    list_editable = ['is_available']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.name}"
    get_doctor_name.short_description = 'Doctor'
    
    def get_weekday(self, obj):
        return obj.get_weekday_display()
    get_weekday.short_description = 'Day'
