from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'address']




from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Profile
        fields = [
            'full_name', 'email', 'age', 'gender', 'phone_number', 'address',
            'profile_picture', 'resume_path', 'bio', 'summary',
            'current_job_title', 'current_company', 'years_of_experience',
            'highest_education_level', 'preferred_location', 'expected_salary'
        ]


from django import forms
from .models import UserSkill , Education

class UserSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['skill', 'proficiency_level', 'years_of_experience']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-control'}),
            'proficiency_level': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_year', 'end_year']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        if end_year and end_year < start_year:
            raise forms.ValidationError("End year cannot be before start year.")




from django import forms
from .models import Experience

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company_name', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        if not is_current and not end_date:
            raise forms.ValidationError("End date is required if not currently employed.")
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
