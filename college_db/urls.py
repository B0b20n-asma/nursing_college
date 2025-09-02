

from django.urls import path
from . import views


urlpatterns = [
    
    path('', views.dashboard, name='dashboard'),

    # auth
    path('login/', views.login_view, name='login'),   # <-- ensure this
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),  # ✅ add this

    # Student URLs
    path('students/', views.view_students, name='view_students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:student_id>/', views.view_student, name='view_student'),
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
# Staff URLs
    path("staff/", views.view_staff, name="view_staff"),   # list of staff
    path("staff/add/", views.add_staff, name="add_staff"),
    path("staff/<int:staff_id>/", views.view_staff_member, name="view_staff_member"),  # single staff detail
    path("staff/<int:staff_id>/edit/", views.edit_staff, name="edit_staff"),
    path("staff/<int:staff_id>/delete/", views.delete_staff, name="delete_staff"),
    # Courses
    path('courses/', views.view_courses, name='view_courses'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:course_id>/', views.view_course, name='view_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Attendance
   path('attendance/', views.view_attendances, name='view_attendances'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/<int:attendance_id>/', views.view_attendance, name='view_attendance'),
    path('attendance/<int:attendance_id>/edit/', views.edit_attendance, name='edit_attendance'),
    path('attendance/<int:attendance_id>/delete/', views.delete_attendance, name='delete_attendance'),

    # Fees
    path('fees/', views.view_fees, name='view_fees'),
    path('fees/add/', views.add_fee, name='add_fee'),
    path('fees/<int:fee_id>/edit/', views.edit_fee, name='edit_fee'),
    path('fees/<int:fee_id>/delete/', views.delete_fee, name='delete_fee'),
    path('fees/<int:fee_id>/', views.view_fee, name='view_fee'),  # <-- this is required

    # Reports
    path('reports/', views.view_reports, name='view_reports'),
    path('reports/add/', views.add_report, name='add_report'),
    path('reports/<int:report_id>/edit/', views.edit_report, name='edit_report'),
    path('reports/<int:report_id>/delete/', views.delete_report, name='delete_report'),
    path('reports/<int:report_id>/', views.view_report, name='view_report'),  # <-- this is required

    # Grades
path('grades/', views.view_grades, name='view_grades'),
path('grades/add/', views.add_grade, name='add_grade'),
path('grades/add/student/<int:student_id>/', views.add_grade, name='add_grade_for_student'),
path('grades/<int:grade_id>/', views.view_grade, name='view_grade'),
path('grades/<int:grade_id>/edit/', views.edit_grade, name='edit_grade'),
path('grades/<int:grade_id>/delete/', views.delete_grade, name='delete_grade'),
path('students/<int:student_id>/grades/', views.student_grades, name='student_grades'),
path('students/<int:student_id>/enroll/', views.add_enrollment, name='add_enrollment'),
path('<int:pk>/pdf/', views.student_pdf, name='student_pdf'),    # PDF download

   
]
