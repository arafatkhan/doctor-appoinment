"""
Remove Patient Profile from Admin User
Admin users should not have patient profiles
"""

import os
import sys
import django

# Setup Django
sys.path.append('C:/Users/Dell/Desktop/pation-appoinment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.contrib.auth.models import User
from appointments.models import Patient

print("=" * 70)
print("FIXING ADMIN USER - REMOVING PATIENT PROFILE")
print("=" * 70)

try:
    admin_user = User.objects.get(username='admin')
    print(f"\n✓ Found admin user: {admin_user.username}")
    
    # Check if admin has a patient profile
    try:
        patient_profile = Patient.objects.get(user=admin_user)
        print(f"\n⚠️ Admin user has a Patient profile (ID: {patient_profile.id})")
        print("   This causes admin to see patient dashboard instead of admin panel")
        
        # Delete the patient profile
        patient_profile.delete()
        
        print("\n✅ Patient profile removed from admin user!")
        print("\n" + "=" * 70)
        print("FIXED!")
        print("=" * 70)
        print("\nNow when you login as admin:")
        print("1. Go to: http://localhost:8000/admin")
        print("2. You will see the ADMIN PANEL (not patient dashboard)")
        print("3. You can manage all patients, doctors, appointments, payments")
        
    except Patient.DoesNotExist:
        print("\n✓ Admin user does NOT have a patient profile")
        print("  This is correct! Admin should access /admin URL directly")
        print("\n" + "=" * 70)
        print("TO ACCESS ADMIN PANEL:")
        print("=" * 70)
        print("\n1. Go to: http://localhost:8000/admin")
        print("2. Username: admin")
        print("3. Password: (your password)")
        print("\n✅ You will see full admin dashboard with:")
        print("   - Patients management")
        print("   - Doctors management")
        print("   - Appointments management")
        print("   - Payments management")
        print("   - Time Slots management")
        
except User.DoesNotExist:
    print("\n❌ Admin user not found!")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("IMPORTANT NOTES:")
print("=" * 70)
print("\n1. Admin URL: http://localhost:8000/admin")
print("2. Patient URL: http://localhost:8000/dashboard")
print("3. Admin users should use /admin URL")
print("4. Patient users should use /dashboard URL")
print("\n" + "=" * 70)
