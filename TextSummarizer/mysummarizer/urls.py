
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',home.as_view(),name='home'),
    path('signup/',Signup.as_view(),name='signup'),
]
