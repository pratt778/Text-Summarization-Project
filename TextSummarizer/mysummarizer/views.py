from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import FormView,View
from .forms import UserForm,UserLogin
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from rouge import Rouge
from .summarize import AdvancedTextRankSummarizer
from .models import UserHistory
from django.contrib.auth.models import User





summarizer = AdvancedTextRankSummarizer()



def home(request):
    if request.method == "POST":
        summary_text = request.POST.get('summary')
        # reference_summary = request.POST.get('reference_summary')

        if not summary_text:
            return render(request, 'index.html', {'error': 'No text provided for summarization.'})

        if not request.user.is_authenticated and len(summary_text.split()) > 350:
            message = f"The text is {len(summary_text.split())} words! Use text less than 350 words."
            return render(request, 'index.html', {'message': message})

        try:
            text_length=len(summary_text.split())
            title, summary, keywords = summarizer.summarize(summary_text, num_sentences=5, num_keywords=5)
            
            context = {
                'summary': summary,
                'keywords': keywords,
                'title': title,
                'text': summary_text,
                'length':text_length,
            }

            if request.user.is_authenticated:
                UserHistory.objects.create(
                    user=request.user,
                    summary_text=summary,
                    generated_text=summary_text,
                    summary_title=title,
                    summary_keywords=", ".join(keywords)
                )
            return render(request, 'index.html', context)

        except Exception as e:
            return render(request, 'index.html', {'error': str(e)})

    return render(request, 'index.html')

# ... (other views remain the same)
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

def Userhistory(request,id):
    data={}
    user=User.objects.get(pk=id)
    if user==request.user:
        myhistory = UserHistory.objects.filter(user=user)
        data['history']=myhistory
    else:
        return redirect('signin')
    return render(request,'userhistory.html',data)


def summaryuser(request,pk):
    data={}
    mysummary= get_object_or_404(UserHistory,pk=pk)
    if mysummary.user == request.user:
        data['text']=mysummary.generated_text
        data['summary']=mysummary.summary_text
        data['keywords']=mysummary.summary_keywords
        data['title']=mysummary.summary_title
        data['length']=len(mysummary.generated_text.split())
        data['created_at']=mysummary.created_at
    else:
        return redirect('signin')
    return render(request,'summarydetail.html',data)

def deletesummary(request,pk):
    summary=UserHistory.objects.get(pk=pk)
    if summary.user==request.user:
        summary.delete()
    else:
        return redirect("signin")
    return redirect("userhistory",summary.user.id)