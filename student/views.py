# student/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg

from account.models import Student
from LMS.models import (
    Assignment, AssignmentSubmission, Notes, Quiz, QuizAttempt,
    Subject, Lesson, Unit, QuizQuestion
)
from LMS.forms import AssignmentSubmissionForm
from ERP.models import Attendance, StudentResult, Timetable, Circular, Event, OldExamPaper
from faculty.models import Notification, LeaveRequest, Feedback
from faculty.forms import LeaveRequestForm, FeedbackForm
from account.forms import StudentUpdateForm


# ─────────────────────────────────────────
# Decorator
# ─────────────────────────────────────────

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            messages.warning(request, "Please log in to continue.")
            return redirect('login')
        try:
            request.student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            request.session.flush()
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_student(request):
    student_id = request.session.get('student_id')
    if student_id:
        try:
            return Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            pass
    return None


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@student_required
def student_dashboard(request):
    student = request.student
    today = timezone.now()

    # Upcoming assignments
    upcoming_assignments = Assignment.objects.filter(
        status='active', due_date__gte=today
    ).select_related('subject').order_by('due_date')[:5]

    # Submitted assignment IDs
    submitted_ids = AssignmentSubmission.objects.filter(
        student=student
    ).values_list('assignment_id', flat=True)

    # Attendance summary
    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(student=student, status=True).count()
    attendance_pct = round((present_classes / total_classes * 100), 1) if total_classes > 0 else 0

    # Recent results
    recent_results = StudentResult.objects.filter(
        student=student
    ).select_related('subject').order_by('-created_at')[:5]

    # Circulars
    recent_circulars = Circular.objects.filter(
        Q(target_audience='students') | Q(target_audience='both')
    ).order_by('-is_pinned', '-publish_date')[:5]

    # Notifications
    notifications = Notification.objects.filter(
        Q(target='students') | Q(target='all'), is_active=True
    ).order_by('-created_at')[:5]

    # Upcoming events
    upcoming_events = Event.objects.filter(
        start_date__gte=today, is_active=True
    ).order_by('start_date')[:3]

    # Pending leave requests
    pending_leave = LeaveRequest.objects.filter(student=student, status='pending').count()

    context = {
        'student': student,
        'upcoming_assignments': upcoming_assignments,
        'submitted_ids': list(submitted_ids),
        'total_classes': total_classes,
        'present_classes': present_classes,
        'attendance_pct': attendance_pct,
        'recent_results': recent_results,
        'recent_circulars': recent_circulars,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
        'pending_leave': pending_leave,
    }
    return render(request, 'student/dashboard.html', context)


# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────

@student_required
def student_profile(request):
    student = request.student
    return render(request, 'student/profile.html', {'student': student})


@student_required
def edit_profile(request):
    student = request.student
    form = StudentUpdateForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('student_profile')
    return render(request, 'student/edit_profile.html', {'form': form, 'student': student})


# ─────────────────────────────────────────
# ASSIGNMENTS
# ─────────────────────────────────────────

@student_required
def student_assignments(request):
    student = request.student
    today = timezone.now()

    assignments = Assignment.objects.filter(status='active').select_related('subject', 'created_by').order_by('due_date')
    submitted_map = {
        s.assignment_id: s
        for s in AssignmentSubmission.objects.filter(student=student)
    }

    assignment_data = []
    for a in assignments:
        submission = submitted_map.get(a.id)
        assignment_data.append({
            'assignment': a,
            'submission': submission,
            'is_overdue': today > a.due_date,
            'can_submit': not submission and today <= a.due_date,
        })

    return render(request, 'student/assignments.html', {
        'assignment_data': assignment_data,
        'student': student,
    })


@student_required
def submit_assignment(request, pk):
    student = request.student
    assignment = get_object_or_404(Assignment, pk=pk, status='active')

    if AssignmentSubmission.objects.filter(assignment=assignment, student=student).exists():
        messages.warning(request, "You have already submitted this assignment.")
        return redirect('student_assignments')

    form = AssignmentSubmissionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.assignment = assignment
        submission.student = student
        if timezone.now() > assignment.due_date:
            submission.status = 'late'
        submission.save()
        messages.success(request, f"Assignment '{assignment.title}' submitted successfully!")
        return redirect('student_assignments')

    return render(request, 'student/submit_assignment.html', {
        'form': form, 'assignment': assignment, 'student': student
    })


