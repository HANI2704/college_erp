# ERP/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import ConstituentCollege
from .forms import ConstituentCollegeForm
from LMS.models import Subject
from account.models import Student



from .models import (
    Event, Circular, Timetable, TimeSlot, TransportRegistration,
    OldExamPaper, ExamSeason, Course, Attendance, StudentResult, Alumni
)
from .forms import (
    EventForm, CircularForm, TimetableForm, TimeSlotForm, TransportForm,
    OldExamPaperForm, ExamSeasonForm, CourseForm, AlumniForm
)
from faculty.models import Staff


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


def get_staff(request):
    try:
        return request.user.staff_profile
    except (Staff.DoesNotExist, AttributeError):
        return None


# ─────────────────────────────────────────
# EVENTS
# ─────────────────────────────────────────

@admin_required
def admin_events(request):
    events = Event.objects.all().order_by('-start_date')
    form = EventForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)
        staff = get_staff(request)
        event.created_by = staff
        event.save()
        messages.success(request, "Event created.")
        return redirect('admin_events')
    return render(request, 'admin_panel/events.html', {'events': events, 'form': form})


@admin_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect('admin_events')
    return render(request, 'admin_panel/event_form.html', {'form': form, 'event': event})


@admin_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted.")
    return redirect('admin_events')


# ─────────────────────────────────────────
# CIRCULARS
# ─────────────────────────────────────────

@admin_required
def admin_circulars(request):
    circulars = Circular.objects.all().order_by('-is_pinned', '-publish_date')
    form = CircularForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        circular = form.save(commit=False)
        circular.created_by = request.user
        circular.save()
        messages.success(request, "Circular published.")
        return redirect('admin_circulars')
    return render(request, 'admin_panel/circulars.html', {'circulars': circulars, 'form': form})


@admin_required
def edit_circular(request, pk):
    circular = get_object_or_404(Circular, pk=pk)
    form = CircularForm(request.POST or None, request.FILES or None, instance=circular)
    
    if request.method == 'POST':
          form = CircularForm(request.POST, request.FILES, instance=circular)

          if form.is_valid():
              circular_obj = form.save(commit=False)

              # Keep old file if new file not uploaded
              if not request.FILES.get('attachment'):
                  circular_obj.attachment = circular.attachment

              circular_obj.save()

              messages.success(request, "Circular updated.")
              return redirect('admin_circulars')
    else:
          form = CircularForm(instance=circular)

    return render(request, 'admin_panel/circular_form.html', {
          'form': form,
          'circular': circular
      })
        

@admin_required
def delete_circular(request, pk):
    circular = get_object_or_404(Circular, pk=pk)
    if request.method == 'POST':
        circular.delete()
        messages.success(request, "Circular deleted.")
    return redirect('admin_circulars')


# ─────────────────────────────────────────
# TIMETABLE
# ─────────────────────────────────────────

@admin_required
def admin_timetable(request):
    timetable = Timetable.objects.select_related('time_slot').order_by('day', 'time_slot__start_time')
    time_slots = TimeSlot.objects.all()
    form = TimetableForm(request.POST or None)
    slot_form = TimeSlotForm(request.POST or None)

    if request.method == 'POST':
        if 'add_slot' in request.POST:
            if slot_form.is_valid():
                slot_form.save()
                messages.success(request, "Time slot added.")
                return redirect('admin_timetable')
        elif form.is_valid():
            form.save()
            messages.success(request, "Timetable entry added.")
            return redirect('admin_timetable')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: timetable.filter(day=day) for day in days}

    return render(request, 'admin_panel/timetable.html', {
        'timetable': timetable,
        'timetable_by_day': timetable_by_day,
        'form': form,
        'slot_form': slot_form,
        'time_slots': time_slots,
        'days': days,
    })


