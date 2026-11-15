# account/views.py

import pandas as pd
import os
from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from ERP.models import ConstituentCollege
from .models import Student, Department, Session
from .forms import StudentRegistrationForm, LoginForm, DepartmentForm, SessionForm
from faculty.models import Staff
from django.http import JsonResponse
from django.utils.text import slugify

# ─────────────────────────────────────────
# Decorators / helpers
# ─────────────────────────────────────────

def student_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.warning(request, "Please log in to continue.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def staff_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to continue.")
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
                messages.error(request, "Access denied.")
                return redirect('login')
        except Staff.DoesNotExist:
            if not request.user.is_superuser:
                messages.error(request, "Access denied.")
                return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_student(request):
    student_id = request.session.get('student_id')
    if student_id:
        return get_object_or_404(Student, id=student_id)
    return None


# ─────────────────────────────────────────
# LOGIN / LOGOUT / REGISTER
# ─────────────────────────────────────────

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return _redirect_authenticated_user(request)
    if request.session.get('student_id'):
        return redirect('student_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'student')

        if role == 'student':
            try:
                email = email.strip().lower()
                password = password.strip()

                student = Student.objects.get(email=email)

                # ❗ Ensure user exists
                if not student.user:
                    messages.error(request, "Student account not linked with login user.")
                    return redirect('login')

                # ✅ DEBUG (optional)
                print("LOGIN EMAIL:", email)
                print("INPUT PASSWORD:", password)
                print("DB USERNAME:", student.user.username)

                # ✅ USE AUTHENTICATE (IMPORTANT FIX)
                user = authenticate(request, username=student.user.username, password=password)

                if user:
                    request.session['student_id'] = student.id
                    request.session['student_name'] = student.name
                    request.session['role'] = 'student'
                    messages.success(request, f"Welcome back, {student.name}!")
                    return redirect('student_dashboard')
                else:
                    messages.error(request, "Invalid email or password.")

            except Student.DoesNotExist:
                messages.error(request, "No student account found with this email.")

        else:  # faculty or admin
            try:
                user = User.objects.get(email=email)
                auth_user = authenticate(request, username=user.username, password=password)
                if auth_user:
                    login(request, auth_user)
                    try:
                        staff = auth_user.staff_profile
                        request.session['staff_id'] = staff.id
                        request.session['staff_name'] = staff.name
                        request.session['role'] = staff.role
                        if staff.role == 'admin' or auth_user.is_superuser:
                            return redirect('admin_dashboard')
                        else:
                            return redirect('faculty_dashboard')
                    except Staff.DoesNotExist:
                        if auth_user.is_superuser:
                            return redirect('admin_dashboard')
                        messages.error(request, "Staff profile not found.")
                else:
                    messages.error(request, "Invalid email or password.")
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")

    return render(request, 'account/login.html')


def _redirect_authenticated_user(request):
    try:
        staff = request.user.staff_profile
        if staff.role == 'admin' or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('faculty_dashboard')
    except Staff.DoesNotExist:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('login')


def logout_view(request):
    request.session.flush()
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            # Create Django user account
            password = form.cleaned_data['password']
            username = student.email.split('@')[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=student.email,
                password=password,
                first_name=student.name.split()[0] if student.name else '',
            )
            student.user = user
            student.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'account/register.html', {'form': form})

