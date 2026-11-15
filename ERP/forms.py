# ERP/forms.py

from django import forms
from .models import (
    Event, Circular, Timetable, TimeSlot, TransportRegistration,
    OldExamPaper, ExamSeason, Course, Attendance, StudentResult, Alumni
)
from account.models import Student
from LMS.models import Subject
from .models import ConstituentCollege

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name', 'venue', 'start_date', 'end_date', 'image', 'fees', 'description', 'is_active']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class CircularForm(forms.ModelForm):
    class Meta:
        model = Circular
        fields = ['title', 'description', 'attachment', 'target_audience', 'department',
                  'classroom', 'publish_date', 'expiry_date', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'classroom': forms.Select(attrs={'class': 'form-select'}),
            'publish_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['academic_year', 'class_name', 'semester', 'subject', 'teacher', 'room', 'day', 'time_slot']
        widgets = {
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.TextInput(attrs={'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        # fields = ['name', 'department','constituent_college', 'duration_years', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'constituent_college': forms.Select(attrs={'class':'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ConstituentCollegeForm(forms.ModelForm):
    class Meta:
        model = ConstituentCollege
        fields = '__all__'

        widgets = {
            'departments': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Enter departments line by line'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)
        if staff:
            self.fields['subject'].queryset = Subject.objects.filter(faculty=staff)


class StudentResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['student', 'subject', 'exam_type', 'marks_obtained', 'total_marks', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mid Sem, End Sem'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    # def __init__(self, *args, **kwargs):
    #     staff = kwargs.pop('staff', None)
    #     super().__init__(*args, **kwargs)
    #     if staff:
    #         self.fields['subject'].queryset = Subject.objects.filter(faculty=staff)

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)

        if staff:
            self.fields['subject'].queryset = Subject.objects.filter(
                faculty=staff
            )

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class TransportForm(forms.ModelForm):
    class Meta:
        model = TransportRegistration
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'transport_office': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pickup_point': forms.TextInput(attrs={'class': 'form-control'}),
            'transportation_mode': forms.Select(attrs={'class': 'form-select'}),
        }


class OldExamPaperForm(forms.ModelForm):
    class Meta:
        model = OldExamPaper
        fields = ['course', 'subject', 'season', 'branch', 'file']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'season': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ExamSeasonForm(forms.ModelForm):
    class Meta:
        model = ExamSeason
        fields = ['name', 'year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Summer, Winter'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AlumniForm(forms.ModelForm):
    class Meta:
        model = Alumni
        fields = '__all__'

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'batch': forms.TextInput(attrs={'class': 'form-control'}),

            # ✅ Dropdowns
            'constituent_college': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),

            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }