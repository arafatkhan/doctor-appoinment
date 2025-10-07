"""
Context processors for templates
"""
from appointments.models import Doctor

def user_type_processor(request):
    """
    Add user type information to template context
    """
    context = {
        'is_doctor': False,
        'is_patient': False,
        'doctor_profile': None,
    }
    
    if request.user.is_authenticated:
        # Check if user is a doctor
        try:
            if hasattr(request.user, 'doctor'):
                context['is_doctor'] = True
                context['doctor_profile'] = request.user.doctor
        except Doctor.DoesNotExist:
            pass
        
        # Check if user is a patient (not doctor and not admin)
        if not context['is_doctor'] and not request.user.is_staff:
            try:
                if hasattr(request.user, 'patient'):
                    context['is_patient'] = True
            except:
                pass
    
    return context
