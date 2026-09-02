from . import views
from django.urls import path
app_name = 'Blog'
urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('details/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    ]