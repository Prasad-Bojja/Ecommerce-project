from django.contrib import admin
from django.urls import path,include
from .views import*
from authentications import views

urlpatterns = [
    path('signup/',register,name='signup'),
    path('login/',login_form,name='login'),
    path('logout/',logout_page,name='logout'),
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    path('forget_password/', forgetPassword, name='forget_password'),
    path('change_password/<token>/',change_password,name='change_password'),
    
    
]
