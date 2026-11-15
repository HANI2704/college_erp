# faculty/forms.py

from django import forms
from .models import Staff, Notification, LeaveRequest, Feedback


class StaffForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=False,
        help_text="Leave blank to keep existing password."
    )

    class Meta:
        model = Staff
        fields = [
            'staff_id', 'name', 'email', 'mobile', 'gender', 'dob',
            'image', 'role', 'department', 'qualification',
            'experience', 'address', 'joining_date', 'is_active',
        ]
        widgets = {
            'staff_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'target', 'department']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'target': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'from_date', 'to_date', 'reason', 'document']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['faculty', 'subject_text', 'message']
        widgets = {
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'subject_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class FeedbackReplyForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['reply']
        widgets = {
            'reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your reply...'}),
        }
