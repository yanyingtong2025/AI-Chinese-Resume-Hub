from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('list/',views.resume_list,name='resume_list'),
    path('detail/<int:resume_id>/',views.resume_detail,name='resume_detail'),
    path('delete/<int:resume_id>/',views.delete_resume,name='delete_resume'),
    path('edit/<int:resume_id>/',views.edit_resume,name='edit_resume'),
    # 优化简历
    path('optimize/<int:resume_id>/',views.optimize_resume,name='optimize_resume'),
    path('generate-optimized/<int:resume_id>/',views.generate_optimized_resume,name='generate_optimized_resume'),
]