from django.urls import path
from . import views

app_name = "nouapp"

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('contactus/', views.contactus, name='contactus'),
    path('courses/', views.courses, name='courses'),
    path('services/', views.services, name='services'),
     path('resources/', views.resources, name='resources'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('chat/', views.chat_api, name='chat_api'),  # added from other branch,
    path('search/', views.search_view, name='search'),
    path('faqs/', views.faqs, name='faqs')
]

