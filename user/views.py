from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lang_code'] = 'en'