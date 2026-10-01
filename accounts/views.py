from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from .forms import RegistrationForm

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            authenticated_user = authenticate(
                request,
                username=user.email,
                password=form.cleaned_data['password'],
            )
            if authenticated_user is not None:
                auth_login(request, authenticated_user)

            messages.success(request, 'Your account has been created.')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})