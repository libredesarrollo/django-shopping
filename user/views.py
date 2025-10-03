# import logging
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

# logger = logging.getLogger(__name__)

from django.shortcuts import redirect
from django.views import View

class ToggleThemeView(View):
    def post(self, request, *args, **kwargs):
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            request.session['theme'] = theme
        return redirect(request.META.get('HTTP_REFERER', 'user.profile'))

    # def get(self, request, *args, **kwargs):
    #     # Mantenemos el GET para compatibilidad o si se usa un enlace simple
    #     current_theme = request.session.get('theme', 'light')
    #     new_theme = 'dark' if current_theme == 'light' else 'light'
    #     request.session['theme'] = new_theme

    #     # Redirigir a la página anterior o a la página de inicio
    #     return redirect(request.META.get('HTTP_REFERER', '/'))

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        # logger.error(f"Test Log:", exc_info=True)
        context = super().get_context_data(**kwargs)
        context['lang_code'] = 'en'