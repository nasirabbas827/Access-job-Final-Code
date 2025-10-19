from django.db.models import Q
from datetime import date
from .models import Job, UserSkill, Profile, Experience, Education
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def get_recommended_jobs(user, max_results=10):
    try:
        # Fetch user data
        profile = Profile.objects.get(user=user)
        user_skills = UserSkill.objects.filter(user=user).select_related('skill')
        user_experiences = Experience.objects.filter(user=user)
        user_educations = Education.objects.filter(user=user)

        # Get active jobs not expired, prefetch skills
        jobs = Job.objects.filter(
            status='active',
            expiration_date__gte=date.today()
        ).prefetch_related('skills')

        # Prepare text data for TF-IDF (content-based filtering)
        user_texts = []
        job_texts = []
        
        # Build user profile text from specified fields only
        user_text = []
        if profile.current_job_title:
            user_text.append(profile.current_job_title)
        if profile.summary:
            user_text.append(profile.summary)
        # Add skills multiple times based on proficiency to boost importance
        for skill in user_skills:
            skill_text = skill.skill.skill_name
            if skill.proficiency_level == 'expert':
                user_text.extend([skill_text] * 3)  # Boost expert skills
            elif skill.proficiency_level == 'intermediate':
                user_text.extend([skill_text] * 2)  # Boost intermediate skills
            else:
                user_text.append(skill_text)
        user_text.extend(exp.job_title + " " + (exp.description or "") for exp in user_experiences)
        user_text.extend(edu.degree + " " + edu.institution for edu in user_educations)
        user_texts.append(" ".join(user_text).lower())

        # Build job texts from relevant job fields
        job_id_to_index = {}
        for idx, job in enumerate(jobs):
            job_text = [job.title, job.description, job.requirements or "", job.responsibilities or ""]
            job_text.extend([skill.skill_name] * 2 for skill in job.skills.all())  # Boost job skills
            job_texts.append(" ".join(job_text).lower())
            job_id_to_index[job.id] = idx

        # Compute TF-IDF vectors and cosine similarity
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))
        job_vectors = tfidf.fit_transform(job_texts)
        user_vector = tfidf.transform(user_texts)
        cosine_similarities = cosine_similarity(user_vector, job_vectors).flatten()

        recommendations = []

        for job in jobs:
            match_score = 0
            reasons = []
            job_idx = job_id_to_index[job.id]
            tfidf_score = cosine_similarities[job_idx]
            if tfidf_score < 0.1:  # Filter out very low similarity scores
                continue
            match_score += tfidf_score * 8  # Increase TF-IDF weight for stronger content influence

            # Skill matching
            job_skill_ids = {skill.id for skill in job.skills.all()}
            matched_skills = []
            for user_skill in user_skills:
                if user_skill.skill.id in job_skill_ids:
                    matched_skills.append(user_skill.skill.skill_name)
                    match_score += 2  # Higher weight for skill matches
                    if user_skill.proficiency_level == 'expert':
                        match_score += 1.5
                        reasons.append(f"Expert in {user_skill.skill.skill_name}")
                    elif user_skill.proficiency_level == 'intermediate':
                        match_score += 0.75
                        reasons.append(f"Intermediate in {user_skill.skill.skill_name}")
                    else:
                        reasons.append(f"Beginner in {user_skill.skill.skill_name}")

            if matched_skills:
                reasons.append(f"Matched skills: {', '.join(matched_skills)}")

            # Education match
            if user_educations.exists():
                job_requirements = (job.requirements or "").lower()
                for education in user_educations:
                    degree = education.degree.lower()
                    institution = education.institution.lower()
                    if degree in job_requirements or institution in job_requirements:
                        match_score += 1.5
                        reasons.append(f"Education matches: {education.degree} from {education.institution}")
                        break

            # Experience match
            if user_experiences.exists():
                user_job_titles = {exp.job_title.lower() for exp in user_experiences if exp.job_title}
                job_title_words = job.title.lower().split()
                matched_titles = [word for word in job_title_words if word in user_job_titles]
                if matched_titles:
                    match_score += 1.5
                    reasons.append(f"Experience matches: {', '.join(matched_titles)}")

            # Location match
            if profile.preferred_location == 'remote' and job.is_remote:
                match_score += 2
                reasons.append("Matches preferred remote work")
            elif profile.preferred_location == 'onsite' and not job.is_remote:
                match_score += 1
                reasons.append("Matches preferred onsite work")

            # Salary match
            if profile.expected_salary and job.salary_min and job.salary_max:
                try:
                    # Extract numeric value from expected_salary (e.g., "$50,000" -> 50000)
                    expected_salary = float(re.sub(r'[^\d.]', '', profile.expected_salary))
                    if job.salary_min <= expected_salary <= job.salary_max:
                        match_score += 2
                        reasons.append("Salary matches your expectations")
                except ValueError:
                    pass  # Skip if expected_salary format is invalid

            if match_score > 0:
                reasons.append(f"Content similarity score: {tfidf_score:.2f}")
                recommendations.append((job, match_score, reasons))

        # Sort by match score descending and limit results
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:max_results]

    except Profile.DoesNotExist:
        return []