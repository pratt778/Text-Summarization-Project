from django.shortcuts import render,redirect
from django.views.generic import FormView,View
from .forms import UserForm,UserLogin
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .summarize import generate_summary
# Create your views here.



def home(request):
    if request.method=="POST":
        summary_test = request.POST.get('summary')
        summary = generate_summary(summary_test)
        print(summary)
        return render(request,'index.html',{'summary':summary})
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
        print('test')
        form = UserLogin(request,data=request.POST)
        print(form.is_valid())
        if form.is_valid():
            username=form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(username)
            print(password)
            user=authenticate(request,username=username,password=password)
            if user is not None:
                print('ok')
                login(request,user)
                messages.success(request, f'You have been logged in as {username}!')
                return redirect('home')
            else:
                 messages.error(request, 'Invalid username or password.')
    else:
        form=UserLogin()
    return render(request,'signin.html',{'form':form})

    
def Signout(request):
    logout(request)
    return redirect('home')