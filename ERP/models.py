# ERP/models.py

import datetime
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings


def validate_dob(value):
    if value >= datetime.date.today():
        raise ValueError("Date of birth must be in the past.")


class Course(models.Model):
    name = models.CharField(max_length=255)
    constituent_college = models.ForeignKey(
        'ConstituentCollege',
        on_delete=models.CASCADE,
        related_name="Course"
    )
    department = models.ForeignKey(
        'account.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses'
    )
    duration_years = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'main_app_course'
        ordering = ['name']

    def __str__(self):
        return self.name
    
class ConstituentCollege(models.Model):
    name = models.CharField(max_length=200)
    department_names = models.TextField(blank=True, null=True)

    def get_departments_list(self):
        if self.department_names:
            return [
                dept.strip()
                for dept in self.department_names.splitlines()
                if dept.strip()
            ]
        return []

    def __str__(self):
        return self.name
    
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    image = models.ImageField(upload_to='event_images/')
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'faculty.Staff', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='events_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.event_name

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()


class Circular(models.Model):
    TARGET_CHOICES = (
        ('students', 'Students'),
        ('faculty', 'Faculty'),
        ('both', 'Both'),
    )

    DEPARTMENT_CHOICES = (
        ('cse', 'Computer Science'),
        ('it', 'Information Technology'),
        ('ece', 'Electronics'),
        ('mech', 'Mechanical'),
        ('civil', 'Civil'),
    )

    CLASSROOM_CHOICES = (
        ('fy', 'First Year'),
        ('sy', 'Second Year'),
        ('ty', 'Third Year'),
        ('final', 'Final Year'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='circulars/', blank=True, null=True)
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='both')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    classroom = models.CharField(max_length=20, choices=CLASSROOM_CHOICES, blank=True, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-publish_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        if self.expiry_date:
            return timezone.now() <= self.expiry_date
        return True


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class Timetable(models.Model):
    ACADEMIC_YEAR_CHOICES = (
        ('2025-2026', '2025-2026'),
        ('2026-2027', '2026-2027'),
    )

    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )

    academic_year = models.CharField(max_length=20, choices=ACADEMIC_YEAR_CHOICES)
    class_name = models.CharField(max_length=100)
    semester = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    teacher = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day', 'time_slot__start_time']

    def __str__(self):
        return f"{self.class_name} - {self.subject} ({self.day})"


class Attendance(models.Model):
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey('LMS.Subject', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.BooleanField(default=True)  # True = Present
    marked_by = models.ForeignKey(
        'faculty.Staff', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='attendance_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        status_str = "Present" if self.status else "Absent"
        return f"{self.student.name} - {self.subject.subject_name} - {self.date} ({status_str})"


class AttendanceReport(models.Model):
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='attendance_reports')
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.attendance.date}"


class StudentResult(models.Model):
    GRADE_CHOICES = (
        ('O', 'Outstanding'),
        ('A+', 'Excellent'),
        ('A', 'Very Good'),
        ('B+', 'Good'),
        ('B', 'Above Average'),
        ('C', 'Average'),
        ('D', 'Pass'),
        ('F', 'Fail'),
    )

    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(
    'LMS.Subject',
    on_delete=models.CASCADE,
    related_name='results'
)
    exam_type = models.CharField(max_length=50, default='Semester Exam')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.PositiveIntegerField(default=100)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        'faculty.Staff', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='results_uploaded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'subject', 'exam_type')

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}: {self.marks_obtained}/{self.total_marks}"

    @property
    def percentage(self):
        return round((self.marks_obtained / self.total_marks) * 100, 2)

    def save(self, *args, **kwargs):
        pct = self.percentage
        if pct >= 90:
            self.grade = 'O'
        elif pct >= 80:
            self.grade = 'A+'
        elif pct >= 70:
            self.grade = 'A'
        elif pct >= 60:
            self.grade = 'B+'
        elif pct >= 55:
            self.grade = 'B'
        elif pct >= 50:
            self.grade = 'C'
        elif pct >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)


class TransportRegistration(models.Model):
    TERM_CHOICES = (('Odd', 'Odd'), ('Even', 'Even'))
    SHIFT_CHOICES = (('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening'))
    MODE_CHOICES = (('Non AC', 'Non AC'), ('AC', 'AC'))

    student = models.ForeignKey(
        'account.Student', on_delete=models.CASCADE,
        null=True, blank=True, related_name='transport_registrations'
    )
    transport_office = models.CharField(max_length=200)
    registration_date = models.DateField()
    department = models.ForeignKey(
        'account.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transport_registrations'
    )
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    in_time = models.TimeField()
    out_time = models.TimeField()
    city = models.CharField(max_length=100)
    pickup_point = models.CharField(max_length=200)
    transportation_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        student_name = self.student.name if self.student else "Unknown"
        return f"{student_name} - {self.pickup_point} ({self.academic_year})"


class ExamSeason(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.year}"


class OldExamPaper(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='papers')
    subject = models.ForeignKey('LMS.Subject', on_delete=models.CASCADE)
    season = models.ForeignKey(ExamSeason, on_delete=models.CASCADE, related_name='papers')
    branch = models.CharField(max_length=100)
    file = models.FileField(upload_to='old_exam_papers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} - {self.season}"

class Alumni(models.Model):
    full_name = models.CharField(max_length=100)

    mobile_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{10}$',
                message='Mobile number must be exactly 10 digits.'
            )
        ]
    )

    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(validators=[validate_dob])

    profile_photo = models.ImageField(
        upload_to='alumni_photos/',
        blank=True,
        null=True
    )

    batch = models.CharField(max_length=20)

    constituent_college = models.ForeignKey(
        'ConstituentCollege',
        on_delete=models.CASCADE,
        related_name="alumni"   # ✅ FIXED
    )

    department = models.ForeignKey(
        'account.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alumni'   # ✅ FIXED
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alumni'   # ✅ FIXED
    )

    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.batch})"

class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey('account.Department', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
