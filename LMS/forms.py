# LMS/forms.py

from django import forms
from .models import Subject, Assignment, AssignmentSubmission, Notes, Quiz, QuizQuestion, Lesson, Unit


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name', 'subject_code', 'course', 'department', 'semester', 'description']
        widgets = {
            'subject_id': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Semester 1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'file', 'due_date', 'total_marks', 'status']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)
        if staff:
            self.fields['subject'].queryset = Subject.objects.filter(faculty=staff)


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'notes']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['subject', 'title', 'description', 'file', 'unit']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)
        if staff:
            self.fields['subject'].queryset = Subject.objects.filter(faculty=staff)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['subject', 'title', 'description', 'total_marks', 'duration_minutes', 'start_time', 'end_time']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff', None)
        super().__init__(*args, **kwargs)
        if staff:
            self.fields['subject'].queryset = Subject.objects.filter(faculty=staff)


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'marks']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'correct_option': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['subject', 'title', 'description', 'order']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['unit', 'title', 'content', 'file', 'video_url', 'order']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
