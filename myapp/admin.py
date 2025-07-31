from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Profile, Skill, UserSkill, Experience, Education,
    Job, Bookmark, Application
)

# Inline for Profile in User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'profile__full_name', 'profile__phone_number')
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'phone_number', 'gender', 'age', 'status')  # Added status
    search_fields = ('user__username', 'full_name', 'email', 'phone_number', 'status')       # Added status
    list_filter = ('gender', 'highest_education_level', 'preferred_location', 'status')      # Added status


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name',)
    search_fields = ('skill_name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency_level', 'years_of_experience')
    list_filter = ('proficiency_level',)
    search_fields = ('user__username', 'skill__skill_name')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'company_name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('user__username', 'job_title', 'company_name')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'degree', 'institution', 'start_year', 'end_year')
    search_fields = ('user__username', 'degree', 'institution')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'job_type', 'location', 'is_remote', 'salary_min', 'salary_max', 'experience_level', 'status', 'posted_date')
    list_filter = ('job_type', 'is_remote', 'experience_level', 'status', 'posted_date')
    search_fields = ('title', 'location', 'description')
    filter_horizontal = ('skills',)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__username', 'job__title')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('user__username', 'job__title')
