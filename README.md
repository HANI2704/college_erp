# College ERP System — Django Full-Stack Project

A complete, dynamic College ERP system built with Django featuring three role-based dashboards: **Admin**, **Faculty**, and **Student**.

---

## Project Structure

```
college_erp/
├── college_erp/          # Main project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── account/              # Auth, Student model, Department, Session
├── faculty/              # Staff model, Notifications, Leave, Feedback
├── LMS/                  # Subject, Assignment, Notes, Quiz, Lesson
├── ERP/                  # Events, Circulars, Timetable, Attendance, Results
├── student/              # Student-facing views
├── templates/
│   ├── base/             # Shared layout
│   ├── account/          # Login, Register
│   ├── student/          # Student templates
│   ├── faculty/          # Faculty templates
│   └── admin_panel/      # Admin templates
├── static/               # CSS, JS, images
├── media/                # Uploaded files
├── manage.py
└── requirements.txt
```

---

## Quick Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations account
python manage.py makemigrations faculty
python manage.py makemigrations LMS
python manage.py makemigrations ERP
python manage.py makemigrations student
python manage.py migrate
```

### 3. Create superuser (Admin)
```bash
python manage.py createsuperuser
```

### 4. Create a Staff profile for the superuser (via Django shell)
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from faculty.models import Staff

user = User.objects.get(username='your_superuser_username')
Staff.objects.create(
    user=user,
    staff_id='ADM001',
    name='Admin User',
    email=user.email,
    mobile='9999999999',
    role='admin'
)
exit()
```

### 5. Start the server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## User Roles & Login

| Role    | Login Method                          | Redirect To        |
|---------|---------------------------------------|--------------------|
| Student | Register at `/register/`, then login  | Student Dashboard  |
| Faculty | Admin creates staff, then login       | Faculty Dashboard  |
| Admin   | Superuser or role=admin staff         | Admin Dashboard    |

---

## Key Features

### Admin
- Manage Students, Staff, Departments, Courses, Subjects
- Create Timetables, Sessions, Events, Circulars
- Upload Old Exam Papers
- Attendance reports
- Transport registrations
- Send notifications
- Alumni management

### Faculty
- Create/manage Assignments with file uploads
- Take & track Attendance
- Upload Results with auto-grade calculation
- Upload Notes and Lessons
- Create Quizzes with MCQ questions
- Approve/reject Leave Requests
- Reply to Student Feedback
- Send Notifications

### Student
- View Assignments & Submit files
- Check Attendance (subject-wise %)
- View Results with grades
- Download Notes and Lessons
- Attempt Quizzes (timed, auto-submit)
- View Timetable, Events, Circulars
- Submit Leave Requests
- Send Feedback to faculty
- Download Old Exam Papers

---

## Models Overview

```
account:  Student, Department, Session
faculty:  Staff, Notification, LeaveRequest, Feedback
LMS:      Subject, Unit, Lesson, Notes, Assignment, AssignmentSubmission, Quiz, QuizQuestion, QuizAttempt
ERP:      Course, Event, Circular, TimeSlot, Timetable, Attendance, AttendanceReport, StudentResult,
          TransportRegistration, ExamSeason, OldExamPaper, Alumni, ClassRoom
```

---

## URL Map

| Path                    | Description              |
|-------------------------|--------------------------|
| `/`                     | Login page               |
| `/register/`            | Student registration     |
| `/student/dashboard/`   | Student dashboard        |
| `/faculty/dashboard/`   | Faculty dashboard        |
| `/faculty/admin/dashboard/` | Admin dashboard      |
| `/admin-panel/events/`  | Admin events             |
| `/lms/subjects/`        | Admin subjects           |
| `/django-admin/`        | Django admin panel       |

---

## Media & Static Files

- **MEDIA_ROOT**: `media/` — uploaded files (photos, assignments, notes)
- **STATIC_ROOT**: `staticfiles/` — collected static files
- In `DEBUG=True` mode, Django serves media files automatically

---

## Grade System (Auto-calculated)

| Percentage | Grade |
|------------|-------|
| ≥ 90       | O     |
| ≥ 80       | A+    |
| ≥ 70       | A     |
| ≥ 60       | B+    |
| ≥ 55       | B     |
| ≥ 50       | C     |
| ≥ 40       | D     |
| < 40       | F     |
