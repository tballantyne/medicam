from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('consultation/', views.consultation, name='consultation'),
    path('finish/', views.finish, name='finish'),
    path('privacy/', TemplateView.as_view(template_name='clinic/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='clinic/terms.html'), name='terms'),
]
