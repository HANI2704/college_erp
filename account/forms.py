# account/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Student, Department, Session
from django.core.exceptions import ValidationError
from ERP.models import ConstituentCollege
import re

from datetime import date

# class StudentRegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
#     confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

#     class Meta:
#         model = Student
#         fields = [
#             'stu_id', 'name', 'branch', 'prnno', 'abcid', 'student_class',
#             'dob', 'image', 'std_mo', 'father_name', 'mobile_no_father',
#             'mother_name', 'mobile_no_mother', 'email', 'address',
#         ]
#         widgets = {
#             'stu_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'}),
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
#             'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch'}),
#             'prnno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PRN Number'}),
#             'abcid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC ID'}),
#             'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class (e.g. FY, SY, TY)'}),
#             'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#             'std_mo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Mobile'}),
#             'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Name"}),
#             'mobile_no_father': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's Mobile"}),
#             'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Name"}),
#             'mobile_no_mother': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mother's Mobile"}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         confirm = cleaned_data.get('confirm_password')
#         if password and confirm and password != confirm:
#             raise forms.ValidationError("Passwords do not match.")
#         return cleaned_data

class StudentRegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password'}),
        min_length=6
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Student
        fields = [
            'stu_id','name','constituent_college', 'branch','semester','prnno','abcid','student_class',
            'dob','image','std_mo','father_name','mobile_no_father',
            'mother_name','mobile_no_mother','email','address'
        ]

        widgets = {
            'stu_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'constituent_college': forms.Select(attrs={'class':'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'prnno': forms.TextInput(attrs={'class': 'form-control'}),
            'abcid': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control','type':'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'std_mo': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_no_father': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_no_mother': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control','rows':3}),
        }

    # Password Validation
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    # Student Mobile Validation
    def clean_std_mo(self):
        mobile = self.cleaned_data.get('std_mo')

        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter valid 10 digit mobile number")

        return mobile

    def std_mo(self):
        mobile = self.cleaned_data.get('std_mo')

        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter valid father's mobile number")

        return mobile
    # Father Mobile
    def clean_mobile_no_father(self):
        mobile = self.cleaned_data.get('mobile_no_father')

        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter valid father's mobile number")

        return mobile

    # Mother Mobile
    def clean_mobile_no_mother(self):
        mobile = self.cleaned_data.get('mobile_no_mother')

        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter valid mother's mobile number")

        return mobile

    # Email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Student.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")

        return email

    # DOB validation (minimum age 15)
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 15:
            raise ValidationError("Student must be at least 15 years old")

        return dob

    # Image size validation
    def clean_image(self):
        image = self.cleaned_data.get('image')

        if image:
            if image.size > 2*1024*1024:
                raise ValidationError("Image must be less than 2MB")

        return image
    
# class StudentUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = [
#             'name', 'branch', 'student_class', 'dob', 'image',
#             'std_mo', 'father_name', 'mobile_no_father',
#             'mother_name', 'mobile_no_mother', 'address',
#         ]
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'branch': forms.TextInput(attrs={'class': 'form-control'}),
#             'student_class': forms.TextInput(attrs={'class': 'form-control'}),
#             'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#             'std_mo': forms.TextInput(attrs={'class': 'form-control'}),
#             'father_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'mobile_no_father': forms.TextInput(attrs={'class': 'form-control'}),
#             'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'mobile_no_mother': forms.TextInput(attrs={'class': 'form-control'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

class StudentUpdateForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'name','branch','semester','student_class','dob','image',
            'std_mo','father_name','mobile_no_father',
            'mother_name','mobile_no_mother','address'
        ]

        widgets = {

            'name': forms.TextInput(attrs={'class': 'form-control'}),

            'branch': forms.Select(attrs={'class': 'form-control'}),

            'semester': forms.Select(attrs={'class': 'form-control'}),

            'student_class': forms.TextInput(attrs={'class': 'form-control'}),

            'dob': forms.DateInput(attrs={'class': 'form-control','type':'date'}),

            'image': forms.FileInput(attrs={'class': 'form-control'}),

            'std_mo': forms.TextInput(attrs={'class': 'form-control'}),

            'father_name': forms.TextInput(attrs={'class': 'form-control'}),

            'mobile_no_father': forms.TextInput(attrs={'class': 'form-control'}),

            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),

            'mobile_no_mother': forms.TextInput(attrs={'class': 'form-control'}),

            'address': forms.Textarea(attrs={'class': 'form-control','rows':3}),
        }

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('faculty', 'Faculty'), ('admin', 'Admin')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = '__all__'

        widgets = {
            'department_id': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'constituent_college': forms.Select(attrs={
                'class': 'form-select',
                'id': 'college-select'
            }),
            'name': forms.Select(attrs={
                'class': 'form-select',
                'id': 'department-select'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'hod': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'department_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['constituent_college'].queryset = (
            ConstituentCollege.objects.all().order_by('name')
        )

        college_id = (
            self.data.get('constituent_college')
            or self.initial.get('constituent_college')
            or getattr(self.instance, 'constituent_college_id', None)
        )

        # Only accept numeric database IDs here.
        college = None

        if college_id and str(college_id).isdigit():
            college = ConstituentCollege.objects.filter(
                pk=int(college_id)
            ).first()

        department_choices = [('', 'Select Department')]

        if college:
            names = college.get_departments_list()

            for name in names:
                if name:
                    department_choices.append((name, name))

        # Preserve existing department name during editing.
        if self.instance and self.instance.pk:
            current_name = self.instance.name

            if current_name and current_name not in [
                value for value, label in department_choices
            ]:
                department_choices.append(
                    (current_name, current_name)
                )

        self.fields['name'].choices = department_choices

        
# class DepartmentForm(forms.ModelForm):

#     class Meta:
#         model = Department
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         seen = set()
#         unique_ids = []

#         for college in ConstituentCollege.objects.all():
#             if college.name not in seen:
#                 seen.add(college.name)
#                 unique_ids.append(college.id)

#         self.fields['constituent_college'].queryset = (
#             ConstituentCollege.objects.filter(id__in=unique_ids)
#         )

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_start', 'session_end']
        widgets = {
            'session_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'session_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
