# faculty/views.py
import pandas as pd 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Avg, Q

from .models import Staff, Notification, LeaveRequest, Feedback
from .forms import StaffForm, NotificationForm, LeaveRequestForm, FeedbackReplyForm
from account.models import Student, Department
from LMS.models import Subject, Assignment, AssignmentSubmission, Notes, Quiz, Lesson
from LMS.forms import AssignmentForm, NotesForm, QuizForm, QuizQuestionForm
from ERP.models import Attendance, StudentResult, Timetable
from ERP.forms import AttendanceForm, StudentResultForm

import os
from django.conf import settings
from django.core.files import File

# ─────────────────────────────────────────
# Decorators
# ─────────────────────────────────────────

def faculty_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in.")
            return redirect('login')
        try:
            staff = request.user.staff_profile
            request.staff = staff
        except Staff.DoesNotExist:
            if request.user.is_superuser:
                request.staff = None
            else:
                messages.error(request, "Faculty access required.")
                return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            staff = request.user.staff_profile
            if staff.role != 'admin' and not request.user.is_superuser:
                messages.error(request, "Admin access required.")
                return redirect('login')
            request.staff = staff
        except Staff.DoesNotExist:
            if not request.user.is_superuser:
                messages.error(request, "Access denied.")
                return redirect('login')
            request.staff = None
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_staff(request):
    try:
        return request.user.staff_profile
    except (Staff.DoesNotExist, AttributeError):
        return None


# ─────────────────────────────────────────
# FACULTY DASHBOARD
# ─────────────────────────────────────────

@faculty_required
def faculty_dashboard(request):
    staff = get_staff(request)
    today = timezone.now().date()

    assignments_created = Assignment.objects.filter(created_by=staff).count() if staff else 0
    pending_submissions = AssignmentSubmission.objects.filter(
        assignment__created_by=staff, status='submitted'
    ).count() if staff else 0
    today_classes = Timetable.objects.filter(
        teacher=staff.name if staff else '', day=today.strftime('%A')
    ) if staff else []
    recent_submissions = AssignmentSubmission.objects.filter(
        assignment__created_by=staff
    ).select_related('student', 'assignment').order_by('-submitted_at')[:5] if staff else []
    subjects = Subject.objects.filter(faculty=staff) if staff else []
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    unread_feedbacks = Feedback.objects.filter(faculty=staff, reply__isnull=True).count() if staff else 0
    notifications = Notification.objects.filter(
        Q(target='faculty') | Q(target='all')
    ).order_by('-created_at')[:5]

    context = {
        'staff': staff,
        'assignments_created': assignments_created,
        'pending_submissions': pending_submissions,
        'today_classes': today_classes,
        'recent_submissions': recent_submissions,
        'subjects': subjects,
        'pending_leaves': pending_leaves,
        'unread_feedbacks': unread_feedbacks,
        'notifications': notifications,
        'today': today,
    }
    return render(request, 'faculty/dashboard.html', context)


# ─────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_faculty = Staff.objects.filter(role__in=['faculty', 'hod']).count()
    total_departments = Department.objects.count()
    total_subjects = Subject.objects.count()
    total_assignments = Assignment.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()

    recent_students = Student.objects.order_by('-created_at')[:5]
    recent_staff = Staff.objects.order_by('-created_at')[:5]

    from ERP.models import Event, Circular
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), is_active=True)[:3]
    recent_circulars = Circular.objects.order_by('-publish_date')[:5]

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_departments': total_departments,
        'total_subjects': total_subjects,
        'total_assignments': total_assignments,
        'pending_leaves': pending_leaves,
        'recent_students': recent_students,
        'recent_staff': recent_staff,
        'upcoming_events': upcoming_events,
        'recent_circulars': recent_circulars,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ─────────────────────────────────────────
# STAFF MANAGEMENT (Admin)
# ─────────────────────────────────────────

@admin_required
def admin_staff_list(request):
    staff_list = Staff.objects.select_related('department').all()
    return render(request, 'admin_panel/staff_list.html', {'staff_list': staff_list})


