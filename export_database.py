#!/usr/bin/env python
"""
SQLite to PostgreSQL Data Migration Script
==========================================
This script will export your current SQLite data and help you import it to Railway PostgreSQL
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.core import serializers
from appointments.models import Doctor, Patient, Appointment, TimeSlot
from django.contrib.auth.models import User

def export_sqlite_data():
    """Export all data from SQLite database"""
    
    print("🔄 Starting SQLite data export...")
    
    # Create export directory
    export_dir = "database_export"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Export Users
    users = User.objects.all()
    if users:
        with open(f"{export_dir}/users.json", "w") as f:
            serializers.serialize("json", users, stream=f, indent=2)
        print(f"✅ Exported {users.count()} users")
    
    # Export Doctors
    doctors = Doctor.objects.all()
    if doctors:
        with open(f"{export_dir}/doctors.json", "w") as f:
            serializers.serialize("json", doctors, stream=f, indent=2)
        print(f"✅ Exported {doctors.count()} doctors")
    
    # Export Patients
    patients = Patient.objects.all()
    if patients:
        with open(f"{export_dir}/patients.json", "w") as f:
            serializers.serialize("json", patients, stream=f, indent=2)
        print(f"✅ Exported {patients.count()} patients")
    
    # Export TimeSlots
    timeslots = TimeSlot.objects.all()
    if timeslots:
        with open(f"{export_dir}/timeslots.json", "w") as f:
            serializers.serialize("json", timeslots, stream=f, indent=2)
        print(f"✅ Exported {timeslots.count()} time slots")
    
    # Export Appointments
    appointments = Appointment.objects.all()
    if appointments:
        with open(f"{export_dir}/appointments.json", "w") as f:
            serializers.serialize("json", appointments, stream=f, indent=2)
        print(f"✅ Exported {appointments.count()} appointments")
    
    # Create summary
    summary = {
        "export_date": datetime.now().isoformat(),
        "total_users": users.count(),
        "total_doctors": doctors.count(),
        "total_patients": patients.count(),
        "total_timeslots": timeslots.count(),
        "total_appointments": appointments.count(),
        "export_location": export_dir
    }
    
    with open(f"{export_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n🎉 Export completed successfully!")
    print(f"📁 Data exported to: {export_dir}/")
    print(f"📊 Summary:")
    print(f"   - Users: {summary['total_users']}")
    print(f"   - Doctors: {summary['total_doctors']}")
    print(f"   - Patients: {summary['total_patients']}")
    print(f"   - Time Slots: {summary['total_timeslots']}")
    print(f"   - Appointments: {summary['total_appointments']}")
    
    return summary

def create_import_script():
    """Create script to import data to PostgreSQL"""
    
    import_script = '''#!/usr/bin/env python
"""
PostgreSQL Data Import Script
============================
Run this script after deploying to Railway to import your SQLite data
"""

import os
import sys
import django
import json

# Setup Django with PostgreSQL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.core import serializers
from django.core.management import call_command

def import_data():
    """Import data to PostgreSQL database"""
    
    print("🔄 Starting PostgreSQL data import...")
    
    # Run migrations first
    print("🔧 Running migrations...")
    call_command('migrate')
    
    export_dir = "database_export"
    
    # Import in correct order (to handle foreign keys)
    import_order = [
        'users.json',
        'doctors.json', 
        'patients.json',
        'timeslots.json',
        'appointments.json'
    ]
    
    for filename in import_order:
        filepath = os.path.join(export_dir, filename)
        if os.path.exists(filepath):
            print(f"📥 Importing {filename}...")
            call_command('loaddata', filepath)
            print(f"✅ {filename} imported successfully")
        else:
            print(f"⚠️ {filename} not found, skipping...")
    
    print("🎉 Import completed successfully!")
    print("🔧 Now create a superuser for admin access:")
    print("   python manage.py createsuperuser")

if __name__ == "__main__":
    import_data()
'''
    
    with open("database_export/import_to_postgresql.py", "w") as f:
        f.write(import_script)
    
    print("📝 Created import script: database_export/import_to_postgresql.py")

if __name__ == "__main__":
    try:
        summary = export_sqlite_data()
        create_import_script()
        
        print("\n" + "="*50)
        print("🚀 NEXT STEPS FOR RAILWAY DEPLOYMENT:")
        print("="*50)
        print("1. Deploy your project to Railway")
        print("2. Add PostgreSQL service to your Railway project")
        print("3. Upload the 'database_export' folder to your Railway project")
        print("4. Run: python database_export/import_to_postgresql.py")
        print("5. Create superuser: python manage.py createsuperuser")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error during export: {str(e)}")
        print("Make sure you're in the correct directory and Django is properly configured")