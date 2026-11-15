# account/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date
from ERP.models import ConstituentCollege


# Mobile validator (Indian format)
mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10 digit mobile number"
)

# PRN validator
prn_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]{6,20}$',
    message="PRN must contain only letters and numbers (6-20 characters)"
)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    stu_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    constituent_college = models.ForeignKey(
    'ERP.ConstituentCollege',
    on_delete=models.PROTECT,
    related_name="students"

    # constituent_college = models.ForeignKey(
    #     'ERP.ConstituentCollege',
    #     on_delete=models.CASCADE,
    #     related_name="Student"   # ✅ FIXED
    )
    branch = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )
    SEMESTER_CHOICES = (
        (1, "Semester 1"),
        (2, "Semester 2"),
        (3, "Semester 3"),
        (4, "Semester 4"),
        (5, "Semester 5"),
        (6, "Semester 6"),
        (7, "Semester 7"),
        (8, "Semester 8"),
    )
    semester = models.IntegerField(
        choices=SEMESTER_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    prnno = models.CharField(
        max_length=20,
        unique=True,
        validators=[prn_validator]
    )
    abcid = models.CharField(max_length=20, unique=True)
    student_class = models.CharField(max_length=50)
    dob = models.DateField()
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)

    std_mo = models.CharField(max_length=10,validators=[mobile_validator])

    father_name = models.CharField(max_length=100)
    mobile_no_father = models.CharField(
        max_length=10,
        validators=[mobile_validator])

    mother_name = models.CharField(max_length=100)
    mobile_no_mother = models.CharField(
        max_length=10,
        validators=[mobile_validator]
    )

    email = models.EmailField(unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def clean(self):

        # DOB validation
        if self.dob >= date.today():
            raise ValidationError("Date of birth cannot be today or future.")

        # Minimum age validation (16 years)
        age = (date.today() - self.dob).days // 365
        if age < 16:
            raise ValidationError("Student must be at least 16 years old.")
        
    def __str__(self):
        return f"{self.name} ({self.stu_id})"

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default_avatar.png'


class Department(models.Model):

    department_id = models.CharField(max_length=20, unique=True)

    constituent_college = models.ForeignKey(
        ConstituentCollege,
        on_delete=models.CASCADE,
        related_name="departments"
    )

    name = models.CharField(max_length=100)

    code = models.CharField(max_length=20, unique=True)

    hod = models.ForeignKey(
        'faculty.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hod_department'
    )

    description = models.TextField(blank=True, null=True)

    department_image = models.ImageField(
        upload_to='department_images/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['constituent_college', 'name'],
                name='unique_department_per_college'
            ),
    ]

    def __str__(self):
        return self.name
    
class Session(models.Model):
    session_start = models.DateField()
    session_end = models.DateField()

    def __str__(self):
        return f"{self.session_start} - {self.session_end}"
