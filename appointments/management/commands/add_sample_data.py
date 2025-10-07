from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Doctor, Patient
from datetime import date


class Command(BaseCommand):
    help = 'Add sample doctors and patients to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding doctors and patients...')
        
        # Add 5 Doctors
        doctors_data = [
            {
                'name': 'Ahmed Hossain',
                'specialization': 'General Physician',
                'email': 'ahmed.hossain@hospital.com',
                'phone': '01711111111',
                'consultation_fee': 500.00,
                'is_available': True
            },
            {
                'name': 'Fatima Rahman',
                'specialization': 'Cardiologist',
                'email': 'fatima.rahman@hospital.com',
                'phone': '01722222222',
                'consultation_fee': 800.00,
                'is_available': True
            },
            {
                'name': 'Kamal Uddin',
                'specialization': 'Pediatrician',
                'email': 'kamal.uddin@hospital.com',
                'phone': '01733333333',
                'consultation_fee': 600.00,
                'is_available': True
            },
            {
                'name': 'Nazia Sultana',
                'specialization': 'Dermatologist',
                'email': 'nazia.sultana@hospital.com',
                'phone': '01744444444',
                'consultation_fee': 700.00,
                'is_available': True
            },
            {
                'name': 'Rahul Das',
                'specialization': 'Orthopedic Surgeon',
                'email': 'rahul.das@hospital.com',
                'phone': '01755555555',
                'consultation_fee': 900.00,
                'is_available': True
            }
        ]
        
        for doctor_data in doctors_data:
            doctor, created = Doctor.objects.get_or_create(
                email=doctor_data['email'],
                defaults=doctor_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Added Dr. {doctor.name} - {doctor.specialization}'))
            else:
                self.stdout.write(self.style.WARNING(f'✗ Dr. {doctor.name} already exists'))
        
        # Add 5 Patients
        patients_data = [
            {
                'username': 'patient1',
                'password': 'patient123',
                'first_name': 'Rahim',
                'last_name': 'Mia',
                'email': 'rahim.mia@email.com',
                'phone': '01811111111',
                'address': 'Dhaka, Bangladesh',
                'date_of_birth': date(1990, 5, 15),
                'medical_history': 'No major medical issues'
            },
            {
                'username': 'patient2',
                'password': 'patient123',
                'first_name': 'Ayesha',
                'last_name': 'Begum',
                'email': 'ayesha.begum@email.com',
                'phone': '01822222222',
                'address': 'Chittagong, Bangladesh',
                'date_of_birth': date(1985, 8, 20),
                'medical_history': 'Diabetes Type 2'
            },
            {
                'username': 'patient3',
                'password': 'patient123',
                'first_name': 'Shakib',
                'last_name': 'Ahmed',
                'email': 'shakib.ahmed@email.com',
                'phone': '01833333333',
                'address': 'Sylhet, Bangladesh',
                'date_of_birth': date(1995, 3, 10),
                'medical_history': 'Asthma'
            },
            {
                'username': 'patient4',
                'password': 'patient123',
                'first_name': 'Sumaiya',
                'last_name': 'Islam',
                'email': 'sumaiya.islam@email.com',
                'phone': '01844444444',
                'address': 'Rajshahi, Bangladesh',
                'date_of_birth': date(1988, 11, 25),
                'medical_history': 'High blood pressure'
            },
            {
                'username': 'patient5',
                'password': 'patient123',
                'first_name': 'Tanvir',
                'last_name': 'Hasan',
                'email': 'tanvir.hasan@email.com',
                'phone': '01855555555',
                'address': 'Khulna, Bangladesh',
                'date_of_birth': date(1992, 7, 8),
                'medical_history': 'No known allergies'
            }
        ]
        
        for patient_data in patients_data:
            try:
                user = User.objects.get(username=patient_data['username'])
                self.stdout.write(self.style.WARNING(f'✗ Patient {patient_data["first_name"]} {patient_data["last_name"]} already exists'))
            except User.DoesNotExist:
                # Create user
                user = User.objects.create_user(
                    username=patient_data['username'],
                    password=patient_data['password'],
                    first_name=patient_data['first_name'],
                    last_name=patient_data['last_name'],
                    email=patient_data['email']
                )
                
                # Create patient profile
                Patient.objects.create(
                    user=user,
                    phone=patient_data['phone'],
                    address=patient_data['address'],
                    date_of_birth=patient_data['date_of_birth'],
                    medical_history=patient_data['medical_history']
                )
                
                self.stdout.write(self.style.SUCCESS(f'✓ Added Patient {patient_data["first_name"]} {patient_data["last_name"]} (username: {patient_data["username"]})'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully added all doctors and patients!'))
        self.stdout.write(self.style.SUCCESS('\nPatient login credentials:'))
        self.stdout.write('Username: patient1, patient2, patient3, patient4, patient5')
        self.stdout.write('Password: patient123 (for all patients)')
