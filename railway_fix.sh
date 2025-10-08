#!/bin/bash
# Railway Deployment Fix Script
# This script runs during Railway deployment to fix Bad Request (400) errors

echo "🔄 Starting Railway deployment fixes..."

# Run migrations to create database tables
echo "📊 Running database migrations..."
python manage.py migrate --run-syncdb

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('✅ Admin user already exists')
"

# Import sample data if database is empty
echo "📥 Importing database export if available..."
if [ -f "database_export/import_to_postgresql.py" ]; then
    python database_export/import_to_postgresql.py
    echo "✅ Database import completed"
else
    echo "⚠️ No database export found, creating sample data..."
    python manage.py shell -c "
from appointments.models import Doctor, TimeSlot
from django.contrib.auth.models import User
import datetime

# Create a sample doctor if none exists
if not Doctor.objects.exists():
    user = User.objects.create_user('doctor1', 'doctor@test.com', 'password123')
    doctor = Doctor.objects.create(
        user=user,
        name='Dr. Sample Doctor',
        specialization='General Medicine',
        phone='01700000000',
        email='doctor@test.com',
        fee=500,
        bio='Sample doctor for testing'
    )
    
    # Create sample time slots
    times = ['09:00', '10:00', '11:00', '14:00', '15:00']
    for time_str in times:
        TimeSlot.objects.create(
            doctor=doctor,
            start_time=datetime.time(*map(int, time_str.split(':'))),
            is_available=True
        )
    
    print('✅ Sample doctor and time slots created')
"
fi

echo "🎉 Railway deployment fixes completed!"
echo "🌐 Your app should now be accessible at the Railway URL"
echo "👤 Admin login: admin/admin123"