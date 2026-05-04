from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_job, name='create_job'),
    path('detail/<int:job_id>/',views.job_detail, name='job_detail'),
    path('list/', views.job_list, name='job_list'),
    path('edit/<int:job_id>/',views.edit_job, name='edit_job'),
    # 投递相关
    path('apply/<int:job_id>/',views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:job_id>', views.job_applications, name='job_applications'),
    path('update-application/<int:application_id>/',views.update_application_status, name='update_application_status'),
    # HR匹配简历
    path('match/<int:job_id>/',views.start_matching, name='start_matching'),
    path('match-detail/<int:match_id>/',views.match_detail, name='match_detail'),
    path('match-results/<int:job_id>', views.match_results, name='match_results'),
    path('update-status/<int:job_id>/',views.update_match_status, name='update_match_status'),
    # 求职者匹配岗位
    path('matched-jobs/', views.matched_jobs, name='matched_jobs'),
]