@admin_required
def delete_timetable_entry(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Entry deleted.")
    return redirect('admin_timetable')


# ─────────────────────────────────────────
# COURSES
# ─────────────────────────────────────────

@admin_required
def admin_courses(request):
    courses = Course.objects.select_related('department').all()
    form = CourseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Course added.")
        return redirect('admin_courses')
    return render(request, 'admin_panel/courses.html', {'courses': courses, 'form': form})


@admin_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Course updated.")
        return redirect('admin_courses')
    return render(request, 'admin_panel/course_form.html', {'form': form, 'course': course})


@admin_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted.")
    return redirect('admin_courses')

@admin_required
def admin_constituent(request):

    if request.method == "POST":
        form = ConstituentCollegeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_constituent')

    else:
        form = ConstituentCollegeForm()

    colleges = ConstituentCollege.objects.all()

    return render(request, "admin_panel/constituent.html", {
        "form": form,
        "colleges": colleges
    })
    # return render(request,"admin_panel/constituent.html",{
    #     "form":form,
    #     "colleges":colleges
    # })

@admin_required
def edit_constituent(request,id):

    college = get_object_or_404(ConstituentCollege,id=id)

    if request.method=="POST":
        form = ConstituentCollegeForm(request.POST,instance=college)

        if form.is_valid():
            form.save()
            return redirect('admin_constituent')

    else:
        form = ConstituentCollegeForm(instance=college)

    return render(request,"admin_panel/edit_constituent.html",{"form":form})

@admin_required
def delete_constituent(request,id):

    college = get_object_or_404(ConstituentCollege,id=id)
    college.delete()

    return redirect('admin_constituent')
# ─────────────────────────────────────────
# TRANSPORT
# ─────────────────────────────────────────

@admin_required
def admin_transport(request):
    registrations = TransportRegistration.objects.select_related('student').order_by('-created_at')
    form = TransportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Transport registration added.")
        return redirect('admin_transport')
    return render(request, 'admin_panel/transport.html', {'registrations': registrations, 'form': form})


@admin_required
def delete_transport(request, pk):
    reg = get_object_or_404(TransportRegistration, pk=pk)
    if request.method == 'POST':
        reg.delete()
        messages.success(request, "Registration deleted.")
    return redirect('admin_transport')


# ─────────────────────────────────────────
# OLD EXAM PAPERS
# ─────────────────────────────────────────

@admin_required
def admin_exam_papers(request):
    papers = OldExamPaper.objects.select_related('course', 'subject', 'season').order_by('-uploaded_at')
    seasons = ExamSeason.objects.all()
    form = OldExamPaperForm(request.POST or None, request.FILES or None)
    season_form = ExamSeasonForm(request.POST or None)

    if request.method == 'POST':
        if 'add_season' in request.POST:
            if season_form.is_valid():
                season_form.save()
                messages.success(request, "Exam season added.")
                return redirect('admin_exam_papers')
        elif form.is_valid():
            form.save()
            messages.success(request, "Exam paper uploaded.")
            return redirect('admin_exam_papers')

    return render(request, 'admin_panel/exam_papers.html', {
        'papers': papers, 'seasons': seasons,
        'form': form, 'season_form': season_form
    })


@admin_required
def delete_exam_paper(request, pk):
    paper = get_object_or_404(OldExamPaper, pk=pk)
    if request.method == 'POST':
        paper.delete()
        messages.success(request, "Paper deleted.")
    return redirect('admin_exam_papers')


# ─────────────────────────────────────────
# ALUMNI
# ─────────────────────────────────────────

@admin_required
def admin_alumni(request):
    alumni_list = Alumni.objects.all().order_by('-created_at')
    form = AlumniForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Alumni record added.")
        return redirect('admin_alumni')
    return render(request, 'admin_panel/alumni.html', {'alumni_list': alumni_list, 'form': form})


@admin_required
def delete_alumni(request, pk):
    alumni = get_object_or_404(Alumni, pk=pk)
    if request.method == 'POST':
        alumni.delete()
        messages.success(request, "Alumni deleted.")
    return redirect('admin_alumni')


# ─────────────────────────────────────────
# ATTENDANCE REPORT (Admin)
# ─────────────────────────────────────────

@admin_required
def admin_attendance_report(request):
    subjects = Subject.objects.all()
    report_data = []

    selected_subject = None   # ✅ MUST ADD THIS

    if request.GET.get('subject_id'):
        selected_subject = get_object_or_404(
            Subject, pk=request.GET['subject_id']
        )

        for student in Student.objects.all():
            total = Attendance.objects.filter(student=student, subject=selected_subject).count()
            present = Attendance.objects.filter(student=student, subject=selected_subject, status=True).count()

            absent = total - present
            pct = round((present / total * 100), 1) if total > 0 else 0

            report_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': absent,
                'percentage': pct
            })

    return render(request, 'admin_panel/attendance_report.html', {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'report_data': report_data,
    })