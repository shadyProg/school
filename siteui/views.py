from django.shortcuts import render

# Create your views here.
def index(req):

    return render(req,'index.html')

def index2(req):

    return render(req,'index2.html')


def about(req):

    return render(req,'about.html')


def blog(req):

    return render(req,'blog.html')


def course(req):

    return render(req,'course.html')


def faq(req):

    return render(req,'faq.html')

