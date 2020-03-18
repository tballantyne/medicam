from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('consultation/', views.consultation, name='consultation'),
    path('finish/', views.finish, name='finish'),
]
