import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Quiz, Result, Question
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, CourseForm, QuizForm, QuestionForm
from django.contrib.auth.models import Group


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def is_student(user):
    return user.groups.filter(name='Student').exists()


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('dashboard')  # Redirect to a dashboard after login
    else:
        form = RegistrationForm()
    return render(request, 'courses/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after successful login
        else:
            return HttpResponse("Invalid login")
    return render(request, 'courses/login.html')

@login_required
def dashboard(request):
    if request.user.groups.filter(name='Teacher').exists():
        return redirect('teacher_dashboard')
    elif request.user.groups.filter(name='Student').exists():
        return redirect('student_dashboard')
    else:
        return HttpResponse("No role assigned")

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    # Dashboard content for teachers
    return render(request, 'courses/teacher_dashboard.html')

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    # Dashboard content for students
    return render(request, 'courses/student_dashboard.html')

@login_required
@user_passes_test(is_teacher)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user  # Assign the teacher to the course
            course.save()
            return redirect('course_list')  # Redirect to the course list after creation
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.teacher = request.user  # Associate the quiz with the logged-in teacher
            quiz.save()
            return redirect('add_questions', quiz_id=quiz.id)  # Redirect to add questions
    else:
        quiz_form = QuizForm()
    return render(request, 'courses/create_quiz.html', {'quiz_form': quiz_form})

@login_required
@user_passes_test(is_teacher)
def add_questions(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz  # Associate the question with the quiz
            question.save()
            return redirect('add_questions', quiz_id=quiz.id)  # Redirect to add more questions
    else:
        question_form = QuestionForm()
    questions = quiz.questions.all()  # Get all questions related to this quiz
    return render(request, 'courses/add_questions.html', {
        'quiz': quiz,
        'question_form': question_form,
        'questions': questions,
    })


@login_required
@user_passes_test(is_student)
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.all()  # Assuming related name for the questions field is 'questions'
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        for question in questions:
            # Get the student's selected answer for each question
            selected_choice = request.POST.get(f'question_{question.id}')
            
            if selected_choice:
                # Compare the selected choice with the correct answer
                if selected_choice == question.correct_answer:  # Assuming you store correct_answer in Question model
                    score += 1
        
        # Calculate percentage or final score, if needed
        final_score = (score / total_questions) * 100
        
        # Save the result for the student
        Result.objects.create(student=request.user, quiz=quiz, marks=final_score)
        
        # Redirect to results page (adjust 'view_results' if needed)
        return redirect('view_results')
    
    return render(request, 'courses/take_quiz.html', {
        'quiz': quiz, 
        'questions': questions
    })


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()  # Fetch all quizzes. You can filter them by course if needed.
    
    # Render the template and pass the quizzes
    return render(request, 'courses/quiz_list.html', {'quizzes': quizzes})

@login_required
@user_passes_test(is_student)
def view_results(request):
    results = Result.objects.filter(student=request.user)  # Get all results for the logged-in student
    return render(request, 'courses/view_results.html', {'results': results})

@login_required
@user_passes_test(is_teacher)
def generate_report(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    results = Result.objects.filter(quiz=quiz)
    return render(request, 'courses/report.html', {'quiz': quiz, 'results': results})

@login_required
def course_list(request):
    # Fetch all courses from the database
    courses = Course.objects.all()  # You can filter by conditions if needed
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    # Fetch the specific course by its ID
    course = Course.objects.get(id=course_id)
    return render(request, 'courses/course_detail.html', {'course': course})
@login_required
@user_passes_test(is_teacher)
def fetch_api_quiz(request):
    courses = Course.objects.all()  # Fetch all courses

    if request.method == 'POST':
        api_url = request.POST.get('api_url')
        quiz_title = request.POST.get('quiz_title')
        course_id = request.POST.get('course')  # Get the selected course ID

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                questions = data.get('results', [])

                # Create a new quiz and associate it with the selected course
                quiz = Quiz.objects.create(title=quiz_title, teacher=request.user, course_id=course_id)

                # Save fetched questions to the quiz
                for question_data in questions:
                    question_text = question_data['question']
                    correct_answer = question_data['correct_answer']
                    incorrect_answers = question_data['incorrect_answers']

                    # Save the fetched questions
                    Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        option_a=correct_answer,
                        option_b=incorrect_answers[0],
                        option_c=incorrect_answers[1],
                        option_d=incorrect_answers[2],
                        correct_answer=correct_answer
                    )
                return redirect('add_questions', quiz_id=quiz.id)
            else:
                return render(request, 'courses/fetch_api_quiz.html', {
                    'error': 'Failed to fetch questions from the API.',
                    'courses': courses
                })
        except requests.exceptions.RequestException as e:
            return render(request, 'courses/fetch_api_quiz.html', {
                'error': str(e),
                'courses': courses
            })

    return render(request, 'courses/fetch_api_quiz.html', {'courses': courses})


@login_required
def quiz_submissions(request):
    results = Result.objects.all()  # Fetch all quiz results
    
    # Check if the logged-in user is a teacher
    is_teacher = request.user.groups.filter(name='Teacher').exists()

    if request.method == 'POST' and is_teacher:
        # Handle feedback submission by teacher
        for result in results:
            feedback = request.POST.get(f'feedback_{result.id}')
            if feedback:
                result.feedback = feedback
                result.save()
        return redirect('quiz_submissions')

    return render(request, 'courses/quiz_submissions.html', {
        'results': results,
        'is_teacher': is_teacher,  # Pass boolean indicating whether the user is a teacher
    })




