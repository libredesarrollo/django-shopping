import logging
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        logger.error(f"Test Log:", exc_info=True)
        context = super().get_context_data(**kwargs)
        context['lang_code'] = 'en'