@admin_required
def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        staff = form.save(commit=False)
        password = form.cleaned_data.get('password') or staff.staff_id
        email = form.cleaned_data['email']
        username = email.split('@')[0]
        base = username
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"
            i += 1
        user = User.objects.create_user(
            username=username, email=email,
            password=password or 'changeme123',
            first_name=staff.name.split()[0] if staff.name else '',
        )
        if staff.role == 'admin':
            user.is_staff = True
            user.save()
        staff.user = user
        staff.save()
        messages.success(request, f"Staff member '{staff.name}' added successfully.")
        return redirect('admin_staff_list')
    return render(request, 'admin_panel/staff_form.html', {'form': form, 'action': 'Add'})


@admin_required
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    form = StaffForm(request.POST or None, request.FILES or None, instance=staff)
    if request.method == 'POST' and form.is_valid():
        staff = form.save(commit=False)
        password = form.cleaned_data.get('password')
        if password:
            staff.user.set_password(password)
            staff.user.save()
        staff.save()
        messages.success(request, "Staff updated successfully.")
        return redirect('admin_staff_list')
    return render(request, 'admin_panel/staff_form.html', {'form': form, 'action': 'Edit', 'staff': staff})


@admin_required
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        if staff.user:
            staff.user.delete()
        else:
            staff.delete()
        messages.success(request, "Staff deleted successfully.")
    return redirect('admin_staff_list')

@admin_required
def import_staff_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(excel_file)

            added_count = 0

            for _, row in df.iterrows():
                email = str(row.get('email')).strip()
                staff_id = str(row.get('staff_id')).strip()

                if Staff.objects.filter(email=email).exists():
                    continue

                username = email.split('@')[0]
                base = username
                i = 1

                while User.objects.filter(username=username).exists():
                    username = f"{base}{i}"
                    i += 1

                # ✅ Password = staff_id
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=staff_id
                )

                dept_name = str(row.get('department')).strip()
                department = Department.objects.filter(
                    name__iexact=dept_name
                ).first()

                staff = Staff.objects.create(
                    user=user,
                    staff_id=staff_id,
                    name=row.get('name'),
                    email=email,
                    mobile=str(row.get('mobile')),
                    gender=row.get('gender', 'male'),
                    dob=row.get('dob'),
                    role=row.get('role', 'faculty'),
                    department=department,
                    qualification=row.get('qualification', ''),
                    experience=row.get('experience', ''),
                    address=row.get('address', ''),
                    joining_date=row.get('joining_date'),
                )

                # ✅ Image from PC path
                image_path = str(row.get('image_path', '')).strip()

                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as img:
                        file_name = os.path.basename(image_path)
                        staff.image.save(
                            file_name,
                            File(img),
                            save=True
                        )

                added_count += 1

            messages.success(
                request,
                f"{added_count} staff imported successfully"
            )

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('admin_staff_list')

    return render(request, 'admin_panel/import_staff.html')
# ─────────────────────────────────────────
# STUDENT MANAGEMENT (Admin)
# ─────────────────────────────────────────

@admin_required
def admin_students(request):
    students = Student.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/students.html', {'students': students})


@admin_required
def admin_student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = StudentResult.objects.filter(student=student).select_related('subject')
    attendances = Attendance.objects.filter(student=student).select_related('subject')
    submissions = AssignmentSubmission.objects.filter(student=student).select_related('assignment')
    return render(request, 'admin_panel/student_detail.html', {
        'student': student, 'results': results,
        'attendances': attendances, 'submissions': submissions,
    })


@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        if student.user:
            student.user.delete()
        else:
            student.delete()
        messages.success(request, "Student deleted.")
    return redirect('admin_students')


# ─────────────────────────────────────────
# ASSIGNMENTS (Faculty)
# ─────────────────────────────────────────

