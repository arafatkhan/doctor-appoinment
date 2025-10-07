"""
Fix Admin User Permissions
This script will make the admin user a proper superuser with staff permissions
"""

import os
import sys
import django

# Setup Django
sys.path.append('C:/Users/Dell/Desktop/pation-appoinment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 70)
print("FIXING ADMIN USER PERMISSIONS")
print("=" * 70)

# Find admin user
try:
    admin_user = User.objects.get(username='admin')
    print(f"\n✓ Found user: {admin_user.username}")
    print(f"  Email: {admin_user.email}")
    print(f"  Current status:")
    print(f"    - is_staff: {admin_user.is_staff}")
    print(f"    - is_superuser: {admin_user.is_superuser}")
    print(f"    - is_active: {admin_user.is_active}")
    
    # Make admin a proper superuser
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.save()
    
    print("\n" + "=" * 70)
    print("✅ ADMIN PERMISSIONS UPDATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nNew status:")
    print(f"  - is_staff: {admin_user.is_staff} ✓")
    print(f"  - is_superuser: {admin_user.is_superuser} ✓")
    print(f"  - is_active: {admin_user.is_active} ✓")
    
    print("\n" + "=" * 70)
    print("NOW YOU CAN ACCESS ADMIN PANEL:")
    print("=" * 70)
    print("\n1. Go to: http://localhost:8000/admin")
    print(f"2. Username: {admin_user.username}")
    print("3. Password: (your password)")
    print("\n✅ You will now see the full admin dashboard!")
    
except User.DoesNotExist:
    print("\n❌ ERROR: Admin user not found!")
    print("\nCreating new admin user...")
    
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    
    print("\n✅ NEW ADMIN USER CREATED!")
    print("=" * 70)
    print(f"Username: admin")
    print(f"Password: admin123")
    print(f"Email: admin@example.com")
    print("\n⚠️ PLEASE CHANGE THE PASSWORD AFTER FIRST LOGIN!")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("DONE!")
print("=" * 70)
