from django.contrib import admin
from .models import Subject, Assignment, AssignmentSubmission, Notes, Quiz, QuizQuestion, QuizAttempt, Unit, Lesson

admin.site.register(Subject)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Notes)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizAttempt)
admin.site.register(Unit)
admin.site.register(Lesson)
