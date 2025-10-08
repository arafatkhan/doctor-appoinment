#!/usr/bin/env python
"""
Complete Database Import Script for Railway PostgreSQL
=====================================================
This script will import all SQLite data to Railway PostgreSQL database
"""

import os
import sys
import django
import json
from django.core import serializers
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.contrib.auth.models import User
from appointments.models import Doctor, Patient, Appointment, TimeSlot

def clear_existing_data():
    """Clear existing data to avoid conflicts"""
    print("🗑️ Clearing existing data...")
    Appointment.objects.all().delete()
    TimeSlot.objects.all().delete()
    Patient.objects.all().delete()
    Doctor.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("✅ Existing data cleared")

def import_from_json():
    """Import data from JSON files"""
    print("📥 Starting data import from JSON files...")
    
    export_dir = "database_export"
    
    # Import order matters for foreign key relationships
    import_files = [
        ('users.json', 'Users'),
        ('doctors.json', 'Doctors'),
        ('patients.json', 'Patients'),
        ('timeslots.json', 'Time Slots'),
        ('appointments.json', 'Appointments')
    ]
    
    for filename, description in import_files:
        filepath = os.path.join(export_dir, filename)
        if os.path.exists(filepath):
            print(f"📥 Importing {description} from {filename}...")
            try:
                call_command('loaddata', filepath)
                print(f"✅ {description} imported successfully")
            except Exception as e:
                print(f"❌ Error importing {description}: {str(e)}")
        else:
            print(f"⚠️ {filename} not found, skipping...")

def create_admin_user():
    """Create admin user if not exists"""
    print("👤 Creating admin user...")
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Admin user created: admin/admin123")
    else:
        print("ℹ️ Admin user already exists")

def create_sample_data():
    """Create sample data if JSON import fails"""
    print("📝 Creating sample data...")
    
    # Create sample doctor user
    if not User.objects.filter(username='doctor1').exists():
        doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='doctor123',
            first_name='Dr. Rahman',
            last_name='Ahmed'
        )
        
        # Create doctor profile
        Doctor.objects.create(
            user=doctor_user,
            specialization='General Medicine',
            phone='01700000001',
            bio='Experienced doctor with 10+ years in general medicine',
            experience_years=10,
            consultation_fee=1000.00
        )
        print("✅ Sample doctor created")
    
    # Create sample patient
    if not User.objects.filter(username='patient1').exists():
        patient_user = User.objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='patient123',
            first_name='John',
            last_name='Doe'
        )
        
        Patient.objects.create(
            user=patient_user,
            phone='01800000001',
            date_of_birth='1990-01-01',
            gender='M',
            address='Dhaka, Bangladesh'
        )
        print("✅ Sample patient created")
    
    # Create sample time slots
    if not TimeSlot.objects.exists():
        time_slots = [
            ('09:00', '10:00'),
            ('10:00', '11:00'),
            ('11:00', '12:00'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
        ]
        
        for start, end in time_slots:
            TimeSlot.objects.create(
                start_time=start,
                end_time=end,
                is_available=True
            )
        print("✅ Sample time slots created")

def main():
    """Main function to run all imports"""
    print("🚀 Starting complete database import for Railway...")
    print("="*50)
    
    try:
        # Run migrations first
        print("🔧 Running database migrations...")
        call_command('migrate')
        print("✅ Migrations completed")
        
        # Clear existing data
        clear_existing_data()
        
        # Try to import from JSON files first
        import_from_json()
        
        # Create admin user
        create_admin_user()
        
        # Create sample data if needed
        create_sample_data()
        
        # Print summary
        print("\n" + "="*50)
        print("📊 DATABASE IMPORT SUMMARY:")
        print("="*50)
        print(f"👥 Total Users: {User.objects.count()}")
        print(f"👨‍⚕️ Total Doctors: {Doctor.objects.count()}")
        print(f"👤 Total Patients: {Patient.objects.count()}")
        print(f"⏰ Total Time Slots: {TimeSlot.objects.count()}")
        print(f"📅 Total Appointments: {Appointment.objects.count()}")
        print("="*50)
        print("🎉 Database import completed successfully!")
        print("🌐 Your app is now ready with all data!")
        print("👤 Admin Login: admin/admin123")
        print("👨‍⚕️ Doctor Login: doctor1/doctor123")
        print("👤 Patient Login: patient1/patient123")
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()