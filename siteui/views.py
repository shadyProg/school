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

def blog_single(req):

    return render(req,'blog_single.html')


def course(req):

    return render(req,'course.html')

def course_detail(req, course_id=None):

    return render(req,'course_detail.html')


def contact(req):

    return render(req,'contact.html')


def faq(req):

    return render(req,'faq.html')

def instructor(req):

    return render(req,'instructor.html')

def instructor_detail(req):

    return render(req,'ins_details.html')

def pricing(req):

    return render(req,'pricing.html')

def thank_you(req):

    return render(req,'thank-you.html')

