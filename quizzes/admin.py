from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event, Contact
from django import forms
# ---------- Contact Admin ----------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)

    def has_delete_permission(self, request, obj=None):
        return False


# ---------- Quiz Admin ----------
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.submissions.exists():
            return False
        return True

admin.site.register(Quiz, QuizAdmin)


# ---------- Answer Formset with Validation ----------
class AnswerInlineFormset(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_answers = 0
        correct_answers = 0

        for form in self.forms:
            if form.cleaned_data.get('DELETE', False):
                continue
            total_answers += 1
            if form.cleaned_data.get('is_correct', False):
                correct_answers += 1

        if total_answers < 2:
            raise ValidationError("Each question must have at least 2 answers.")

        if correct_answers != 1:
            raise ValidationError("Each question must have exactly 1 correct answer.")


# ---------- Answer Inline ----------
class AnswerInline(admin.TabularInline):
    model = Answer
    formset = AnswerInlineFormset 
    extra = 2
    min_num = 2
    max_num = 4
    fields = ('text', 'is_correct')
# ---------- Question Admin ----------
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'question_type')
    search_fields = ('text',)
    inlines = [AnswerInline]

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Question, QuestionAdmin)


# ---------- UserSubmission Admin ----------
class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user_name','quiz','score','submitted_at')
    readonly_fields = ('user_name','quiz','score','submitted_at')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(UserSubmission, UserSubmissionAdmin)


# ---------- UserAnswer Admin ----------
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'answer', 'is_correct')
    readonly_fields = ('submission', 'question', 'answer', 'is_correct')

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(UserAnswer, UserAnswerAdmin)


# ---------- Event Admin ----------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')  
    search_fields = ('title',)
    list_filter = ('date',)
