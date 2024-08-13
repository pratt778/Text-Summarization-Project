
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('signup/',Signup,name='signup'),
    path('signin/',Signin,name='signin'),
    path('signout/',Signout,name='signout'),
    path('userhistory/<int:id>',Userhistory,name='userhistory'),
    path('summarydetail/<int:pk>',summaryuser,name='summarydetail'),
    path('deletesummary/<int:pk>',deletesummary,name='deletesummary'),
    path('search',search,name="searchquery"),
]
