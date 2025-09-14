"""
URL configuration for nouproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from nouapp.views import set_theme, custom_404
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(('nouapp.nouappurls','nouapp'),namespace='nouapp')),
    path('studentapp/',include(('studentapp.studentappurls','studentapp'),namespace='studentapp')),
    path('adminapp/',include(('adminapp.adminappurls','adminapp'),namespace='adminapp')),
    path('set-theme/', set_theme, name='set-theme'),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

handler404 = custom_404
