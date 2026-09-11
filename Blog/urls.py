from . import views
from django.urls import path
app_name = 'Blog'
urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('details/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('create/', views.BlogCreateView.as_view(), name='blog_create'),
    path('update/<int:pk>/', views.BlogUpdateView.as_view(), name='blog_update'),
    path('delete/<int:pk>/', views.BlogDeleteView.as_view(), name='blog_delete'),
    ]