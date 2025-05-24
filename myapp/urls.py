from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('skills/', views.skills_page, name='skills_page'),
    path('skills/delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('education/', views.education_manage, name='education_manage'),
    path('experience/', views.experience_manage, name='experience_manage'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/bookmark/', views.bookmark_job, name='bookmark_job'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('recommended-jobs/', views.recommended_jobs, name='recommended_jobs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
