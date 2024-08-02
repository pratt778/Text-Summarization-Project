
from django.urls import path,include
from .views import *

urlpatterns = [
    path('summarize/',home,name='home'),
    path('signup/',Signup,name='signup'),
    path('signin/',Signin,name='signin'),
    path('signout/',Signout,name='signout')
]