@faculty_required
def faculty_assignments(request):
    staff = get_staff(request)
    assignments = Assignment.objects.filter(created_by=staff).select_related('subject').order_by('-created_at')
    return render(request, 'faculty/assignments.html', {'assignments': assignments, 'staff': staff})


@faculty_required
def create_assignment(request):
    staff = get_staff(request)
    form = AssignmentForm(request.POST or None, request.FILES or None, staff=staff)
    form.fields['subject'].queryset = Subject.objects.all()
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.created_by = staff
        assignment.save()
        messages.success(request, f"Assignment '{assignment.title}' created successfully.")
        return redirect('faculty_assignments')
    return render(request, 'faculty/assignment_form.html', {'form': form, 'action': 'Create'})


@faculty_required
def edit_assignment(request, pk):
    staff = get_staff(request)
    assignment = get_object_or_404(Assignment, pk=pk, created_by=staff)
    form = AssignmentForm(request.POST or None, request.FILES or None, instance=assignment, staff=staff)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Assignment updated.")
        return redirect('faculty_assignments')
    return render(request, 'faculty/assignment_form.html', {'form': form, 'action': 'Edit', 'assignment': assignment})


@faculty_required
def delete_assignment(request, pk):
    staff = get_staff(request)
    assignment = get_object_or_404(Assignment, pk=pk, created_by=staff)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Assignment deleted.")
    return redirect('faculty_assignments')


@faculty_required
def view_submissions(request, pk):
    staff = get_staff(request)
    assignment = get_object_or_404(Assignment, pk=pk, created_by=staff)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    return render(request, 'faculty/submissions.html', {
        'assignment': assignment, 'submissions': submissions, 'staff': staff
    })


@faculty_required
def grade_submission(request, pk):
    staff = get_staff(request)
    submission = get_object_or_404(AssignmentSubmission, pk=pk, assignment__created_by=staff)
    if request.method == 'POST':
        marks = request.POST.get('marks_obtained')
        feedback = request.POST.get('feedback', '')
        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = 'graded'
        submission.save()
        messages.success(request, f"Submission graded: {marks}/{submission.assignment.total_marks}")
        return redirect('view_submissions', pk=submission.assignment.pk)
    return render(request, 'faculty/grade_submission.html', {'submission': submission})


# ─────────────────────────────────────────
# ATTENDANCE (Faculty)
# ─────────────────────────────────────────

# faculty/views.py

@faculty_required
def faculty_attendance(request):
    staff = get_staff(request)

    print("Logged in staff:", staff)
    print("Subjects:", Subject.objects.filter(faculty=staff))

    # Only subjects assigned to logged-in faculty
    # subjects = Subject.objects.filter(faculty=staff)
    subjects = Subject.objects.all()

    context = {
        'subjects': subjects,
        'staff': staff,
        'selected_subject': None,
        'students': [],
        'date': '',
        'existing': {}
    }

    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        date_str = request.POST.get('date')

        # Validation
        if not subject_id or not date_str:
            messages.error(request, "Please select subject and date.")
            return render(request, 'faculty/attendance.html', context)

        # Get selected subject
        subject = get_object_or_404(
            Subject,
            id=subject_id
        )

        # Get students of same department/branch
        students = Student.objects.filter(
            branch=subject.department
        )

        # Save attendance
        if request.POST.get('mark_attendance') == '1':
            for student in students:
                status = request.POST.get(
                    f'status_{student.id}'
                ) == 'present'

                Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=date_str,
                    defaults={
                        'status': status,
                        'marked_by': staff
                    }
                )

            messages.success(request, "Attendance saved successfully.")
            return redirect('faculty_attendance')

        # Load student list
        context['selected_subject'] = subject
        context['students'] = students
        context['date'] = date_str
        context['existing'] = {
            attendance.student_id: attendance.status
            for attendance in Attendance.objects.filter(
                subject=subject,
                date=date_str
            )
        }

    return render(request, 'faculty/attendance.html', context)

