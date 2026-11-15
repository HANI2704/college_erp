# LMS/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Subject, Assignment, Notes, Quiz, Unit, Lesson
from .forms import SubjectForm, UnitForm, LessonForm
from faculty.models import Staff
from account.models import Student


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            staff = request.user.staff_profile
            if staff.role != 'admin' and not request.user.is_superuser:
                messages.error(request, "Admin access required.")
                return redirect('login')
        except Staff.DoesNotExist:
            if not request.user.is_superuser:
                return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def faculty_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_staff(request):
    try:
        return request.user.staff_profile
    except (Staff.DoesNotExist, AttributeError):
        return None


# ─────────────────────────────────────────
# SUBJECT MANAGEMENT (Admin)
# ─────────────────────────────────────────

@admin_required
def admin_subjects(request):
    subjects = Subject.objects.select_related('faculty', 'department', 'course').all()
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject added.")
        return redirect('admin_subjects')
    return render(request, 'admin_panel/subjects.html', {'subjects': subjects, 'form': form})


@admin_required
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Subject updated.")
        return redirect('admin_subjects')
    return render(request, 'admin_panel/subject_form.html', {'form': form, 'subject': subject})


@admin_required
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, "Subject deleted.")
    return redirect('admin_subjects')


@admin_required
def assign_faculty_to_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    staff_list = Staff.objects.filter(is_active=True)
    if request.method == 'POST':
        staff_id = request.POST.get('faculty_id')
        subject.faculty = get_object_or_404(Staff, pk=staff_id) if staff_id else None
        subject.save()
        messages.success(request, f"Faculty assigned to {subject.subject_name}.")
        return redirect('admin_subjects')
    return render(request, 'admin_panel/assign_faculty.html', {
        'subject': subject, 'staff_list': staff_list
    })


# ─────────────────────────────────────────
# UNITS & LESSONS (Faculty)
# ─────────────────────────────────────────

@faculty_required
def faculty_units(request):
    staff = get_staff(request)
    subjects = Subject.objects.filter(faculty=staff)
    units = Unit.objects.filter(subject__in=subjects).select_related('subject')
    form = UnitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Unit added.")
        return redirect('faculty_units')
    return render(request, 'faculty/units.html', {'units': units, 'form': form, 'staff': staff})


@faculty_required
def faculty_lessons(request):
    staff = get_staff(request)
    subjects = Subject.objects.filter(faculty=staff)
    units = Unit.objects.filter(subject__in=subjects)
    lessons = Lesson.objects.filter(unit__in=units).select_related('unit__subject')
    form = LessonForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Lesson added.")
        return redirect('faculty_lessons')
    return render(request, 'faculty/lessons.html', {'lessons': lessons, 'form': form, 'staff': staff})


@faculty_required
def delete_lesson(request, pk):
    staff = get_staff(request)
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, "Lesson deleted.")
    return redirect('faculty_lessons')
