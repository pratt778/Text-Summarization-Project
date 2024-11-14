from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, View
from .forms import UserForm, UserLogin
from django.contrib import messages
from urllib.parse import urlencode
from django.contrib.auth import authenticate, login, logout
from .summarize import AdvancedTextRankSummarizer
from .models import UserHistory
from django.contrib.auth.models import User
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize summarizer once globally to avoid reinitializing on each request
summarizer = AdvancedTextRankSummarizer()

def index(request):
    return render(request,"homepage.html")

def home(request):
    if request.method == "POST":
        summary_text = request.POST.get('summary')
        summary_num = int(request.POST.get('rangeInput', 0))

        if not summary_text:
            return render(request, 'summary.html', {'error': 'No text provided for summarization.'})

        text_length = len(summary_text.split())
        sentence_count = summarizer.findsentlen(summary_text)

        if not request.user.is_authenticated and text_length > 350:
            message = f"The text is {text_length} words! Use text less than 350 words."
            return render(request, 'summary.html', {'message': message})
        
        if sentence_count<3:
            message=f"Input At least 3 sentences to get a proper summary"
            return render(request,"summary.html",{'message':message})

        try:
            title, summary, keywords = summarizer.summarize(summary_text, num_sentences=summary_num, num_keywords=5)

            context = {
                'summary': summary,
                'keywords': keywords,
                'title': title,
                'text': summary_text,
                'length': text_length,
                'sentcount':sentence_count,
                'summary_num': summary_num,
            }

            if request.user.is_authenticated:
                UserHistory.objects.create(
                    user=request.user,
                    summary_text=summary,
                    generated_text=summary_text,
                    summary_title=title,
                    summary_keywords=", ".join(keywords)
                )
            return render(request, 'summary.html', context)

        except Exception as e:
            return render(request, 'summary.html', {'error': str(e)})

    return render(request, 'summary.html')

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = UserLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You have been logged in as {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLogin()
    return render(request, 'signin.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('home')

def user_history(request, id):
    if request.user.is_authenticated and request.user.id == id:
        myhistory = UserHistory.objects.filter(user=request.user)
        return render(request, 'userhistory.html', {'history': myhistory})
    return redirect('signin')

def summary_user(request, pk):
    mysummary = get_object_or_404(UserHistory, pk=pk, user=request.user)
    data = {
        'text': mysummary.generated_text,
        'summary': mysummary.summary_text,
        'keywords': mysummary.summary_keywords,
        'title': mysummary.summary_title,
        'length': len(mysummary.generated_text.split()),
        'created_at': mysummary.created_at
    }
    return render(request, 'summarydetail.html', data)

def delete_summary(request, pk):
    summary = get_object_or_404(UserHistory, pk=pk, user=request.user)
    summary.delete()
    return redirect("userhistory", request.user.id)

def search_titles(query, titles):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([query] + titles)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    related_indices = np.argsort(-cosine_similarities)
    return [titles[i] for i in related_indices]

def search(request):
    query = request.GET.get('search')
    if not query:
        return redirect('userhistory', request.user.id)

    
    summaries = UserHistory.objects.filter(user=request.user)
    titles = [summary.summary_title for summary in summaries]

    if titles:
        results = search_titles(query, titles)  
        sorted_summaries = sorted(summaries, key=lambda x: results.index(x.summary_title))
        return render(request, 'userhistory.html', {'history': sorted_summaries[:5],'highlight':True})
    return render(request, 'userhistory.html', {'history': summaries})



