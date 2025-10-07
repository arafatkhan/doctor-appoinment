"""
Management command to create user accounts for existing doctors
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Doctor


class Command(BaseCommand):
    help = 'Create user accounts for doctors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create user accounts for all doctors without user accounts',
        )
        parser.add_argument(
            '--doctor-id',
            type=int,
            help='Create user account for specific doctor by ID',
        )

    def handle(self, *args, **options):
        if options['all']:
            self.create_all_doctor_users()
        elif options['doctor_id']:
            self.create_doctor_user(options['doctor_id'])
        else:
            self.stdout.write(self.style.ERROR('Please specify --all or --doctor-id=<id>'))

    def create_all_doctor_users(self):
        """Create user accounts for all doctors without user accounts"""
        doctors_without_users = Doctor.objects.filter(user__isnull=True)
        
        if not doctors_without_users.exists():
            self.stdout.write(self.style.WARNING('All doctors already have user accounts!'))
            return
        
        self.stdout.write(f'Found {doctors_without_users.count()} doctors without user accounts\n')
        
        for doctor in doctors_without_users:
            self.create_user_for_doctor(doctor)

    def create_doctor_user(self, doctor_id):
        """Create user account for specific doctor"""
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            
            if doctor.user:
                self.stdout.write(self.style.WARNING(f'Dr. {doctor.name} already has a user account: {doctor.user.username}'))
                return
            
            self.create_user_for_doctor(doctor)
            
        except Doctor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Doctor with ID {doctor_id} not found!'))

    def create_user_for_doctor(self, doctor):
        """Create user account for a doctor"""
        # Generate username from doctor name
        username = self.generate_username(doctor.name)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=doctor.email,
            password='doctor123',  # Default password
            first_name=doctor.name.split()[0] if doctor.name else 'Doctor',
            last_name=' '.join(doctor.name.split()[1:]) if len(doctor.name.split()) > 1 else '',
        )
        
        # Link user to doctor
        doctor.user = user
        doctor.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Created user for Dr. {doctor.name}\n'
                f'  Username: {username}\n'
                f'  Password: doctor123\n'
                f'  Email: {doctor.email}\n'
            )
        )

    def generate_username(self, name):
        """Generate unique username from doctor name"""
        # Remove "Dr." prefix if present
        name = name.replace('Dr.', '').replace('Dr', '').strip()
        
        # Convert to lowercase and replace spaces with dots
        base_username = name.lower().replace(' ', '.')
        
        # Check if username already exists
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
