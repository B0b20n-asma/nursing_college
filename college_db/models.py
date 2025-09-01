from django.db import models
from django.utils import timezone
from django.conf import settings

GENDER_CHOICES = (('M','Male'),('F','Female'),('O','Other'))
STATUS_CHOICES = (('active','Active'),('inactive','Inactive'),('graduated','Graduated'),('suspended','Suspended'))

class College(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    accreditation_status = models.CharField(max_length=100, default='Accredited')
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.college.name}"

class AcademicYear(models.Model):
    year = models.CharField(max_length=20)  # e.g., 2024/2025
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.year

class Course(models.Model):
    #department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=200, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credit_units = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Staff(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=120)  # e.g., Lecturer, Admin
    #department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=200, blank=True, null=True)
    date_joined = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    qualifications = models.TextField(blank=True, null=True)
    timetable = models.TextField(blank=True, null=True)
    assigned_courses = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

class Student(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    department = models.CharField(max_length=200, blank=True, null=True)
    # Change from ForeignKey to CharField
    academic_year = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)  # Changed to CharField
    date_enrolled = models.DateField(default=timezone.now)
    grade = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course', 'academic_year')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
    
class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Fee {self.amount} for {self.student}"

class Payment(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    receipt_no = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.amount} - {self.payment_date}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    present = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {'P' if self.present else 'A'}"

class Report(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    attachment = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return self.title
    
    # ----------GRADING SYSTEM-----------#

class GradingScale(models.Model):
    """
    Admin-configurable grading scale.
    Example rows (min_score, label, description):
      (70, 'A', 'Excellent')
      (60, 'B', 'Good')
      (50, 'C', 'Satisfactory')
      (45, 'D', 'Pass')
      (0,  'F', 'Fail')
    The code selects the highest min_score <= score.
    """
    min_score = models.PositiveSmallIntegerField(help_text="Minimum percentage (inclusive)")
    label = models.CharField(max_length=10)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first in admin")

    class Meta:
        ordering = ['-min_score']  # so higher thresholds come first
        unique_together = ('min_score', 'label')

    def __str__(self):
        return f"{self.label} (≥{self.min_score}%)"


class StudentGrade(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., 2024-2025, First Year, etc.")
    score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Numeric score or percentage (0-100)")
    grade_label = models.CharField(max_length=10, blank=True)   # filled automatically
    remark = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'academic_year')  # optional; ensures one grade per student/course/year

    def __str__(self):
        return f"{self.student} - {self.course} : {self.grade_label or self.score}"

    def compute_grade_label(self):
        """
        Look up GradingScale and return the label for this.score.
        If no scale found, use manual mapping fallback.
        """
        try:
            scales = GradingScale.objects.all().order_by('-min_score')
            for s in scales:
                if float(self.score) >= s.min_score:
                    return s.label
        except Exception:
            pass

        # Fallback default mapping (if admin hasn't configured GradingScale)
        try:
            sc = float(self.score)
        except Exception:
            return ''
        if sc >= 70:
            return 'A'
        if sc >= 60:
            return 'B'
        if sc >= 50:
            return 'C'
        if sc >= 45:
            return 'D'
        return 'F'

    def save(self, *args, **kwargs):
        # auto-set grade_label before save
        self.grade_label = self.compute_grade_label()
        super().save(*args, **kwargs)