def import_students_excel(request):

    if request.method == 'GET':
        return render(request, 'admin_panel/import_students.html')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']

        try:
            df = pd.read_excel(file)

            # Required columns
            required_columns = [
                'stu_id',
                'name',
                'email',
                'prnno',
                'abcid',
                'student_class',
                'dob',
                'std_mo',
                'father_name',
                'mobile_no_father',
                'mother_name',
                'mobile_no_mother',
                'address',
                'semester',
                'branch',
                'constituent_college',
                'image_path',
            ]

            # Check missing columns
            missing_columns = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing_columns:
                messages.error(
                    request,
                    "Missing Excel columns: " +
                    ", ".join(missing_columns)
                )
                return redirect('admin_students')

            for index, row in df.iterrows():

                email = str(row['email']).strip().lower()
                prn = str(row['prnno']).strip()

                # Get college
                college_name = str(
                    row['constituent_college']
                ).strip()

                college = ConstituentCollege.objects.get(
                    name__iexact=college_name
                )

                # Get branch
                branch_name = str(
                    row['branch']
                ).strip()

                branch = Department.objects.get(
                    name__iexact=branch_name
                )

                # Username
                username = email.split('@')[0]
                base_username = username
                counter = 1

                while User.objects.filter(
                    username=username
                ).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=prn,
                    first_name=str(row['name']).strip()
                )

                # Create student
                student = Student.objects.create(
                    user=user,
                    stu_id=str(row['stu_id']).strip(),
                    name=str(row['name']).strip(),
                    constituent_college=college,
                    branch=branch,
                    semester=int(row['semester']),
                    prnno=prn,
                    abcid=str(row['abcid']).strip(),
                    student_class=str(row['student_class']).strip(),
                    dob=pd.to_datetime(row['dob']).date(),

                    std_mo=str(int(row['std_mo'])).strip(),

                    father_name=str(
                        row['father_name']
                    ).strip(),

                    mobile_no_father=str(
                        int(row['mobile_no_father'])
                    ).strip(),

                    mother_name=str(
                        row['mother_name']
                    ).strip(),

                    mobile_no_mother=str(
                        int(row['mobile_no_mother'])
                    ).strip(),

                    email=email,
                    address=str(row['address']).strip()
                )

                # Image
                image_path = str(
                    row['image_path']
                ).strip()

                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        student.image.save(
                            os.path.basename(image_path),
                            File(img_file),
                            save=True
                        )

            messages.success(
                request,
                "Students imported successfully!"
            )

            return redirect('admin_students')

        except ConstituentCollege.DoesNotExist:
            messages.error(
                request,
                f"Constituent College not found: "
                f"{college_name}"
            )
            return redirect('admin_students')

        except Department.DoesNotExist:
            messages.error(
                request,
                f"Department/Branch not found: "
                f"{branch_name}"
            )
            return redirect('admin_students')

        except Exception as e:
            messages.error(
                request,
                f"Error: {str(e)}"
            )
            return redirect('admin_students')

    return redirect('admin_students')

# def import_students_excel(request):

#     if request.method == 'GET':ConstituentCollege.objects.values('id', 'name')
#         return render(request, 'admin_panel/import_students.html')

#     if request.method == 'POST' and request.FILES.get('excel_file'):
#         file = request.FILES['excel_file']

#         try:
#             df = pd.read_excel(file)

#             for index, row in df.iterrows():
#                 email = str(row['email']).strip().lower()
#                 prn = str(row['prnno']).strip()

#                 college = ConstituentCollege.objects.get(
#                     name=str(row['constituent_college']).strip()
#                 )

#                 branch = Department.objects.get(
#                     name=str(row['branch']).strip()
#                 )

#                 username = email.split('@')[0]
#                 base_username = username
#                 counter = 1

#                 while User.objects.filter(username=username).exists():
#                     username = f"{base_username}{counter}"
#                     counter += 1

#                 user = User.objects.create_user(
#                     username=username,
#                     email=email,
#                     password=prn,
#                     first_name=str(row['name']).strip()
#                 )

#                 student = Student.objects.create(
#                     user=user,
#                     stu_id=str(row['stu_id']).strip(),
#                     name=str(row['name']).strip(),
#                     constituent_college=college,
#                     branch=branch,
#                     semester=int(row['semester']),
#                     prnno=prn,
#                     abcid=str(row['abcid']).strip(),
#                     student_class=str(row['student_class']).strip(),
#                     dob=pd.to_datetime(row['dob']).date(),
#                     std_mo=str(row['std_mo']).strip(),
#                     father_name=str(row['father_name']).strip(),
#                     mobile_no_father=str(row['mobile_no_father']).strip(),
#                     mother_name=str(row['mother_name']).strip(),
#                     mobile_no_mother=str(row['mobile_no_mother']).strip(),
#                     email=email,
#                     address=str(row['address']).strip()
#                 )

#                 # ✅ IMAGE PATH IMPORT
#                 image_path = str(row['image_path']).strip()

