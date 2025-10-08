#!/usr/bin/env python
"""
Railway Deployment Fix Script
=============================
This script fixes common Railway deployment issues and Bad Request (400) errors.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')

def fix_railway_deployment():
    """Fix Railway deployment issues"""
    
    print("🔄 Starting Railway deployment fixes...")
    
    try:
        # Setup Django
        django.setup()
        
        # Import models after Django setup
        from django.contrib.auth.models import User
        from appointments.models import Doctor, TimeSlot, Patient
        import datetime
        
        print("📊 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("📊 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # Create superuser if doesn't exist
        print("👤 Setting up admin user...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Admin user created: admin/admin123")
        else:
            print("✅ Admin user already exists")
        
        # Import data if export exists
        export_dir = "database_export"
        if os.path.exists(f"{export_dir}/import_to_postgresql.py"):
            print("📥 Importing database export...")
            exec(open(f"{export_dir}/import_to_postgresql.py").read())
            print("✅ Database import completed")
        else:
            # Create sample data if database is empty
            if not Doctor.objects.exists():
                print("⚠️ Creating sample data...")
                
                # Create sample doctor
                user = User.objects.create_user('doctor1', 'doctor@test.com', 'password123')
                doctor = Doctor.objects.create(
                    user=user,
                    name='Dr. Sample Doctor',
                    specialization='General Medicine',
                    phone='01700000000',
                    email='doctor@test.com',
                    fee=500,
                    bio='Sample doctor for testing',
                    experience_years=5
                )
                
                # Create sample time slots
                times = ['09:00', '10:00', '11:00', '14:00', '15:00']
                for time_str in times:
                    hour, minute = map(int, time_str.split(':'))
                    TimeSlot.objects.create(
                        doctor=doctor,
                        start_time=datetime.time(hour, minute),
                        is_available=True
                    )
                
                print("✅ Sample doctor and time slots created")
        
        print("🎉 Railway deployment fixes completed successfully!")
        print("🌐 Your app should now be accessible")
        print("👤 Admin login: admin/admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_railway_deployment()
    sys.exit(0 if success else 1)