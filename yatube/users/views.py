from .form import CreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
