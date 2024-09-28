from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.timezone import now


teacher_group, created = Group.objects.get_or_create(name='Teacher')
student_group, created = Group.objects.get_or_create(name='Student')


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=100, default="Untitled Quiz")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100, default="Option A")
    option_b = models.CharField(max_length=100, default="Option B")
    option_c = models.CharField(max_length=100, default="Option C")
    option_d = models.CharField(max_length=100, default="Option D")
    correct_answer = models.CharField(max_length=1,choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A') 

class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    marks = models.IntegerField(default=0)  # Store the score, calculated automatically
    feedback = models.TextField(blank=True, null=True)  # Optional feedback from the teacher
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.student} - {self.quiz} - {self.marks}'
