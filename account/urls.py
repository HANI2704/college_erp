from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_student, name='register_student'),

    path(
        'admin/change-password/',
        views.admin_change_password,
        name='admin_change_password'
    ),

    path(
        'import-students/',
        views.import_students_excel,
        name='import_students_excel'
    ),

    # Departments
    path(
        'departments/',
        views.admin_departments,
        name='admin_departments'
    ),

    path(
        'departments/edit/<int:pk>/',
        views.edit_department,
        name='edit_department'
    ),

    path(
        'departments/delete/<int:pk>/',
        views.delete_department,
        name='delete_department'
    ),

    path(
    'get-college-departments/',
    views.get_college_departments,
    name='get_college_departments'
),

    # Sessions
    path(
        'sessions/',
        views.admin_sessions,
        name='admin_sessions'
    ),

    path(
        'sessions/delete/<int:pk>/',
        views.delete_session,
        name='delete_session'
    ),

]