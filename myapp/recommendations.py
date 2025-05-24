from .models import Job, UserSkill, Profile, Experience
from django.db.models import Q
from datetime import date

from .models import Job, UserSkill, Profile, Experience
from datetime import date

def get_recommended_jobs(user, max_results=10):
    try:
        profile = Profile.objects.get(user=user)
        user_skills = UserSkill.objects.filter(user=user).select_related('skill')
        user_experiences = Experience.objects.filter(user=user)

        # Get active jobs not expired, prefetch skills
        jobs = Job.objects.filter(
            status='active',
            expiration_date__gte=date.today()
        ).prefetch_related('skills')

        recommendations = []

        for job in jobs:
            match_score = 0
            reasons = []

            # Get skill IDs for this job
            job_skill_ids = {skill.id for skill in job.skills.all()}

            matched_skills = []
            for user_skill in user_skills:
                if user_skill.skill.id in job_skill_ids:
                    matched_skills.append(user_skill.skill.skill_name)
                    # Score increment for skill match
                    match_score += 1
                    # Bonus for proficiency
                    if user_skill.proficiency_level == 'expert':
                        match_score += 1
                    elif user_skill.proficiency_level == 'intermediate':
                        match_score += 0.5

            if matched_skills:
                reasons.append(f"Matched skills: {', '.join(matched_skills)}")

            # Location match
            if profile.preferred_location == 'remote' and job.is_remote:
                match_score += 2
                reasons.append("Preferred remote job and job is remote")
            elif profile.preferred_location == 'onsite' and not job.is_remote:
                match_score += 1
                reasons.append("Preferred onsite job and job is onsite")

            # Experience level match based on profile years_of_experience
            if profile.years_of_experience is not None:
                yoe = profile.years_of_experience
                if job.experience_level == 'entry' and yoe < 2:
                    match_score += 1
                    reasons.append("Experience matches entry level")
                elif job.experience_level == 'mid' and 2 <= yoe <= 5:
                    match_score += 1
                    reasons.append("Experience matches mid level")
                elif job.experience_level == 'senior' and yoe > 5:
                    match_score += 1
                    reasons.append("Experience matches senior level")

            # Match job title with past experiences
            if user_experiences.exists():
                user_job_titles = {exp.job_title.lower() for exp in user_experiences if exp.job_title}
                job_title_words = job.title.lower().split()
                if any(word in user_job_titles for word in job_title_words):
                    match_score += 1
                    reasons.append("Job title similar to your past experience")

            # Only add jobs with some positive match score
            if match_score > 0:
                recommendations.append((job, match_score, reasons))

        # Sort by match score descending and limit results
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:max_results]

    except Profile.DoesNotExist:
        # No profile, no recommendations
        return []
