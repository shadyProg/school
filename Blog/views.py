from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from Blog.froms import CRUD_BlogForm
from .models import Blog


# Function-based view

def blog_home(request):
    blogs = Blog.objects.all()
    return render(request, 'Blog/blog_list.html', {'blogs': blogs})


# Class-based views

class BlogListView(ListView):
    model = Blog
    template_name = 'Blog/blog_list.html'
    context_object_name = 'blogs'
    # ordering = ['-created_at'] don`t need to add ordering here because we already added it in the model Meta class.


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'Blog/blog_single.html'
    context_object_name = 'blog'


class BlogCreateView(CreateView):
    model = Blog
    form_class = CRUD_BlogForm
    template_name = 'Blog/blog_form.html'
    fields = ['title', 'category', 'description', 'image', 'user']
    success_url = reverse_lazy('blog:blog_list')


class BlogUpdateView(UpdateView):
    model = Blog
    template_name = 'Blog/blog_form.html'
    fields = ['title', 'category', 'description', 'image', 'user']
    success_url = reverse_lazy('blog:blog_list')


class BlogDeleteView(DeleteView):
    model = Blog
    template_name = 'Blog/blog_confirm_delete.html'
    context_object_name = 'blog'
    success_url = reverse_lazy('blog:blog_list')


