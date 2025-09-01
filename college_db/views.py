from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum
from .models import Student, Staff, Course, Attendance, Fee, Report,College,  Department, AcademicYear, Enrollment,StudentGrade, GradingScale
from .forms import StudentForm, StaffForm, CourseForm, AttendanceForm, FeeForm, ReportForm,  DepartmentForm,StudentGradeForm,EnrollmentForm  # create this form
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout  # rename the imported function
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.conf.urls.static import static



@login_required
def dashboard(request):
    # counts
    total_students = Student.objects.count()
    total_staff = Staff.objects.count()
    total_courses = Course.objects.count()
    due_fees = Fee.objects.filter(paid=False).count()
    recent_students = Student.objects.order_by('-created_at')[:5]
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'total_courses': total_courses,
        'due_fees': due_fees,
        'recent_students': recent_students,
    }
    return render(request, 'college_db/dashboard.html', context)

# SIGN UP

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'college_db/signup.html', {'form': form})

# LOGIN view
def login_view(request):
    # if already logged in, go to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    username_prefill = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        username_prefill = username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # use Django auth login (renamed to avoid shadowing)
            auth_login(request, user)
            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
            return redirect(request.GET.get('next') or 'dashboard')
        else:
            error = "Invalid username or password."

    return render(request, 'college_db/login.html', {
        'error': error,
        'username_prefill': username_prefill,
    })

# LOGOUT view
def logout_view(request):
    """
    Safe logout handler that will not recurse.
    Update your urls.py to point to views.logout_view.
    """
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('login')


# ---------------- Student CRUD ----------------
#def view_students(request):
    #students = Student.objects.select_related('college','department','academic_year').all().order_by('admission_number')
    #return render(request, 'college_db/view_students.html', {'students': students})

#def view_student(request, student_id):
    #student = get_object_or_404(Student, pk=student_id)
    #enrollments = student.enrollments.select_related('course','academic_year').all()
    #fees = student.fees.all()
    #attendance = Attendance.objects.filter(student=student).order_by('-date')[:20]
    #return render(request, 'college_db/view_student.html', {
        #'student': student, 'enrollments': enrollments, 'fees': fees, 'attendance': attendance
    
from django.db.models import Prefetch
from .models import Student, Enrollment

def view_students(request):
    # Correct version - only use select_related for actual foreign keys
    students = Student.objects.select_related("college").all().order_by('admission_number')
    
    return render(request, 'college_db/view_students.html', {'students': students})


def view_student(request, student_id):
    student = get_object_or_404(
        Student.objects
        .select_related("college")  # Only foreign keys here
        .prefetch_related(
            Prefetch('enrollments', queryset=Enrollment.objects.select_related('course'))  # REMOVE 'academic_year'
        ),
        pk=student_id
    )

    enrollments = student.enrollments.all()
    fees = student.fees.all()
    attendance = student.attendance_set.all().order_by('-date')[:20]

    return render(request, 'college_db/view_student.html', {
        'student': student,
        'enrollments': enrollments,
        'fees': fees,
        'attendance': attendance
    })

@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)

            # Assign college (single college system: first college)
            student.college = College.objects.first()

            student.save()
            messages.success(request, 'Student added successfully.')
            return redirect('view_students')
    else:
        form = StudentForm()

    return render(request, 'college_db/add_student.html', {'form': form})
def edit_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated.')
            return redirect('view_student', student_id=student.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'college_db/edit_student.html', {'form': form, 'student': student})

