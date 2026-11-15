# student/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/edit/', views.edit_profile, name='edit_student_profile'),
    path('assignments/', views.student_assignments, name='student_assignments'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/submission/<int:pk>/', views.view_submission, name='view_submission'),
    path('results/', views.student_results, name='student_results'),
    path('attendance/', views.student_attendance, name='student_attendance'),
    path('notes/', views.student_notes, name='student_notes'),
    path('lessons/', views.student_lessons, name='student_lessons'),
    path('quizzes/', views.student_quizzes, name='student_quizzes'),
    path('quizzes/<int:pk>/attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('circulars/', views.student_circulars, name='student_circulars'),
    path('events/', views.student_events, name='student_events'),
    path('timetable/', views.student_timetable, name='student_timetable'),
    path('notifications/', views.student_notifications, name='student_notifications'),
    path('leave/', views.student_leave, name='student_leave'),
    path('feedback/', views.student_feedback, name='student_feedback'),
    path('exam-papers/', views.student_exam_papers, name='student_exam_papers'),
]