@student_required
def view_submission(request, pk):
    student = request.student
    submission = get_object_or_404(AssignmentSubmission, pk=pk, student=student)
    return render(request, 'student/view_submission.html', {
        'submission': submission, 'student': student
    })


# ─────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────

@student_required
def student_results(request):
    student = request.student
    results = StudentResult.objects.filter(
        student=student
    ).select_related('subject').order_by('-created_at')

    # Group by subject
    subjects_data = {}
    for result in results:
        key = result.subject.subject_name
        if key not in subjects_data:
            subjects_data[key] = []
        subjects_data[key].append(result)

    avg_percentage = None
    if results.exists():
        total_pct = sum(r.percentage for r in results)
        avg_percentage = round(total_pct / results.count(), 2)

    return render(request, 'student/results.html', {
        'results': results,
        'subjects_data': subjects_data,
        'avg_percentage': avg_percentage,
        'student': student,
    })


# ─────────────────────────────────────────
# ATTENDANCE
# ─────────────────────────────────────────

@student_required
def student_attendance(request):
    student = request.student
    subjects = Subject.objects.all()
    attendance_data = []

    for subject in subjects:
        records = Attendance.objects.filter(student=student, subject=subject)
        total = records.count()
        if total == 0:
            continue
        present = records.filter(status=True).count()
        pct = round((present / total) * 100, 1)
        attendance_data.append({
            'subject': subject,
            'total': total,
            'present': present,
            'absent': total - present,
            'percentage': pct,
            'status': 'good' if pct >= 75 else 'low',
        })

    total_all = Attendance.objects.filter(student=student).count()
    present_all = Attendance.objects.filter(student=student, status=True).count()
    overall_pct = round((present_all / total_all * 100), 1) if total_all > 0 else 0

    recent = Attendance.objects.filter(student=student).select_related('subject').order_by('-date')[:20]

    return render(request, 'student/attendance.html', {
        'attendance_data': attendance_data,
        'overall_pct': overall_pct,
        'total_all': total_all,
        'present_all': present_all,
        'recent': recent,
        'student': student,
    })


# ─────────────────────────────────────────
# NOTES
# ─────────────────────────────────────────

@student_required
def student_notes(request):
    student = request.student
    notes = Notes.objects.filter(is_active=True).select_related('subject', 'uploaded_by').order_by('-created_at')
    subjects = Subject.objects.all()

    selected_subject = request.GET.get('subject')
    if selected_subject:
        notes = notes.filter(subject_id=selected_subject)

    return render(request, 'student/notes.html', {
        'notes': notes, 'subjects': subjects,
        'selected_subject': selected_subject, 'student': student,
    })


# ─────────────────────────────────────────
# LESSONS
# ─────────────────────────────────────────

@student_required
def student_lessons(request):
    student = request.student
    subjects = Subject.objects.all()
    units = Unit.objects.select_related('subject').prefetch_related('lessons').all()
    return render(request, 'student/lessons.html', {
        'units': units, 'subjects': subjects, 'student': student
    })


# ─────────────────────────────────────────
# QUIZZES
# ─────────────────────────────────────────

@student_required
def student_quizzes(request):
    student = request.student
    now = timezone.now()
    quizzes = Quiz.objects.filter(is_active=True).select_related('subject').order_by('-start_time')
    attempted_ids = QuizAttempt.objects.filter(
        student=student, is_completed=True
    ).values_list('quiz_id', flat=True)

    quiz_data = []
    for quiz in quizzes:
        attempt = QuizAttempt.objects.filter(quiz=quiz, student=student).first()
        quiz_data.append({
            'quiz': quiz,
            'attempt': attempt,
            'can_attempt': not attempt and quiz.start_time <= now <= quiz.end_time,
            'is_upcoming': quiz.start_time > now,
        })

    return render(request, 'student/quizzes.html', {
        'quiz_data': quiz_data, 'student': student
    })


