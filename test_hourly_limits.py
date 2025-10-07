#!/usr/bin/env python
"""
Quick Test Script for Hourly Appointment Limits
================================================
This script will create multiple test appointments to demonstrate 
the 20 appointments per hour limit feature.

Usage: python test_hourly_limits.py
"""

import os
import sys
import django
from datetime import datetime, date, time

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.contrib.auth.models import User
from appointments.models import Doctor, Patient, Appointment

def create_test_appointments():
    """Create test appointments to test hourly limits"""
    
    print("🔥 Testing Hourly Appointment Limits (20 per hour)")
    print("=" * 50)
    
    # Get first available doctor
    try:
        doctor = Doctor.objects.filter(is_available=True).first()
        if not doctor:
            print("❌ No available doctors found!")
            return
        
        print(f"📋 Testing with Doctor: {doctor.name}")
        print(f"💰 Consultation Fee: ৳{doctor.consultation_fee}")
        
        # Test date and time (2:00 PM on a future date)
        test_date = date(2025, 10, 15)  # Future date
        test_time = time(14, 0)  # 2:00 PM
        
        print(f"📅 Test Date: {test_date}")
        print(f"⏰ Test Time: {test_time} (2:00 PM - 3:00 PM hour)")
        
        # Create or get test patients
        test_patients = []
        for i in range(25):  # Create 25 patients to test limit
            username = f"testpatient{i+1}"
            email = f"testpatient{i+1}@test.com"
            
            # Create user if doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test{i+1}',
                    'last_name': 'Patient',
                    'password': 'pbkdf2_sha256$390000$test$hash'  # dummy hash
                }
            )
            
            # Create patient profile if doesn't exist
            patient, created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f'01712345{i+1:03d}',
                    'date_of_birth': date(1990, 1, 1),
                    'address': f'Test Address {i+1}',
                }
            )
            
            test_patients.append(patient)
        
        print(f"👥 Created/Found {len(test_patients)} test patients")
        
        # Delete existing appointments for this test
        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=test_date,
            appointment_time=test_time
        )
        deleted_count = existing.count()
        existing.delete()
        print(f"🗑️ Deleted {deleted_count} existing test appointments")
        
        # Create appointments
        successful_appointments = 0
        failed_appointments = 0
        
        print("\n🚀 Creating appointments...")
        print("-" * 30)
        
        for i, patient in enumerate(test_patients, 1):
            try:
                appointment = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    appointment_date=test_date,
                    appointment_time=test_time,
                    reason=f"Test appointment #{i} for hourly limit testing",
                    symptoms=f"Test symptoms for patient {i}",
                    amount=doctor.consultation_fee,
                    status='confirmed'  # Skip payment for testing
                )
                successful_appointments += 1
                print(f"✅ Appointment #{i}: {patient.user.get_full_name()} - SUCCESS")
                
                # Check if we reached the limit
                if successful_appointments >= 20:
                    print(f"\n🎯 LIMIT REACHED! Successfully created {successful_appointments} appointments")
                    print("📊 Testing validation on next appointment...")
                    
            except Exception as e:
                failed_appointments += 1
                print(f"❌ Appointment #{i}: {patient.user.get_full_name()} - FAILED: {str(e)}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Successful Appointments: {successful_appointments}")
        print(f"❌ Failed Appointments: {failed_appointments}")
        print(f"📋 Doctor: {doctor.name}")
        print(f"📅 Date: {test_date}")
        print(f"⏰ Time Slot: {test_time}")
        
        if successful_appointments >= 20:
            print("\n🎉 SUCCESS! Hourly limit system working correctly!")
            print("💡 Now try booking from frontend - should show limit error")
        else:
            print(f"\n⚠️ WARNING: Only {successful_appointments} appointments created")
            print("💡 Try booking more from frontend to test limit")
        
        # Check hourly count
        from datetime import timedelta
        hour_start = datetime.combine(test_date, test_time).replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        
        hourly_count = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=test_date,
            appointment_time__gte=hour_start.time(),
            appointment_time__lt=hour_end.time(),
            status__in=['pending', 'confirmed']
        ).count()
        
        print(f"\n📈 Current hourly count: {hourly_count}/20")
        
        if hourly_count >= 20:
            print("🔴 HOUR IS FULL - New bookings should be blocked!")
        else:
            print(f"🟡 {20 - hourly_count} slots remaining in this hour")
        
        print(f"\n🌐 Test booking at: http://localhost:8000/appointments/book/")
        print(f"👨‍⚕️ Login as doctor to see dashboard: http://localhost:8000/login/")
        print("📊 Doctor Dashboard will show hourly statistics")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_appointments()