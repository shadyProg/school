from . import views
from django.urls import path
app_name = 'siteui'
urlpatterns = [
    path('', views.index, name='index'),
    path('index2/', views.index2, name='index2'),
    path('about/', views.about, name='about'),
    path('course/', views.course, name='course'),
    path('course/details/', views.course_detail, name='course_detail_page'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('instructors/', views.instructor, name='instructor'),
    path('instructors/details/', views.instructor_detail, name='instructor_detail'),
    path('pricing/', views.pricing, name='pricing'),
    path('thank-you/', views.thank_you, name='thank_you'),
]
