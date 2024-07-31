from django.shortcuts import render
from django.views.generic import FormView,View
from .forms import UserForm
# Create your views here.



class home(View):
    def get(self,request):
        return render(request,'index.html')
    
class Signup(FormView):
    template_name='signup.html'
    form_class=UserForm
    def form_valid(self,form):
        form.save()

    