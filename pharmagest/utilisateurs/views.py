from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .forms import LoginForm


class CustomLoginView(LoginView):
    template_name = 'utilisateurs/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


@login_required
def deconnexion(request):
    logout(request)
    return redirect('utilisateurs:login')