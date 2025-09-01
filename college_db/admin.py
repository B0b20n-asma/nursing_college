from django.contrib import admin
from .models import (College, Department, AcademicYear, Course, Staff, Student,
                     Enrollment, Fee, Payment, Attendance, Report,GradingScale, StudentGrade)

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name','city','region','accreditation_status')

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ('label','min_score','description')
    ordering = ('-min_score',)
    list_editable = ('min_score','description')
    search_fields = ('label','description')


@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('student','course','academic_year','score','grade_label','recorded_by','recorded_at')
    list_filter = ('grade_label','academic_year','course')
    search_fields = ('student__first_name','student__last_name','student__admission_number','course__name')

admin.site.register(Department)
admin.site.register(AcademicYear)
admin.site.register(Course)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Fee)
admin.site.register(Payment)
admin.site.register(Attendance)
admin.site.register(Report)



