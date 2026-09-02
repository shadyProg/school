from multiprocessing import context
import re

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from Blog.froms import CRUD_BlogForm
from siteui.views import get_section_context
from .models import Blog


# Function-based view
'''
def blog_home(request):
    blogs = Blog.objects.all()
    return render(request, 'blog.html', {'blogs': blogs})
'''

# Class-based views

class BlogListView(ListView):
    model = Blog
    template_name = 'blog.html'
    context_object_name = 'blogs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_section_context('Blogs', 'Blog'))
        return context
        """
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            context.update(
                get_section_context('Blogs', 'Blog')
            )

            return context
        """
    # ordering = ['-created_at'] don`t need to add ordering here because we already added it in the model Meta class.


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog_single.html'
    context_object_name = 'blog'


class BlogCreateView(CreateView):
    model = Blog
    form_class = CRUD_BlogForm
    template_name = 'blog_form.html'
    #fields = ['title', 'category', 'description', 'image', 'user']
    success_url = reverse_lazy('blog:blog_list')
    #from_validation = True  # This is a custom attribute to indicate that form validation is enabled.
    def form_valid(self, form):
        # Custom form validation logic can be added here if needed.
        form.instance.user = self.request.user
        return super(BlogCreateView, self).form_valid(form)

class BlogUpdateView(UpdateView):
    model = Blog
    form_class = CRUD_BlogForm
    template_name = 'blog_form.html'
    success_url = reverse_lazy('blog:blog_list')
    def form_valid(self, form):
        
        form.instance.user = self.request.user
        return super(BlogCreateView, self).form_valid(form)


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'blog_confirm_delete.html'
    success_url = reverse_lazy('blog:blog_list')


