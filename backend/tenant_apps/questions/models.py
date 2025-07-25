from django.db import models
from public_apps.tenants.models import TenantUser
import uuid


class QuestionCategory(models.Model):
    """Categories for organizing questions - isolated by schema"""
    
    # No tenant FK needed - isolation is at schema level
    name = models.CharField(max_length=100, unique=True)  # Unique within tenant schema
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_categories'
    
    def __str__(self):
        return self.name


class Question(models.Model):
    """Question model supporting multiple types - isolated by schema"""
    
    TYPE_CHOICES = [
        ('coding', 'Coding'),
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text/Essay'),
        ('system_design', 'System Design'),
        ('behavioral', 'Behavioral'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # No tenant FK needed - isolation is at schema level
    created_by = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='created_questions')
    
    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.ForeignKey(QuestionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timing
    time_limit = models.IntegerField(help_text="Time limit in minutes", null=True, blank=True)
    
    # Tags and metadata
    tags = models.JSONField(default=list, blank=True)
    skills_assessed = models.JSONField(default=list, blank=True)
    
    # Question-specific data
    question_data = models.JSONField(default=dict, help_text="Question-specific configuration")
    
    # Grading configuration
    max_score = models.IntegerField(default=100)
    auto_grade = models.BooleanField(default=True)
    grading_criteria = models.JSONField(default=dict, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Can be used by other tenants
    
    # Analytics
    times_used = models.IntegerField(default=0)
    average_score = models.FloatField(null=True, blank=True)
    average_completion_time = models.IntegerField(null=True, blank=True)  # in seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        indexes = [
            models.Index(fields=['question_type']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_question_type_display()})"


class CodingQuestion(models.Model):
    """Additional data for coding questions"""
    
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='coding_data')
    
    # Programming language support
    allowed_languages = models.JSONField(default=list)  # ['python', 'javascript', 'java']
    default_language = models.CharField(max_length=20, default='python')
    
    # Code templates
    starter_code = models.JSONField(default=dict)  # {language: code}
    solution_code = models.JSONField(default=dict)  # {language: code}
    
    # Test cases
    test_cases = models.JSONField(default=list)
    hidden_test_cases = models.JSONField(default=list)
    
    # Execution settings
    memory_limit = models.IntegerField(default=256)  # MB
    execution_time_limit = models.IntegerField(default=10)  # seconds
    
    # Solution validation
    expected_complexity = models.CharField(max_length=100, blank=True)
    keywords_required = models.JSONField(default=list)
    keywords_forbidden = models.JSONField(default=list)
    
    class Meta:
        db_table = 'coding_questions'


class MultipleChoiceQuestion(models.Model):
    """Additional data for multiple choice questions"""
    
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='mcq_data')
    
    # Options and answers
    options = models.JSONField(default=list)  # [{"id": "A", "text": "Option A", "is_correct": true}]
    allow_multiple = models.BooleanField(default=False)
    randomize_options = models.BooleanField(default=True)
    
    # Explanation
    explanation = models.TextField(blank=True)
    explanation_media = models.FileField(upload_to='question_explanations/', null=True, blank=True)
    
    class Meta:
        db_table = 'multiple_choice_questions'


class QuestionSet(models.Model):
    """Collection of questions for interviews - isolated by schema"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # No tenant FK needed - isolation is at schema level
    created_by = models.ForeignKey(TenantUser, on_delete=models.CASCADE, related_name='created_question_sets')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Questions in this set
    questions = models.ManyToManyField(Question, through='QuestionSetItem')
    
    # Configuration
    total_time_limit = models.IntegerField(null=True, blank=True)  # Total time for all questions
    randomize_questions = models.BooleanField(default=False)
    max_questions = models.IntegerField(null=True, blank=True)  # Limit number of questions shown
    
    # Usage tracking
    times_used = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_sets'
    
    def __str__(self):
        return self.name


class QuestionSetItem(models.Model):
    """Through model for questions in a set with ordering"""
    
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_required = models.BooleanField(default=True)
    weight = models.FloatField(default=1.0)  # Weight for scoring
    
    class Meta:
        db_table = 'question_set_items'
        unique_together = ['question_set', 'question']
        ordering = ['order']