#                 if image_path and os.path.exists(image_path):
#                     with open(image_path, 'rb') as img_file:
#                         student.image.save(
#                             os.path.basename(image_path),
#                             File(img_file),
#                             save=True
#                         )

#             messages.success(request, "Students imported successfully!")
#             return redirect('admin_students')

#         except Exception as e:
#             messages.error(request, f"Error: {str(e)}")
#             return redirect('admin_students')

#     return redirect('admin_students')

# ─────────────────────────────────────────
# ADMIN – Department / Session management
# ─────────────────────────────────────────

@admin_required
def get_college_departments(request):

    college_id = request.GET.get('college_id', '').strip()

    # Prevent SPCE or other text values from being used as PK.
    if not college_id.isdigit():
        return JsonResponse({'departments': []})

    college = ConstituentCollege.objects.filter(
        pk=int(college_id)
    ).first()

    if not college:
        return JsonResponse({'departments': []})

    departments = college.get_departments_list()

    return JsonResponse({
        'departments': departments
    })



def sync_college_departments(college):
    """
    Create Department records from department_names
    without creating duplicates.
    """

    department_names = college.get_departments_list()

    for index, dept_name in enumerate(department_names, start=1):

        dept_name = dept_name.strip()

        # Skip empty department names
        if not dept_name:
            continue

        # Check whether department already exists
        exists = Department.objects.filter(
            constituent_college=college,
            name__iexact=dept_name
        ).exists()

        if exists:
            continue

        # Generate unique department ID and code
        slug = slugify(dept_name).upper() or f"DEPT{index}"

        def unique_value(field, prefix):

            base = f"{prefix}{college.pk}-{slug}"[:20]
            value = base
            counter = 1

            while Department.objects.filter(
                **{field: value}
            ).exists():

                suffix = f"-{counter}"
                value = f"{base[:20-len(suffix)]}{suffix}"
                counter += 1

            return value

        # Create department record
        Department.objects.create(
            constituent_college=college,
            name=dept_name,
            department_id=unique_value(
                'department_id', 'D'
            ),
            code=unique_value(
                'code', 'C'
            )
        )


@admin_required
def admin_departments(request):

    college_value = request.GET.get('college', '').strip()

    colleges = ConstituentCollege.objects.all()

    # Get selected college
    selected_college = None

    if college_value:
        if college_value.isdigit():
            selected_college = colleges.filter(
                pk=int(college_value)
            ).first()

        if selected_college is None:
            selected_college = colleges.filter(
                name__iexact=college_value
            ).first()

    # Automatically synchronize departments
    if selected_college:
        sync_college_departments(selected_college)

        departments = Department.objects.filter(
            constituent_college=selected_college
        ).select_related('hod', 'constituent_college')

    elif college_value:
        messages.warning(request, "College not found.")
        departments = Department.objects.none()

    else:
        # Synchronize all colleges
        for college in colleges:
            sync_college_departments(college)

        departments = Department.objects.select_related(
            'hod',
            'constituent_college'
        )

    form = DepartmentForm()

    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Department added successfully."
            )
            return redirect('admin_departments')

    return render(
        request,
        'admin_panel/departments.html',
        {
            'departments': departments,
            'form': form,
            'colleges': colleges,
            'selected_college': (
                selected_college.name if selected_college else college_value
            )
        }
    )


@admin_required
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, request.FILES or None, instance=dept)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Department updated.")
        return redirect('admin_departments')
    return render(request, 'admin_panel/department_form.html', {'form': form, 'dept': dept})


@admin_required
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, "Department deleted.")
    return redirect('admin_departments')


@admin_required
def admin_sessions(request):
    sessions = Session.objects.all().order_by('-session_start')
    form = SessionForm()
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Session added successfully.")
            return redirect('admin_sessions')
    return render(request, 'admin_panel/sessions.html', {'sessions': sessions, 'form': form})


@admin_required
def delete_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session.delete()
        messages.success(request, "Session deleted.")
    return redirect('admin_sessions')

@login_required
def admin_change_password(request):
    if not request.user.is_superuser:
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
        else:
            user = request.user
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully")
            return redirect('login')  # force re-login

    return render(request, 'admin_panel/change_password.html')