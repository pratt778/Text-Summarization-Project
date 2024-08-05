from django.shortcuts import render,redirect
from django.views.generic import FormView,View
from .forms import UserForm,UserLogin
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from rouge import Rouge
from .summarize import AdvancedTextRankSummarizer
# Create your views here.



# Initialize the summarizer once
summarizer = AdvancedTextRankSummarizer()

def home(request):
    if request.method == "POST":
        summary_test = request.POST.get('summary')
        reference_summary = request.POST.get('reference_summary')  # Assuming you have a field for reference summary
        if summary_test:
            try:
                summary, keywords = summarizer.summarize(summary_test, num_sentences=5, num_keywords=5)
                context = {'summary': summary, 'keywords': keywords}
                
                # Evaluate with ROUGE if reference summary is provided
                if reference_summary:
                    rouge = Rouge()
                    scores = rouge.get_scores(summary, reference_summary)
                    context['rouge_scores'] = scores
            except Exception as e:
                context = {'error': str(e)}
        else:
            context = {'error': 'No text provided for summarization.'}
        
        return render(request, 'index.html', context)
    
    return render(request, 'index.html')

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