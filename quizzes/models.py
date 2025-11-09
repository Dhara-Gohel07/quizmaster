from django.db import models

#Contact model to store contact form submissions
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
# Quiz model to store quizzes, questions, answers, and user submissions
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Question model to store questions related to quizzes
class Question(models.Model):
    QUESTION_TYPES = (('mcq', 'Multiple Choice'), ('tf', 'True/False'))
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES,default='mcq')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz.title} - {self.text[:50]}"
    
# Answer model to store answers related to questions   
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.text[:60]}"

# UserSubmission model to store user quiz submissions   
class UserSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    user_name = models.CharField(max_length=200)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.quiz.title} - {self.score}"

# UserAnswer model to store answers selected by users in their submissions
class UserAnswer(models.Model):
    submission = models.ForeignKey(UserSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question,related_name='user_answers', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Submission {self.submission.id} - Q{self.question.id}"

# Event model to store events
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} - {self.date}"