from django.shortcuts import render


def get_section_context(title, page_link_text):
    return {'section_title': title, 'page_link_text': page_link_text}


# Create your views here.
def index(req):
    context = get_section_context('Home', 'Home')
    return render(req, 'index.html', context)


def index2(req):
    context = get_section_context('Index2', 'Index2')
    return render(req, 'index2.html', context)


def about(req):
    context = get_section_context('About', 'About')
    return render(req, 'about.html', context)


def blog(req):
    context = get_section_context('Blog', 'Blog')
    return render(req, 'blog.html', context)


def blog_single(req):
    context = get_section_context('Blog Single', 'Blog Single')
    return render(req, 'blog_single.html', context)


def course(req):
    context = get_section_context('Course', 'Course')
    return render(req, 'course.html', context)


def course_detail(req, course_id=None):
    context = get_section_context('Course Detail', 'Course Detail')
    return render(req, 'course_detail.html', context)


def contact(req):
    context = get_section_context('Contact', 'Contact')
    return render(req, 'contact.html', context)


def faq(req):
    context = get_section_context('FAQ', 'FAQ')
    return render(req, 'faq.html', context)


def instructor(req):
    context = get_section_context('Instructor', 'Instructor')
    return render(req, 'instructor.html', context)


def instructor_detail(req):
    context = get_section_context('Instructor Details', 'Instructor Details')
    return render(req, 'ins_details.html', context)


def pricing(req):
    context = get_section_context('Pricing', 'Pricing')
    return render(req, 'pricing.html', context)


def thank_you(req):         
    context = get_section_context('Thank You', 'Thank You')
    return render(req, 'thank-you.html', context)

