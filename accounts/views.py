from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import RegistrationForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been created.')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    return render(request, 'accounts/login.html')

def logout(request):
    return render(request, 'accounts/logout.html')