def theme(request):
    current_theme = request.session.get('theme', 'light') # 'light' es el valor por defecto
    return {'theme': current_theme}