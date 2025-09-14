from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'nouapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('contactus/', views.contactus, name='contactus'),
    path('courses/', views.courses, name='courses'),
    path('services/', views.services, name='services'),

    # 🔹 Forgot Password / Reset Password URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name="registration/password_reset_form.html",
             success_url=reverse_lazy('nouapp:password_reset_done')  # ✅ Add this
         ),
         name="password_reset"),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="registration/password_reset_done.html"
         ),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="registration/password_reset_confirm.html",
             success_url=reverse_lazy('nouapp:password_reset_complete')  # ✅ Optional
         ),
         name="password_reset_confirm"),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="registration/password_reset_complete.html"
         ),
         name="password_reset_complete"),
]
