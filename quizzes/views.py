from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, Contact
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse  
import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
def home(request):
    try :
        quizzes = Quiz.objects.all().order_by('-created_at')
    except Quiz.DoesNotExist:
        quizzes = None
    context = {'quizzes': quizzes}
    return render(request, 'index.html',context)

def contact_submit(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return redirect("/#contact")

        Contact.objects.create(name=name, email=email, message=message)
        messages.success(request, "Thank you! Your message has been sent successfully.")
        return redirect("/#contact")

    return redirect("/")
def start_quiz(request):
    try :
        quizzes = Quiz.objects.all().order_by('-created_at')
    except Quiz.DoesNotExist:
        quizzes = None
    context = {'quizzes': quizzes}
    return render(request, 'quiz_list.html', context)

@login_required
def quiz_attempt(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('answers').all()
    return render(request, 'quiz_attempt.html', {'quiz': quiz, 'questions': questions})


@login_required
@csrf_exempt
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_answers = data.get('answers', {})

        quiz = get_object_or_404(Quiz.objects.prefetch_related('questions__answers'), id=quiz_id)
        total_score = 0

        submission = UserSubmission.objects.create(
            quiz=quiz,
            user_name=request.user.username,
            score=0
        )

        for question in quiz.questions.all():
            qid_str = str(question.id)
            qid_int = question.id

            selected_answer_id = selected_answers.get(qid_str) or selected_answers.get(qid_int)

            is_correct = False

            if selected_answer_id is not None:
                try:
                    selected_answer_id = int(selected_answer_id)
                    answer_obj = Answer.objects.get(id=selected_answer_id, question=question)
                    is_correct = answer_obj.is_correct
                except (Answer.DoesNotExist, ValueError):
                    is_correct = False

            UserAnswer.objects.create(
                submission=submission,
                question=question,
                answer_id=selected_answer_id,
                is_correct=is_correct
            )

            if is_correct:
                total_score += 1

        submission.score = total_score
        submission.save()

        return JsonResponse({
            "success": True,
            "redirect_url": f"/quiz/{quiz.id}/result/"
        })

    return JsonResponse({"success": False, "error": "Invalid request"})

@login_required
def quiz_result(request, quiz_id):
    submission = UserSubmission.objects.filter(quiz_id=quiz_id).order_by('-submitted_at').first()
    if not submission:
        return render(request, 'quiz_result.html', {
            'score': 0,
            'total': 0,
            'score_percentage': 0
        })

    total_questions = submission.quiz.questions.count()
    score_percentage = round((submission.score / total_questions) * 100)

    context = {
        'score': submission.score,
        'total': total_questions,
        'score_percentage': score_percentage
    }
    return render(request, 'quiz_result.html', context)


def event(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events.html', {'events': events})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('quizzes:login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})



def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        else:
            return redirect('/')

    if request.method == 'POST':
        identifier = request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')

    
        user = None

        user = authenticate(request, username=identifier, password=password)
        if user is None:
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('/')

        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'login.html')


def logout_view(request):
    auth_logout(request)
    return redirect('quizzes:home')

@login_required
def settings_view(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and confirm_password:
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()

                update_session_auth_hash(request, request.user)

                messages.success(request, "Password updated successfully")
                return redirect("quizzes:settings")
            else:
                messages.error(request, "Passwords do not match ")
        else:
            messages.error(request, "Please fill in both password fields ")

    return render(request, "settings.html")


@login_required
def profile(request):
    user = request.user 
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('quizzes:profile')  
    return render(request, 'profile.html', {'user': user})  
