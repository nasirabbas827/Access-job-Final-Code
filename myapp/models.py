from django.db import models
from django.contrib.auth.models import User
from django.core import validators

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    EDUCATION_CHOICES = [
        ('High School', 'High School'),
        ('Diploma', 'Diploma'),
        ("Bachelor's", "Bachelor's"),
        ("Master's", "Master's"),
        ('PhD', 'PhD'),
    ]

    LOCATION_PREFERENCE_CHOICES = [
        ('onsite', 'Onsite'),
        ('remote', 'Remote'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    age = models.IntegerField(default=None, blank=True, null=True,
                              validators=[validators.MinValueValidator(0)])
    phone_number = models.CharField(
        max_length=20,
        default="",
        blank=True,
        null=True,
        validators=[
            validators.RegexValidator(regex='^[0-9]*$', message='Enter a valid phone number.', code='invalid_number')
        ]
    )
    address = models.TextField(default="", blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    resume_path = models.FileField(upload_to='resumes/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # New Fields
    summary = models.TextField(blank=True, null=True)
    current_job_title = models.CharField(max_length=100, blank=True, null=True)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    highest_education_level = models.CharField(max_length=50, choices=EDUCATION_CHOICES, blank=True, null=True)
    preferred_location = models.CharField(max_length=10, choices=LOCATION_PREFERENCE_CHOICES, blank=True, null=True)
    expected_salary = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username




from django.db import models

class Skill(models.Model):
    skill_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.skill_name



class UserSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)
    years_of_experience = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.skill.skill_name}"


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
    
class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=150)
    institution = models.CharField(max_length=150)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} from {self.institution}"

    

from django.db import models
from django.utils import timezone

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
        # add more if needed
    ]

    SALARY_TYPE_CHOICES = [
        ('annual', 'Annual'),
        ('hourly', 'Hourly'),
        ('monthly', 'Monthly'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('filled', 'Filled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=10, default='USD')  # adjust default if needed
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    posted_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateField(blank=True, null=True)
    application_deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return self.title



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.job.title}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('in_review', 'In Review'),
        ('interview', 'Interview'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} applied for {self.job.title}"
