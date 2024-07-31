
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('signup/',Signup,name='signup'),
    path('signin/',Signin,name='signin'),
]
