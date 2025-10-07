from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Doctors
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:appointment_id>/generate-zoom/', views.generate_zoom_link, name='generate_zoom_link'),
    
    # Payments
    path('appointments/<int:appointment_id>/payment/', views.initiate_payment, name='initiate_payment'),
    path('appointments/<int:appointment_id>/payment/process/', views.process_bkash_payment, name='process_bkash_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('appointments/<int:appointment_id>/payment/success/', views.payment_success, name='payment_success'),
    
    # AJAX endpoints
    path('api/slots/<int:doctor_id>/<str:date>/', views.get_available_slots, name='get_available_slots'),
    
    # Doctor Dashboard URLs
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointment/<int:appointment_id>/', views.doctor_appointment_detail, name='doctor_appointment_detail'),
    path('doctor/appointment/<int:appointment_id>/complete/', views.doctor_complete_appointment, name='doctor_complete_appointment'),
    path('doctor/appointment/<int:appointment_id>/confirm/', views.doctor_confirm_appointment, name='doctor_confirm_appointment'),
    path('doctor/patients/', views.doctor_patients_list, name='doctor_patients_list'),
    path('doctor/schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('doctor/schedule/delete/<int:slot_id>/', views.delete_time_slot, name='delete_time_slot'),
    path('doctor/<int:doctor_id>/time-slots/', views.get_doctor_time_slots, name='get_doctor_time_slots'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
]
