import requests
import jwt
import time
from datetime import datetime, timedelta
from django.conf import settings


class ZoomService:
    """Service class for Zoom API integration"""
    
    def __init__(self):
        self.account_id = settings.ZOOM_ACCOUNT_ID
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.base_url = "https://api.zoom.us/v2"
        self.token_url = "https://zoom.us/oauth/token"
    
    def get_access_token(self):
        """Get OAuth access token using Server-to-Server OAuth"""
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            import base64
            auth_bytes = auth_string.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'account_credentials',
                'account_id': self.account_id
            }
            
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
        
        except requests.exceptions.HTTPError as e:
            print(f"❌ Zoom API Error: {e}")
            if e.response is not None:
                print(f"Response: {e.response.text}")
            print("⚠️ Please check your Zoom credentials in .env file")
            return None
        except Exception as e:
            print(f"❌ Error getting Zoom access token: {str(e)}")
            return None
    
    def create_meeting(self, topic, start_time, duration=60, agenda=""):
        """
        Create a Zoom meeting
        
        Args:
            topic (str): Meeting topic/title
            start_time (datetime): Meeting start time
            duration (int): Meeting duration in minutes (default 60)
            agenda (str): Meeting agenda/description
        
        Returns:
            dict: Meeting details including join URL, meeting ID, password
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Format start time for Zoom API (ISO 8601)
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            meeting_data = {
                "topic": topic,
                "type": 2,  # Scheduled meeting
                "start_time": start_time_str,
                "duration": duration,
                "timezone": "Asia/Dhaka",
                "agenda": agenda,
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "join_before_host": False,
                    "mute_upon_entry": True,
                    "watermark": False,
                    "audio": "both",
                    "auto_recording": "none",
                    "waiting_room": True,
                    "approval_type": 2  # No registration required
                }
            }
            
            # Get user ID (using 'me' for the authenticated user)
            url = f"{self.base_url}/users/me/meetings"
            
            response = requests.post(url, headers=headers, json=meeting_data)
            response.raise_for_status()
            
            meeting_info = response.json()
            
            return {
                'meeting_id': meeting_info.get('id'),
                'join_url': meeting_info.get('join_url'),
                'start_url': meeting_info.get('start_url'),
                'password': meeting_info.get('password'),
                'topic': meeting_info.get('topic'),
                'start_time': meeting_info.get('start_time'),
                'duration': meeting_info.get('duration')
            }
        
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error creating meeting: {e}")
            print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error creating meeting: {str(e)}")
            return None
    
    def get_meeting(self, meeting_id):
        """Get meeting details by meeting ID"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            url = f"{self.base_url}/meetings/{meeting_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"Error getting meeting: {str(e)}")
            return None
    
    def delete_meeting(self, meeting_id):
        """Delete a scheduled meeting"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            url = f"{self.base_url}/meetings/{meeting_id}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            return True
        
        except Exception as e:
            print(f"Error deleting meeting: {str(e)}")
            return False
    
    def update_meeting(self, meeting_id, topic=None, start_time=None, duration=None, agenda=None):
        """Update an existing meeting"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            update_data = {}
            if topic:
                update_data['topic'] = topic
            if start_time:
                update_data['start_time'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            if duration:
                update_data['duration'] = duration
            if agenda:
                update_data['agenda'] = agenda
            
            url = f"{self.base_url}/meetings/{meeting_id}"
            response = requests.patch(url, headers=headers, json=update_data)
            response.raise_for_status()
            
            return True
        
        except Exception as e:
            print(f"Error updating meeting: {str(e)}")
            return False


# Helper function to create meeting for appointment
def create_appointment_meeting(appointment):
    """
    Create a Zoom meeting for an appointment
    
    Args:
        appointment: Appointment model instance
    
    Returns:
        dict: Meeting details or None if failed
    """
    try:
        zoom_service = ZoomService()
        
        # Combine date and time for meeting
        from datetime import datetime
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )
        
        # Create meeting topic
        topic = f"Consultation: {appointment.patient.user.get_full_name()} with Dr. {appointment.doctor.name}"
        agenda = f"Reason: {appointment.reason}"
        
        # Create meeting (default 60 minutes duration)
        meeting_info = zoom_service.create_meeting(
            topic=topic,
            start_time=appointment_datetime,
            duration=60,
            agenda=agenda
        )
        
        if meeting_info:
            # Save meeting details to appointment
            appointment.zoom_meeting_id = meeting_info.get('meeting_id')
            appointment.zoom_join_url = meeting_info.get('join_url')
            appointment.zoom_start_url = meeting_info.get('start_url')
            appointment.zoom_password = meeting_info.get('password')
            appointment.save()
            print(f"✅ Zoom meeting created for appointment #{appointment.id}")
        
        return meeting_info
    
    except Exception as e:
        print(f"❌ Error creating Zoom meeting for appointment #{appointment.id}: {str(e)}")
        return None
