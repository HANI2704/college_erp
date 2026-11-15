# ERP/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Events
    path('events/', views.admin_events, name='admin_events'),
    path('events/edit/<int:pk>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:pk>/', views.delete_event, name='delete_event'),

    # Circulars
    path('circulars/', views.admin_circulars, name='admin_circulars'),
    path('circulars/edit/<int:pk>/', views.edit_circular, name='edit_circular'),
    path('circulars/delete/<int:pk>/', views.delete_circular, name='delete_circular'),

    # Timetable
    path('timetable/', views.admin_timetable, name='admin_timetable'),
    path('timetable/delete/<int:pk>/', views.delete_timetable_entry, name='delete_timetable_entry'),

    # Courses
    path('courses/', views.admin_courses, name='admin_courses'),
    path('courses/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:pk>/', views.delete_course, name='delete_course'),
   
    #constituent
    path('admin/constituent/',views.admin_constituent,name='admin_constituent'),
    path('admin/constituent/edit/<int:id>/',views.edit_constituent,name='edit_constituent'),
    path('admin/constituent/delete/<int:id>/',views.delete_constituent,name='delete_constituent'),

    # Transport
    path('transport/', views.admin_transport, name='admin_transport'),
    path('transport/delete/<int:pk>/', views.delete_transport, name='delete_transport'),

    # Old Exam Papers
    path('exam-papers/', views.admin_exam_papers, name='admin_exam_papers'),
    path('exam-papers/delete/<int:pk>/', views.delete_exam_paper, name='delete_exam_paper'),

    # Alumni
    path('alumni/', views.admin_alumni, name='admin_alumni'),
    path('alumni/delete/<int:pk>/', views.delete_alumni, name='delete_alumni'),

    # Attendance Report
    path('attendance-report/', views.admin_attendance_report, name='admin_attendance_report'),
]
