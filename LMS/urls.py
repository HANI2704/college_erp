# LMS/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Subject management (Admin)
    path('subjects/', views.admin_subjects, name='admin_subjects'),
    path('subjects/edit/<int:pk>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
    path('subjects/<int:pk>/assign-faculty/', views.assign_faculty_to_subject, name='assign_faculty_to_subject'),

    # Units & Lessons (Faculty)
    path('units/', views.faculty_units, name='faculty_units'),
    path('lessons/', views.faculty_lessons, name='faculty_lessons'),
    path('lessons/delete/<int:pk>/', views.delete_lesson, name='delete_lesson'),
]
