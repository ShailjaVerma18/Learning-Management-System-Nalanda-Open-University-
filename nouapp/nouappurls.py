from django.urls import path
from . import views
from .views import StudentListCreateView, StudentRetrieveUpdateDestroyView


app_name = "nouapp"

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('contactus/', views.contactus, name='contactus'),
    path('courses/', views.courses, name='courses'),
    path('services/', views.services, name='services'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('api/students/', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('api/students/<int:rollno>/', views.StudentRetrieveUpdateDestroyView.as_view(), name='student-detail'),
    path('chat/', views.chat_api, name='chat_api'),  # added from other branch
]