@student_required
def attempt_quiz(request, pk):
    student = request.student
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    now = timezone.now()

    if now < quiz.start_time or now > quiz.end_time:
        messages.error(request, "This quiz is not available right now.")
        return redirect('student_quizzes')

    if QuizAttempt.objects.filter(quiz=quiz, student=student, is_completed=True).exists():
        messages.warning(request, "You have already attempted this quiz.")
        return redirect('student_quizzes')

    questions = quiz.questions.all().order_by('order')

    if request.method == 'POST':
        score = 0
        for question in questions:
            answer = request.POST.get(f'q_{question.id}')
            if answer and answer.upper() == question.correct_option:
                score += question.marks

        QuizAttempt.objects.update_or_create(
            quiz=quiz, student=student,
            defaults={
                'score': score,
                'total_questions': questions.count(),
                'is_completed': True,
                'completed_at': now,
            }
        )
        messages.success(request, f"Quiz submitted! Your score: {score}/{quiz.total_marks}")
        return redirect('student_quizzes')

    return render(request, 'student/attempt_quiz.html', {
        'quiz': quiz, 'questions': questions, 'student': student
    })


# ─────────────────────────────────────────
# CIRCULARS
# ─────────────────────────────────────────

@student_required
def student_circulars(request):
    student = request.student
    circulars = Circular.objects.filter(
        Q(target_audience='students') | Q(target_audience='both')
    ).order_by('-is_pinned', '-publish_date')
    return render(request, 'student/circulars.html', {'circulars': circulars, 'student': student})


# ─────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────

@student_required
def student_events(request):
    student = request.student
    now = timezone.now()
    upcoming_events = Event.objects.filter(start_date__gte=now, is_active=True).order_by('start_date')
    past_events = Event.objects.filter(end_date__lt=now).order_by('-end_date')[:10]
    return render(request, 'student/events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'student': student,
    })


# ─────────────────────────────────────────
# TIMETABLE
# ─────────────────────────────────────────

@student_required
def student_timetable(request):
    student = request.student
    timetable = Timetable.objects.filter(
        class_name__icontains=student.student_class
    ).select_related('time_slot').order_by('day', 'time_slot__start_time')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: list(timetable.filter(day=day)) for day in days}

    return render(request, 'student/timetable.html', {
        'timetable_by_day': timetable_by_day,
        'days': days,
        'student': student,
    })


# ─────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────

@student_required
def student_notifications(request):
    student = request.student
    notifications = Notification.objects.filter(
        Q(target='students') | Q(target='all'), is_active=True
    ).select_related('created_by').order_by('-created_at')
    return render(request, 'student/notifications.html', {
        'notifications': notifications, 'student': student
    })


# ─────────────────────────────────────────
# LEAVE REQUEST
# ─────────────────────────────────────────

@student_required
def student_leave(request):
    student = request.student
    form = LeaveRequestForm(request.POST or None, request.FILES or None)
    leave_requests = LeaveRequest.objects.filter(student=student).order_by('-created_at')

    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.student = student
        leave.save()
        messages.success(request, "Leave request submitted.")
        return redirect('student_leave')

    return render(request, 'student/leave.html', {
        'form': form, 'leave_requests': leave_requests, 'student': student
    })


# ─────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────

@student_required
def student_feedback(request):
    student = request.student
    form = FeedbackForm(request.POST or None)
    feedbacks = Feedback.objects.filter(student=student).order_by('-created_at')

    if request.method == 'POST' and form.is_valid():
        feedback = form.save(commit=False)
        feedback.student = student
        feedback.save()
        messages.success(request, "Feedback sent.")
        return redirect('student_feedback')

    return render(request, 'student/feedback.html', {
        'form': form, 'feedbacks': feedbacks, 'student': student
    })


# ─────────────────────────────────────────
# OLD EXAM PAPERS
# ─────────────────────────────────────────

@student_required
def student_exam_papers(request):
    student = request.student
    papers = OldExamPaper.objects.select_related('course', 'subject', 'season').order_by('-uploaded_at')
    return render(request, 'student/exam_papers.html', {'papers': papers, 'student': student})
