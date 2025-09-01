

from django import forms
from .models import Student, Staff, Course, Attendance, Report, Fee, Enrollment, College, Department,StudentGrade

#class CollegeForm(forms.ModelForm):
    #class Meta:
        #model = College
        #fields = '__all__'

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

#class StudentForm(forms.ModelForm):
    #date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)
    #class Meta:
        #model = Student
        #exclude = ('created_at',)

#class StaffForm(forms.ModelForm):
    #date_joined = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}), required=False)
    #class Meta:
        #model = Staff
        #fields = '__all__'

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["college", "created_at"]  # Exclude both college and created_at
        widgets = {
            'academic_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2023-2024'
            }),}

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        exclude = ["college"]   # hide college here too


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

class AttendanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Attendance
        fields = '__all__'

class FeeForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Fee
        fields = '__all__'


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'

class StudentGradeForm(forms.ModelForm):
    class Meta:
        model = StudentGrade
        # don't include recorded_by/grade_label/recorded_at (they are set automatically)
        fields = ['student','course','academic_year','score','remark']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'}),
            'remark': forms.TextInput(),
        }

    def clean_score(self):
        sc = self.cleaned_data.get('score')
        if sc is None:
            raise forms.ValidationError("Provide a numeric score.")
        if sc < 0 or sc > 100:
            raise forms.ValidationError("Score must be between 0 and 100.")
        return sc
    
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'academic_year', 'grade']