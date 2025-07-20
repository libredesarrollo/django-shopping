from django.views.generic import ListView, DetailView

from django.db.models import Q
from django.utils.dateparse import parse_date

from .models import Post, Category, Tag

class PostIndex(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'post/index.html'
    paginate_by = 15

    def get_queryset(self):
        queryset = Post.objects.filter(posted='yes').select_related('category').prefetch_related('tags')

        search = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category_id')
        tag_id = self.request.GET.get('tag_id')
        language = self.request.GET.get('language')
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')

        if search:
            queryset = queryset.filter(
                # Q(id__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if language:
            queryset = queryset.filter(language=language)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        if from_date and to_date:
            from_date_parsed = parse_date(from_date)
            to_date_parsed = parse_date(to_date)
            if from_date_parsed and to_date_parsed:
                queryset = queryset.filter(date__range=(from_date_parsed, to_date_parsed))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        
        # si quieres acceder a los parametros desde el template mediante
        # selected.<field> ej selected.tag_id 
        # context['selected'] = {
        #     'search': self.request.GET.get('search', ''),
        #     'category_id': self.request.GET.get('category_id', ''),
        #     'tag_id': self.request.GET.get('tag_id', ''),
        #     'language': self.request.GET.get('language', ''),
        #     'from': self.request.GET.get('from', ''),
        #     'to': self.request.GET.get('to', ''),
        # }
        return context
    
class PostShow(DetailView): #DetailViewDetailViewDetailView
    model=Post
    context_object_name='post'
    template_name='post/show.html'
    slug_field = 'slug'            # Campo del modelo
    slug_url_kwarg = 'slug'        # Nombre en la URL
