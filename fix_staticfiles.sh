#!/bin/bash
# Fix staticfiles directory for Railway deployment

echo "🔧 Creating staticfiles directory..."
mkdir -p /app/staticfiles

echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Static files setup completed!"