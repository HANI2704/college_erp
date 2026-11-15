# faculty/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10 digit mobile number"
)
class Staff(models.Model):
    ROLE_CHOICES = (
         ('dean', 'Dean'),
        ('faculty', 'Faculty'),
        ('hod', 'Head of Department'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # mobile = models.CharField(max_length=15)
    mobile= models.CharField(
        max_length=10,
        validators=[mobile_validator])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='staff_images/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='faculty')
    department = models.ForeignKey(
        'account.Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='staff_members'
    )
    qualification = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff Members'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default_avatar.png'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_faculty(self):
        return self.role in ('faculty', 'hod')


class Notification(models.Model):
    TARGET_CHOICES = (
        ('all', 'All'),
        ('students', 'Students Only'),
        ('faculty', 'Faculty Only'),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='notifications_sent')
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    department = models.ForeignKey(
        'account.Department', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    LEAVE_TYPE_CHOICES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('medical', 'Medical Leave'),
        ('other', 'Other'),
    )

    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='leave_requests')
    faculty = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_approvals')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='casual')
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    document = models.FileField(upload_to='leave_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    faculty_remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.leave_type} ({self.status})"


class Feedback(models.Model):
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='feedbacks')
    faculty = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks_received')
    subject_text = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.student.name}"
