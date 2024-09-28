from django import forms
from django.contrib.auth.models import User, Group
from .models import Course, Quiz, Question

class RegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(choices=[('teacher', 'Teacher'), ('student', 'Student')], label="Role")

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            role = self.cleaned_data['role']
            if role == 'teacher':
                teacher_group = Group.objects.get(name='Teacher')
                user.groups.add(teacher_group)
            else:
                student_group = Group.objects.get(name='Student')
                user.groups.add(student_group)
        return user


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'course']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']