def delete_student(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted.')
        return redirect('view_students')
    return render(request, 'college_db/delete_student.html', {'student': student})

# ---------------- Staff CRUD ----------------
def view_staff(request):
   staffs = Staff.objects.select_related("college").all().order_by('first_name')
   return render(request, 'college_db/view_staff_members.html', {'staffs': staffs})

#def view_staff(request, staff_id):
   # staff = get_object_or_404(Staff, id=staff_id)
    #return render(request, 'college_db/view_staff.html', {'staff': staff})



def view_staff_member(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    return render(request, 'college_db/view_staff.html', {'staff': staff})

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            # assign the college (e.g., first college in DB)
            staff.college = College.objects.first()
            staff.save()
            return redirect('view_staff')
    else:
        form = StaffForm()
    return render(request, 'college_db/add_staff.html', {'form': form})


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff updated.')
            return redirect('view_staff_member', staff_id=staff.id)
    else:
        form = StaffForm(instance=staff)
    return render(request, 'college_db/edit_staff.html', {'form': form, 'staff': staff})

def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted.')
        return redirect('view_staff')
    return render(request, 'college_db/delete_staff.html', {'staff': staff})

# ---------------- Course CRUD ----------------
def view_courses(request):
    courses = Course.objects.all().order_by('code')
    
    return render(request, 'college_db/view_courses.html', {'courses': courses})

def view_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'college_db/view_course.html', {'course': course})

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added.')
            return redirect('view_courses')
    else:
        form = CourseForm()
    return render(request, 'college_db/add_course.html', {'form': form})

def edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated.')
            return redirect('view_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'college_db/edit_course.html', {'form': form, 'course': course})

def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('view_courses')
    return render(request, 'college_db/delete_course.html', {'course': course})

# -------- Attendance CRUD --------

def view_attendances(request):
    attendance_qs = (
        Attendance.objects.select_related('student', 'course')
        .all()
        .order_by('-date')
    )
    return render(request, 'college_db/view_attendances.html', {'attendances': attendance_qs})

def view_attendance(request, attendance_id):
    attendance = get_object_or_404(
        Attendance.objects.select_related('student', 'course'),
        id=attendance_id
    )
    return render(request, 'college_db/view_attendance.html', {'attendance': attendance})

def add_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance recorded.')
            # ✅ pass the required kwarg
            return redirect('view_attendance', attendance_id=attendance.id)
            # If you namespaced the app (app_name + include('...', namespace='college_db')):
            # return redirect('college_db:view_attendance', attendance_id=attendance.id)
    else:
        form = AttendanceForm()
    return render(request, 'college_db/add_attendance.html', {'form': form})

def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance updated.')
            # ✅ go back to the same record’s detail page
            return redirect('view_attendance', attendance_id=attendance.id)
            # or: return redirect('view_attendances')  # if you prefer list after edit
    else:
        form = AttendanceForm(instance=attendance)
    return render(request, 'college_db/edit_attendance.html', {'form': form, 'attendance': attendance})

def delete_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, pk=attendance_id)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance deleted.')
        # ✅ after delete, go to list (detail no longer exists)
        return redirect('view_attendances')
    return render(request, 'college_db/delete_attendance.html', {'attendance': attendance})

# ---------------- Fees ----------------
def view_fees(request):
    fees = Fee.objects.select_related('student').all().order_by('-due_date')
    return render(request, 'college_db/view_fees.html', {'fees': fees})

def view_fee(request, fee_id):
    # Get the single fee record with related student
    fee = get_object_or_404(Fee.objects.select_related('student'), id=fee_id)
    return render(request, 'college_db/view_fee.html', {'fee': fee})

def add_fee(request):
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee added.')
            return redirect('view_fees')
    else:
        form = FeeForm()
    return render(request, 'college_db/add_fee.html', {'form': form})

def edit_fee(request, fee_id):
    fee = get_object_or_404(Fee, pk=fee_id)
    if request.method == 'POST':
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee updated.')
            return redirect('view_fees')
    else:
        form = FeeForm(instance=fee)
    return render(request, 'college_db/edit_fee.html', {'form': form, 'fee': fee})

def delete_fee(request, fee_id):
    fee = get_object_or_404(Fee, pk=fee_id)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee deleted.')
        return redirect('view_fees')
    return render(request, 'college_db/delete_fee.html', {'fee': fee})

# ---------------- Reports ----------------
def view_reports(request):
    reports = Report.objects.select_related('created_by').all().order_by('-created_at')
    return render(request, 'college_db/view_reports.html', {'reports': reports})

def view_report(request, report_id):
    report_qs = Report.objects.filter(id=report_id)
    report = get_object_or_404(report_qs)
    return render(request, 'college_db/view_report.html', {'report': report})

def add_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report added.')
            return redirect('view_reports')
    else:
        form = ReportForm()
    return render(request, 'college_db/add_report.html', {'form': form})

def edit_report(request, report_id):
    rep = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=rep)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated.')
            return redirect('view_reports')
    else:
        form = ReportForm(instance=rep)
    return render(request, 'college_db/edit_report.html', {'form': form, 'report': rep})

