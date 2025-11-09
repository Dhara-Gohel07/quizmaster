from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/attempt/', views.quiz_attempt, name='quiz_attempt'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('events/', views.event, name='events'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path("settings/", views.settings_view, name="settings"),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
]
