# LMS/models.py

from django.db import models
from django.utils import timezone


class Subject(models.Model):
    subject_id = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, blank=True)
    course = models.ForeignKey('ERP.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    # faculty = models.ForeignKey(
    #     'faculty.Staff', on_delete=models.SET_NULL,
    #     null=True, blank=True, related_name='subjects_taught'
    # )
    faculty = models.ForeignKey(
        'faculty.Staff',
        on_delete=models.CASCADE,
        related_name='subjects', null=True,
        blank=True
    )
    department = models.ForeignKey(
        'account.Department', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    semester = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject_name']

    def __str__(self):
        return f"{self.subject_name} ({self.subject_id})"


class Unit(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.subject.subject_name} - Unit {self.order}: {self.title}"


class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='lessons/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.unit.subject.subject_name} - {self.title}"


class Notes(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    uploaded_by = models.ForeignKey('faculty.Staff', on_delete=models.CASCADE, related_name='notes_uploaded')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notes'

    def __str__(self):
        return f"{self.subject.subject_name} - {self.title}"


class Assignment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey('faculty.Staff', on_delete=models.CASCADE, related_name='assignments_created')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject.subject_name}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def submission_count(self):
        return self.submissions.count()


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late Submission'),
        ('resubmit', 'Needs Resubmission'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    notes = models.TextField(blank=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"


class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    created_by = models.ForeignKey('faculty.Staff', on_delete=models.CASCADE, related_name='quizzes_created')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_marks = models.PositiveIntegerField(default=10)
    duration_minutes = models.PositiveIntegerField(default=30)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.title} - {self.subject.subject_name}"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey('account.Student', on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('quiz', 'student')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title} ({self.score})"
