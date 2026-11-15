# faculty/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Dashboards
    path('dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Staff management (Admin)
    path('admin/staff/', views.admin_staff_list, name='admin_staff_list'),
    path('admin/staff/add/', views.add_staff, name='add_staff'),
    path('admin/staff/edit/<int:pk>/', views.edit_staff, name='edit_staff'),
    path('admin/staff/delete/<int:pk>/', views.delete_staff, name='delete_staff'),
    path('import-staff/', views.import_staff_excel, name='import_staff_excel'),
    
    # Student management (Admin)
    path('admin/students/', views.admin_students, name='admin_students'),
    path('admin/students/<int:pk>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/students/delete/<int:pk>/', views.delete_student, name='delete_student'),

    # Assignments
    path('assignments/', views.faculty_assignments, name='faculty_assignments'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/edit/<int:pk>/', views.edit_assignment, name='edit_assignment'),
    path('assignments/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),
    path('assignments/<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),

    # Attendance
    path('attendance/', views.faculty_attendance, name='faculty_attendance'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),

    # Results
    path('results/', views.faculty_results, name='faculty_results'),
    path('results/upload/', views.upload_result, name='upload_result'),
    path('results/edit/<int:pk>/', views.edit_result, name='edit_result'),

    # Notes
    path('notes/', views.faculty_notes, name='faculty_notes'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),

    # Notifications
    path('notifications/', views.faculty_notifications, name='faculty_notifications'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),

    # Leave requests
    path('leave-requests/', views.faculty_leave_requests, name='faculty_leave_requests'),
    path('leave-requests/<int:pk>/action/', views.approve_leave, name='approve_leave'),

    # Feedback
    path('feedback/', views.faculty_feedback, name='faculty_feedback'),
    path('feedback/<int:pk>/reply/', views.reply_feedback, name='reply_feedback'),

    # Timetable
    path('timetable/', views.faculty_timetable, name='faculty_timetable'),

    # Quizzes
    path('quizzes/', views.faculty_quizzes, name='faculty_quizzes'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/<int:pk>/questions/', views.add_quiz_questions, name='add_quiz_questions'),
]
