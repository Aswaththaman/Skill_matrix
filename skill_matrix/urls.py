"""
URL configuration for skill_matrix project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# from djangosaml2.views import LoginView, LogoutView
# from djangosaml2.views import AssertionConsumerServiceView, saml_authenticated_view


# from .views import CustomACSView  # Import the view
# from . import views

# from .views import CustomLoginView

from djangosaml2.views import AssertionConsumerServiceView
from .views import custom_logout_view
from django.contrib.auth import views as auth_views
from django.shortcuts import render

# from djangosaml2.views import AssertionConsumerService

def home_view(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('new_skill/', include('user_skills.urls')),


    # path('saml2/acs/', CustomACSView.as_view(), name='saml2_acs'),  # ACS endpoint
    # path('saml2/login/', views.custom_saml_login, name='saml_login'),

    # path('saml2/login/', CustomLoginView.as_view(), name='saml2_login'),

    # # Keep the default AssertionConsumerService view for handling the SAML response
    # path('saml2/acs/', AssertionConsumerService.as_view(), name='saml2_acs'),
    # path('saml2/login/', CustomLoginView.as_view(), name='saml2_login'),
    # path('saml2/acs/', AssertionConsumerServiceView.as_view(), name='saml2_acs'),



    path('saml2/', include('djangosaml2.urls')),
    path('logout/', custom_logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

]
