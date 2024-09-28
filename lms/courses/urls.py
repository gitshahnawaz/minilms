from django.urls import path
from . import views

urlpatterns = [
    path('create_course/', views.create_course, name='create_course'),
     path('courses/', views.course_list, name='course_list'),
     path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('add-questions/<int:quiz_id>/', views.add_questions, name='add_questions'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('view_results/', views.view_results, name='view_results'),
    path('generate_report/<int:quiz_id>/', views.generate_report, name='generate_report'),
    path('fetch-api-quiz/', views.fetch_api_quiz, name='fetch_api_quiz'),
    path('quiz-submissions/', views.quiz_submissions, name='quiz_submissions'),
    

]