@faculty_required
def attendance_report(request):
    staff = get_staff(request)
    subjects = Subject.objects.all()
    report_data = []
    selected_subject = None

    if request.GET.get('subject_id'):
        selected_subject = get_object_or_404(Subject, pk=request.GET['subject_id'])
        students = Student.objects.all()
        for student in students:
            total = Attendance.objects.filter(student=student, subject=selected_subject).count()
            present = Attendance.objects.filter(student=student, subject=selected_subject, status=True).count()
            pct = round((present / total * 100), 1) if total > 0 else 0
            report_data.append({'student': student, 'total': total, 'present': present, 'percentage': pct})

    return render(request, 'faculty/attendance_report.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'report_data': report_data,
        'staff': staff,
    })


# ─────────────────────────────────────────
# RESULTS (Faculty)
# ─────────────────────────────────────────

# @faculty_required
# def faculty_results(request):
#     staff = get_staff(request)
#     subjects = Subject.objects.filter(faculty=staff)
#     results = StudentResult.objects.filter(uploaded_by=staff).select_related('student', 'subject').order_by('-created_at')
#     return render(request, 'faculty/results.html', {'results': results, 'subjects': subjects, 'staff': staff})

@faculty_required
def faculty_results(request):
    staff = get_staff(request)

    # subjects = Subject.objects.filter(faculty=staff)
    subjects = Subject.objects.all()
    
    results = StudentResult.objects.filter(
        subject__faculty=staff
    ).select_related(
        'student',
        'subject'
    ).order_by('-created_at')

    return render(request, 'faculty/results.html', {
        'results': results,
        'subjects': subjects,
        'staff': staff
    })

@faculty_required
def upload_result(request):
    staff = get_staff(request)
    form = StudentResultForm(request.POST or None, staff=staff)
    if request.method == 'POST' and form.is_valid():
        result = form.save(commit=False)
        result.uploaded_by = staff
        result.save()
        messages.success(request, "Result uploaded successfully.")
        return redirect('faculty_results')
    return render(request, 'faculty/result_form.html', {'form': form, 'staff': staff})


@faculty_required
def edit_result(request, pk):
    staff = get_staff(request)
    result = get_object_or_404(StudentResult, pk=pk, uploaded_by=staff)
    form = StudentResultForm(request.POST or None, instance=result, staff=staff)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Result updated.")
        return redirect('faculty_results')
    return render(request, 'faculty/result_form.html', {'form': form, 'result': result})


# ─────────────────────────────────────────
# NOTES (Faculty)
# ─────────────────────────────────────────

@faculty_required
def faculty_notes(request):
    staff = get_staff(request)
    notes = Notes.objects.filter(uploaded_by=staff).select_related('subject').order_by('-created_at')
    form = NotesForm(request.POST or None, request.FILES or None, staff=staff)
    form.fields['subject'].queryset = Subject.objects.all()
    if request.method == 'POST' and form.is_valid():
        note = form.save(commit=False)
        note.uploaded_by = staff
        note.save()
        messages.success(request, "Notes uploaded successfully.")
        return redirect('faculty_notes')
    return render(request, 'faculty/notes.html', {'notes': notes, 'form': form, 'staff': staff})


@faculty_required
def delete_note(request, pk):
    staff = get_staff(request)
    note = get_object_or_404(Notes, pk=pk, uploaded_by=staff)
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note deleted.")
    return redirect('faculty_notes')


# ─────────────────────────────────────────
# NOTIFICATIONS (Faculty / Admin)
# ─────────────────────────────────────────

@faculty_required
def faculty_notifications(request):
    staff = get_staff(request)
    form = NotificationForm(request.POST or None)
    notifications = Notification.objects.filter(created_by=staff).order_by('-created_at') if staff else []
    if request.method == 'POST' and form.is_valid():
        notif = form.save(commit=False)
        notif.created_by = staff
        notif.save()
        messages.success(request, "Notification sent.")
        return redirect('faculty_notifications')
    return render(request, 'faculty/notifications.html', {
        'form': form, 'notifications': notifications, 'staff': staff
    })


