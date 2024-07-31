from django.shortcuts import render,redirect
from django.views.generic import FormView,View
from .forms import UserForm,UserLogin
from django.contrib.auth import authenticate,login,logout
# Create your views here.



def home(request):
    return render(request,'index.html')


def Signup(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')
    else:
        form = UserForm()
    return render(request,'signup.html',{'form':form})

def Signin(request):
    if request.method=='POST':
        form = UserLogin(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
    else:
        form=UserLogin()
    return render(request,'signin.html',{'form':form})

    