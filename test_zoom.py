"""
Test Zoom API Connection
Run this to check if Zoom credentials are working
"""

import os
import sys
import django

# Setup Django
sys.path.append('C:/Users/Dell/Desktop/pation-appoinment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from appointments.zoom_service import ZoomService
from datetime import datetime, timedelta

print("=" * 70)
print("TESTING ZOOM API CONNECTION")
print("=" * 70)

# Initialize Zoom Service
zoom = ZoomService()

print("\n1. Testing Access Token Generation...")
print("-" * 70)
token = zoom.get_access_token()

if token:
    print("✅ SUCCESS: Access token generated!")
    print(f"Token (first 20 chars): {token[:20]}...")
else:
    print("❌ FAILED: Could not generate access token!")
    print("Check your Zoom credentials in .env file:")
    print(f"  - ZOOM_ACCOUNT_ID: {zoom.account_id}")
    print(f"  - ZOOM_CLIENT_ID: {zoom.client_id}")
    print(f"  - ZOOM_CLIENT_SECRET: {'*' * 20}")
    sys.exit(1)

print("\n2. Testing Meeting Creation...")
print("-" * 70)

# Test meeting creation
test_time = datetime.now() + timedelta(days=1)
meeting_info = zoom.create_meeting(
    topic="Test Consultation Meeting",
    start_time=test_time,
    duration=30,
    agenda="This is a test meeting"
)

if meeting_info:
    print("✅ SUCCESS: Meeting created!")
    print(f"  Meeting ID: {meeting_info.get('meeting_id')}")
    print(f"  Join URL: {meeting_info.get('join_url')}")
    print(f"  Password: {meeting_info.get('password')}")
    print(f"  Topic: {meeting_info.get('topic')}")
    
    # Try to delete the test meeting
    print("\n3. Cleaning up test meeting...")
    print("-" * 70)
    if zoom.delete_meeting(meeting_info.get('meeting_id')):
        print("✅ Test meeting deleted successfully")
    else:
        print("⚠️ Could not delete test meeting (not critical)")
else:
    print("❌ FAILED: Could not create meeting!")
    print("\nPossible reasons:")
    print("  1. Zoom credentials expired or invalid")
    print("  2. Zoom account doesn't have meeting creation permissions")
    print("  3. API rate limit exceeded")
    print("  4. Network connectivity issue")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
