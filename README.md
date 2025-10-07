# Patient Appointment System

একটি complete অনলাইন appointment booking system যেখানে:
- **Patient** রা online এ appointment বুক করতে পারবে
- **Doctors** login করে তাদের patients manage করতে পারবে
- **Admin** সব কিছু control করতে পারবে
- SQLite database এ সব তথ্য সংরক্ষিত থাকবে
- Zoom integration দিয়ে virtual consultation
- bKash payment gateway integration (TEST MODE)

## ✨ Key Features

### For Patients:
- ✅ Registration & Login System
- ✅ Browse Available Doctors
- ✅ Book Appointments Online
- ✅ Online Payment (bKash TEST MODE)
- ✅ View Appointment History
- ✅ Join Video Consultations
- ✅ Manage Profile & Medical History

### For Doctors:
- ✅ **Dedicated Login System**
- ✅ **Personal Dashboard**
- ✅ **View All Their Appointments**
- ✅ **Manage Patient Information**
- ✅ **Start Zoom Meetings as Host**
- ✅ **Confirm/Complete Appointments**
- ✅ **View Patient Medical History**
- ✅ **Manage Schedule**

### For Admins:
- ✅ Full Admin Panel Access
- ✅ Manage Users, Doctors, Patients
- ✅ View All Appointments
- ✅ Manual Zoom Link Entry
- ✅ Payment Management
- ✅ Select Any Doctor Dashboard

## 🔐 User Types & Access

### 1. Patient Users
- Login → Patient Dashboard
- Can book appointments and make payments
- View their own appointment history

### 2. Doctor Users (NEW!)
- Login → Doctor Dashboard  
- Can manage their own appointments only
- View their own patients
- Start video consultations

### 3. Admin Users
- Login → Admin Panel
- Full system access
- Can view any doctor's dashboard

## Setup Instructions

### 1. Virtual Environment তৈরি করুন
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Dependencies Install করুন
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Setup করুন
`.env` file এ আপনার credentials দিন:
- Zoom API credentials (optional - manual entry available)
- bKash credentials (TEST MODE active - no real credentials needed)
- Email settings

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Sample Data Add করুন (Optional)
```bash
python manage.py add_sample_data
```

### 6. Doctor User Accounts তৈরি করুন
```bash
# All doctors
python manage.py create_doctor_user --all

# Specific doctor
python manage.py create_doctor_user --doctor-id=1
```

### 7. Server চালু করুন
```bash
python manage.py runserver
```

Access the application at: http://localhost:8000

## 🔐 Login Credentials

### Admin Access:
- URL: http://localhost:8000/admin
- Username: admin
- Password: (your admin password)

### Doctor Access (NEW!):
All doctors have default credentials:
- URL: http://localhost:8000/login
- Username: See DOCTOR_CREDENTIALS.txt
- Password: doctor123 (change after first login!)

Examples:
- Dr. Ahmed: ahmed.hossain / doctor123
- Dr. Fatima: fatima.rahman / doctor123
- Dr. Liton: liton / doctor123

### Patient Access:
- URL: http://localhost:8000/login
- Register as new patient or use existing credentials

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `DOCTOR_LOGIN_GUIDE.txt` | Complete guide for doctor login system |
| `DOCTOR_CREDENTIALS.txt` | Quick reference for all doctor usernames |
| `DOCTOR_DASHBOARD_GUIDE.txt` | How to use doctor dashboard |
| `QUICK_START.txt` | Quick start guide |
| `PAYMENT_TEST_MODE.txt` | Payment testing information |
| `ZOOM_QUICK_FIX.txt` | Zoom troubleshooting |

## 🎯 Quick Start Guide

### For Patients:
1. Go to http://localhost:8000
2. Register → Login
3. Browse Doctors
4. Book Appointment
5. Make Payment (TEST MODE)
6. Join Video Consultation

### For Doctors:
1. Go to http://localhost:8000/login
2. Login with your credentials
3. View Dashboard automatically
4. Check today's appointments
5. Manage patients
6. Start video consultations

### For Admins:
1. Go to http://localhost:8000/admin
2. Login with admin credentials
3. Manage all system data
4. Or select doctor dashboard to view

## bKash Integration (TEST MODE)

✅ **Currently Running in TEST MODE**
- No real credentials needed
- All payments are simulated
- Use any values for testing

To enable LIVE mode:
1. Visit https://developer.bka.sh/
2. Register for sandbox credentials
3. Get your App Key, Secret, Username, Password
4. Add them to `.env` file
5. Update `bkash_service.py`

## Zoom API Status

⚠️ **Current Status: Manual Entry Mode**
- API credentials need renewal
- Use admin panel to manually enter Zoom links
- See `ZOOM_QUICK_FIX.txt` for details

To fix:
1. Visit https://marketplace.zoom.us/develop/create
2. Create Server-to-Server OAuth app
3. Update credentials in `.env`
4. Run: `python test_zoom.py`

## Management Commands

```bash
# Create sample doctors and patients
python manage.py add_sample_data

# Create user accounts for all doctors
python manage.py create_doctor_user --all

# Create user for specific doctor
python manage.py create_doctor_user --doctor-id=1

# Create doctor with credentials
python manage.py create_doctor_user
```

## Project Structure
```
appointment_system/
├── appointments/          # Main app
│   ├── models.py         # Database models (Patient, Doctor, Appointment)
│   ├── views.py          # Views with doctor login support
│   ├── urls.py           # URL routing
│   ├── forms.py          # Forms
│   ├── admin.py          # Admin panel customization
│   ├── zoom_service.py   # Zoom integration
│   ├── bkash_service.py  # bKash payment (TEST MODE)
│   ├── templates/        # HTML templates
│   └── management/       # Management commands
├── static/               # CSS, JS, images
├── db.sqlite3            # SQLite database
├── .env                  # Environment variables
└── manage.py            # Django management
```

## Technologies Used
- **Backend:** Django 4.2.7
- **Database:** SQLite3
- **Frontend:** Bootstrap 5, jQuery, Font Awesome
- **Video:** Zoom API (Server-to-Server OAuth)
- **Payment:** bKash Payment Gateway (TEST MODE)
- **Python:** 3.13.2

## Features Summary

✅ Complete appointment booking system
✅ Three user types: Patient, Doctor, Admin
✅ Doctor login and dashboard system
✅ Patient management for doctors
✅ Video consultation via Zoom
✅ Payment integration (TEST MODE)
✅ Medical history tracking
✅ Email notifications (optional)
✅ Responsive design
✅ Admin panel for full control

## License
MIT