@admin_required
def admin_notifications(request):
    staff = get_staff(request)
    form = NotificationForm(request.POST or None)
    notifications = Notification.objects.all().select_related('created_by').order_by('-created_at')
    if request.method == 'POST' and form.is_valid():
        notif = form.save(commit=False)
        notif.created_by = staff
        notif.save()
        messages.success(request, "Notification sent.")
        return redirect('admin_notifications')
    return render(request, 'admin_panel/notifications.html', {
        'form': form, 'notifications': notifications
    })


# ─────────────────────────────────────────
# LEAVE REQUESTS
# ─────────────────────────────────────────

@faculty_required
def faculty_leave_requests(request):
    staff = get_staff(request)
    leave_requests = LeaveRequest.objects.filter(status='pending').select_related('student').order_by('-created_at')
    return render(request, 'faculty/leave_requests.html', {
        'leave_requests': leave_requests, 'staff': staff
    })


@faculty_required
def approve_leave(request, pk):
    staff = get_staff(request)
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        leave.status = 'approved' if action == 'approve' else 'rejected'
        leave.faculty = staff
        leave.faculty_remarks = remarks
        leave.save()
        messages.success(request, f"Leave request {leave.status}.")
    return redirect('faculty_leave_requests')


# ─────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────

@faculty_required
def faculty_feedback(request):
    staff = get_staff(request)
    feedbacks = Feedback.objects.filter(faculty=staff).select_related('student').order_by('-created_at')
    return render(request, 'faculty/feedback.html', {'feedbacks': feedbacks, 'staff': staff})


@faculty_required
def reply_feedback(request, pk):
    staff = get_staff(request)
    feedback = get_object_or_404(Feedback, pk=pk, faculty=staff)
    form = FeedbackReplyForm(request.POST or None, instance=feedback)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Reply sent.")
        return redirect('faculty_feedback')
    return render(request, 'faculty/reply_feedback.html', {'feedback': feedback, 'form': form})


# ─────────────────────────────────────────
# TIMETABLE (Faculty view)
# ─────────────────────────────────────────

@faculty_required
def faculty_timetable(request):
    staff = get_staff(request)
    timetable = Timetable.objects.filter(
        teacher=staff.name if staff else ''
    ).select_related('time_slot').order_by('day', 'time_slot__start_time')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: timetable.filter(day=day) for day in days}
    return render(request, 'faculty/timetable.html', {
        'timetable_by_day': timetable_by_day,
        'days': days,
        'staff': staff,
    })


# ─────────────────────────────────────────
# QUIZ (Faculty)
# ─────────────────────────────────────────

@faculty_required
def faculty_quizzes(request):
    staff = get_staff(request)
    quizzes = Quiz.objects.filter(created_by=staff).select_related('subject').order_by('-created_at')
    return render(request, 'faculty/quizzes.html', {'quizzes': quizzes, 'staff': staff})


@faculty_required
def create_quiz(request):
    staff = get_staff(request)
    form = QuizForm(request.POST or None, staff=staff)
    form.fields['subject'].queryset = Subject.objects.all()
    if request.method == 'POST' and form.is_valid():
        quiz = form.save(commit=False)
        quiz.created_by = staff
        quiz.save()
        messages.success(request, f"Quiz '{quiz.title}' created. Add questions now.")
        return redirect('add_quiz_questions', pk=quiz.pk)
    return render(request, 'faculty/quiz_form.html', {'form': form})


@faculty_required
def add_quiz_questions(request, pk):
    staff = get_staff(request)
    quiz = get_object_or_404(Quiz, pk=pk, created_by=staff)
    form = QuizQuestionForm(request.POST or None)
    questions = quiz.questions.all()
    if request.method == 'POST' and form.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.order = questions.count() + 1
        question.save()
        messages.success(request, "Question added.")
        return redirect('add_quiz_questions', pk=quiz.pk)
    return render(request, 'faculty/quiz_questions.html', {
        'quiz': quiz, 'form': form, 'questions': questions
    })