def delete_report(request, report_id):
    rep = get_object_or_404(Report, pk=report_id)
    if request.method == 'POST':
        rep.delete()
        messages.success(request, 'Report deleted.')
        return redirect('view_reports')
    return render(request, 'college_db/delete_report.html', {'report': rep})

#-------GRADING VIWES------------#
@login_required
def view_grades(request):
    # CORRECTED: Use StudentGrade.objects to get ALL grades
    grades = StudentGrade.objects.select_related('student', 'course', 'recorded_by').order_by('-recorded_at')
    return render(request, 'college_db/view_grades.html', {'grades': grades})

@login_required
def view_grade(request, grade_id):
    # CORRECTED: Get a single grade by ID
    grade = get_object_or_404(StudentGrade.objects.select_related('student', 'course', 'recorded_by'), id=grade_id)
    return render(request, 'college_db/view_grade.html', {'grade': grade})

@login_required
def add_grade(request, student_id=None):
    """
    If student_id provided (from student detail page), prefill that student and hide the student input in template.
    """
    if request.method == 'POST':
        form = StudentGradeForm(request.POST)
        if form.is_valid():
            g = form.save(commit=False)
            g.recorded_by = request.user
            g.save()
            messages.success(request, 'Grade recorded.')
            # redirect to student detail if we added for a student, else list
            return redirect('view_student' if form.cleaned_data.get('student') else 'view_grades', student_id or g.id)
    else:
        if student_id:
            # preselect student, render form with initial
            form = StudentGradeForm(initial={'student': student_id})
        else:
            form = StudentGradeForm()
    return render(request, 'college_db/add_grade.html', {'form': form, 'student_id': student_id})

@login_required
def edit_grade(request, grade_id):
    grade = get_object_or_404(StudentGrade, id=grade_id)
    if request.method == 'POST':
        form = StudentGradeForm(request.POST, instance=grade)
        if form.is_valid():
            updated_grade = form.save(commit=False)
            updated_grade.recorded_by = request.user
            updated_grade.save()
            messages.success(request, 'Grade updated successfully.')
            return redirect('view_grade', grade_id=grade.id)
    else:
        form = StudentGradeForm(instance=grade)
    
    return render(request, 'college_db/edit_grade.html', {
        'form': form,
        'grade': grade
    })


@login_required
def delete_grade(request, grade_id):
    g = get_object_or_404(StudentGrade, id=grade_id)
    if request.method == 'POST':
        g.delete()
        messages.success(request, 'Grade deleted.')
        return redirect('view_grades')
    return render(request, 'college_db/delete_grade.html', {'grade': g})

# helper: show grades for a single student
@login_required
def student_grades(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    grades = student.grades.select_related('course',).all().order_by('-recorded_at')
    return render(request, 'college_db/student_grades.html', {'student': student, 'grades': grades})


def add_enrollment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            return redirect('view_student', student_id=student.id)
    else:
        form = EnrollmentForm()

    return render(request, 'college_db/add_enrollment.html', {
        'form': form,
        'student': student
    })

