from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Profile , UserSkill
from .forms import ProfileForm  , RegistrationForm , UserSkillForm
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from django.db.models import Q
from .models import Job

def index(request):
    jobs = Job.objects.filter(status='active').order_by('-posted_date')
    
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(requirements__icontains=keyword) |
            Q(responsibilities__icontains=keyword)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        if job_type == 'remote':
            jobs = jobs.filter(is_remote=True)
        else:
            jobs = jobs.filter(job_type=job_type)
    
    # Filter salary_min (job salary_min >= filter salary_min)
    if salary_min:
        try:
            salary_min_val = float(salary_min)
            jobs = jobs.filter(salary_min__gte=salary_min_val)
        except ValueError:
            pass

    # Filter salary_max (job salary_max <= filter salary_max)
    if salary_max:
        try:
            salary_max_val = float(salary_max)
            jobs = jobs.filter(salary_max__lte=salary_max_val)
        except ValueError:
            pass
    
    context = {
        'jobs': jobs[:12],  # first 12 results
        'filters': {
            'keyword': keyword,
            'location': location,
            'job_type': job_type,
            'salary_min': salary_min,
            'salary_max': salary_max,
        }
    }
    return render(request, 'index.html', context)


from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = False  # prevent login until verified
            user.save()

            # Create profile with status = Pending
            phone = form.cleaned_data['phone_number']
            addr = form.cleaned_data['address']
            profile = Profile.objects.create(user=user, email=user.email, phone_number=phone, address=addr)

            # Send verification email
            verify_url = request.build_absolute_uri(reverse('verify_email', args=[user.username]))
            send_mail(
                subject='Verify Your Email',
                message=f'Click the link to verify your email: {verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, 'Registration successful! Please verify your email to activate your account.')
            return redirect('user_login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib.auth.models import User  # make sure this import is at the top

def verify_email(request, username):
    try:
        user_obj = User.objects.get(username=username)
        profile = Profile.objects.get(user=user_obj)
        profile.status = 'Approved'
        profile.save()
        user_obj.is_active = True
        user_obj.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('user_login')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                profile = Profile.objects.get(user=user)
                if profile.status != 'Approved':
                    messages.error(request, 'Account not approved. Please verify your email.')
                else:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile
from .forms import ProfileForm

@login_required
def update_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('update_profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'update_profile.html', {
        'form': form,
        'user_profile': profile
    })


@login_required
def view_profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'view_profile.html', {'user_profile': user_profile})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('user_login')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from .models import Job  # Import your Job model

from django.utils.timezone import now, timedelta

@login_required
def dashboard(request):
    jobs = Job.objects.filter(status='active', expiration_date__gte=date.today())

    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    min_salary = request.GET.get('min_salary', '')
    max_salary = request.GET.get('max_salary', '')

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(requirements__icontains=keyword) |
            Q(responsibilities__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if min_salary.isdigit():
        jobs = jobs.filter(salary_max__gte=int(min_salary))
    if max_salary.isdigit():
        jobs = jobs.filter(salary_min__lte=int(max_salary))

    # Count jobs posted in last 7 days as new jobs example
    one_week_ago = now() - timedelta(days=7)
    new_jobs_count = Job.objects.filter(posted_date__gte=one_week_ago, status='active').count()

    context = {
        'jobs': jobs,
        'filters': {
            'keyword': keyword,
            'location': location,
            'min_salary': min_salary,
            'max_salary': max_salary,
        },
        'new_jobs_count': new_jobs_count,
    }
    return render(request, 'dashboard.html', context)



from django.shortcuts import get_object_or_404, render
from .models import Job

from datetime import date

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {
        'job': job,
        'today': date.today()
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Job, Bookmark, Application

@login_required
def bookmark_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    Bookmark.objects.get_or_create(user=request.user, job=job)
    messages.success(request, "Job bookmarked.")
    return redirect('job_detail', job_id=job_id)

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.status != 'active' or job.expiration_date < timezone.now().date():
        messages.warning(request, "You cannot apply for this job.")
        return redirect('job_detail', job_id=job_id)
    
    Application.objects.get_or_create(user=request.user, job=job)
    messages.success(request, "Application submitted.")
    return redirect('job_detail', job_id=job_id)



@login_required
def skills_page(request):
    user = request.user
    skills = UserSkill.objects.filter(user=user)
    edit_skill = None

    # Check if editing existing skill
    edit_skill_id = request.GET.get('edit')
    if edit_skill_id:
        edit_skill = get_object_or_404(UserSkill, id=edit_skill_id, user=user)

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        if skill_id:
            instance = get_object_or_404(UserSkill, id=skill_id, user=user)
            form = UserSkillForm(request.POST, instance=instance)
        else:
            form = UserSkillForm(request.POST)

        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = user
            skill.save()
            return redirect('skills_page')
    else:
        form = UserSkillForm(instance=edit_skill)

    context = {
        'form': form,
        'skills': skills,
        'edit_skill': edit_skill,
    }
    return render(request, 'skills_page.html', context)


@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    if request.method == 'POST':
        skill.delete()
        return redirect('skills_page')
    return redirect('skills_page')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Experience , Education
from .forms import ExperienceForm , EducationForm

@login_required
def experience_manage(request):
    user = request.user
    experiences = Experience.objects.filter(user=user).order_by('-start_date')
    experience_id = request.GET.get('edit')  # for edit

    if experience_id:
        experience_instance = get_object_or_404(Experience, id=experience_id, user=user)
    else:
        experience_instance = None

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete_id = request.POST.get('delete_id')
            exp_to_delete = get_object_or_404(Experience, id=delete_id, user=user)
            exp_to_delete.delete()
            return redirect('experience_manage')
        
        form = ExperienceForm(request.POST, instance=experience_instance)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = user
            exp.save()
            return redirect('experience_manage')
    else:
        form = ExperienceForm(instance=experience_instance)

    return render(request, 'experience_manage.html', {
        'form': form,
        'experiences': experiences,
        'editing_id': experience_id
    })


@login_required
def education_manage(request):
    user = request.user
    educations = Education.objects.filter(user=user).order_by('-start_year')
    education_id = request.GET.get('edit')

    if education_id:
        education_instance = get_object_or_404(Education, id=education_id, user=user)
    else:
        education_instance = None

    if request.method == 'POST':
        if 'delete' in request.POST:
            delete_id = request.POST.get('delete_id')
            edu_to_delete = get_object_or_404(Education, id=delete_id, user=user)
            edu_to_delete.delete()
            return redirect('education_manage')
        
        form = EducationForm(request.POST, instance=education_instance)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = user
            edu.save()
            return redirect('education_manage')
    else:
        form = EducationForm(instance=education_instance)

    return render(request, 'education_manage.html', {
        'form': form,
        'educations': educations,
        'editing_id': education_id
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Bookmark

@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.select_related('job').filter(user=request.user)
    return render(request, 'my_bookmarks.html', {'bookmarks': bookmarks})


from .models import Application

@login_required
def my_applications(request):
    applications = Application.objects.select_related('job').filter(user=request.user)
    return render(request, 'my_applications.html', {'applications': applications})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .recommendations import get_recommended_jobs

@login_required
def recommended_jobs(request):
    recommendations = get_recommended_jobs(request.user)
    jobs_with_reasons = [{'job': rec[0], 'reasons': rec[2]} for rec in recommendations]
    context = {
        'recommended_jobs': jobs_with_reasons,
    }
    return render(request, 'recommended_jobs.html', context)
