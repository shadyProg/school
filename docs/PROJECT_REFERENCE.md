# Eduleb — Django Project Reference

> **What this is:** a complete reference for the `school/` Django project — how to rebuild it
> from an empty folder, what every file does, and the known bugs currently in the code.
>
> **Project:** Eduleb — an online-learning / education landing site with a blog section.
> **Stack:** Django 6.0.4 · Python 3.12 · SQLite · Bootstrap 4 + jQuery (frontend from the
> "Eduleb" HTML template by Bestwpware / ThemeWagon).
> **Last verified against the code:** 2026-09-25

---

## Table of Contents

**Part 1 — Build Guide** (rebuild from scratch)
1. [Prerequisites](#1-prerequisites)
2. [Create the project](#2-create-the-project)
3. [Create the apps](#3-create-the-apps)
4. [Wire up settings.py](#4-wire-up-settingspy)
5. [Build the model](#5-build-the-blog-model)
6. [Make migrations](#6-make-migrations)
7. [Build the form](#7-build-the-crud-form)
8. [Build the views](#8-build-the-views)
9. [Build the URL routing](#9-build-the-url-routing)
10. [Build the templates](#10-build-the-templates)
11. [Add static files](#11-add-static-files)
12. [Wire up media uploads](#12-wire-up-media-uploads)
13. [Run it](#13-run-it)

**Part 2 — Code Reference**
- [Directory tree](#directory-tree)
- [Settings reference](#settings-reference)
- [App: siteui](#app-siteui--the-ui-layer)
- [App: Blog](#app-blog--the-crud-layer)
- [URL map](#complete-url-map)
- [Model schema](#model-schema-blog)
- [Template architecture](#template-architecture)
- [Context flow](#context-flow)
- [Request lifecycle](#request-lifecycle)

**Part 3 — Known Issues** (verified bugs)

**Part 4 — How to extend** (recipes)

**Part 5 — Cheat sheet**

---

# Part 1 — Build Guide

> **ملاحظة:** كل الأوامر في هذا الدليل تُشغَّل من داخل مجلد `school/`.
> *All commands below run from inside the `school/` folder.*

## 1. Prerequisites

| Requirement | Version | Why |
|---|---|---|
| Python | **3.12+** | Django 6.0 requires 3.12 or newer |
| Django | 6.0.4 | Installed version |
| Pillow | any recent | Required for `ImageField` |
| SQLite | built into Python | Default database — no server needed |

> ⚠️ **Python version trap:** Django 6.0 will **not** install on Python 3.11 or older.
> Check with `python3 --version` before starting.

```bash
# create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install django pillow
```

> **ملاحظة:** حزمة `pillow` **إلزامية** بمجرد استخدام `ImageField`، وإلا Django
> يرفع خطأ `Could not find a backend for the 'image' operations` وقت رفع الصورة.
> `Pillow` is **mandatory** as soon as you use `ImageField`, otherwise Django raises
> `Could not find a backend for the 'image' operations` on upload.

## 2. Create the project

```bash
django-admin startproject school .
```

This creates the inner config package `school/` plus `manage.py`:

```
school/                <- the project config package (settings, urls, wsgi, asgi)
manage.py              <- CLI entry point
```

`manage.py` sets one critical variable:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
```

> **نقطة مهمة:** اسم مشروع Django هنا هو `school`، ومجلد `school/` داخله **مجلد
> إعدادات** وليس التطبيق. التطبيقات هي `siteui` و `Blog`.
> The project package is named `school` and lives at `school/school/`. That folder holds
> settings only — your actual apps are `siteui` and `Blog`.

## 3. Create the apps

```bash
python manage.py startapp siteui
python manage.py startapp Blog
```

| App | Role | Contains models? |
|---|---|---|
| `siteui` | Serves all the static marketing pages (home, about, courses, …) | No — `models.py` is empty |
| `Blog` | The only app with real logic: a `Blog` model + full CRUD | Yes |

> **لماذا `siteui` بدون موديلات؟** لأن صفحاته مجرد صفحات تسويقية ثابتة، لا بيانات
> لقاعدة البيانات. كل صفحاتها ترجع `get_section_context(...)` فقط.
> `siteui` has no models because its pages are purely static marketing pages — no
> database data involved. Every view just returns `get_section_context(...)`.

Then register both apps in `INSTALLED_APPS` (see [step 4](#4-wire-up-settingspy)).

> **حالة الأحرف مهمة في Django:** اسم التطبيق `Blog` بحرف `B` كبير، لذلك مساحة
> الأسماء في الـ URLs هي `'Blog'` (وليس `'blog'`). هذا سبب خطأ شائع — انظر
> [Known Issue #1](#known-issue-1--blogdeleteview-points-at-a-wrong-url-namespace).
> App names are **case-sensitive**. The app is `Blog`, so its URL namespace is
> `'Blog'`, not `'blog'`.

## 4. Wire up settings.py

File: `school/school/settings.py`

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
```

`BASE_DIR` resolves to the folder containing `manage.py` (the outer `school/`).

### 4.1 Security keys

```python
SECRET_KEY = 'uahAwgJQsZeAzpYSpc-tvlOr0I4_Lr2SQD_e-1TtHV0'
DEBUG = True
ALLOWED_HOSTS = []
```

> 🔴 **Never ship this `SECRET_KEY` or `DEBUG = True` to production.**
> Move the key to an environment variable and set `DEBUG = False` before deploying.
> This is development-only configuration.

### 4.2 Installed apps

```python
INSTALLED_APPS = [
    'Blog.apps.BlogConfig',        # our app 1
    'siteui.apps.SiteuiConfig',    # our app 2
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

### 4.3 Templates — the critical `DIRS` line

```python
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],   # <-- project-wide templates
    'APP_DIRS': True,                                 # <-- also <app>/templates/
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
```

> **هذا أهم سطر في الإعدادات للمشروع ده.** بدون `DIRS` لن يجد Django
> `base.html` و `navbar.html` و `sectionTop.html` لأنهم في `school/templates/`
> وليس داخل أي تطبيق.
>
> **This is the single most important setting in the project.** Without `DIRS`,
> Django cannot find `base.html`, `navbar.html` or `sectionTop.html`, because they
> live in `school/templates/` — *not* inside any app. `APP_DIRS: True` only looks
> inside `<app>/templates/`.
>
> Both values coexist on purpose:
> - `DIRS` → `school/templates/` (shared `base.html`, `navbar.html`, `sectionTop.html`)
> - `APP_DIRS: True` → `siteui/templates/` and `Blog/templates/` (per-app pages)

Django searches `DIRS` **first**, then app directories. Since no filename collides,
order does not matter here.

### 4.4 Static files and media

```python
STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / 'static']        # project-wide static folder
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')    # where uploads are written
MEDIA_URL = '/media/'                           # the public URL prefix
```

| Setting | Value | Purpose |
|---|---|---|
| `STATIC_URL` | `/static/` | URL prefix Django generates for `{% static %}` |
| `STATICFILES_DIRS` | `school/static/` | Extra dev-only folder holding the template assets |
| `MEDIA_ROOT` | `school/media/` | Filesystem path where uploaded images are saved |
| `MEDIA_URL` | `/media/` | URL prefix that maps to `MEDIA_ROOT` |

> `STATICFILES_DIRS` must be a **list**, not a string. And the folder it points at must
> exist, or Django raises `ImproperlyConfigured` at startup.

### 4.5 Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

SQLite stores everything in one file: `school/db.sqlite3`. No server, no config.

> **المشكلة الشائعة:** لو أضفت مفتاح `USER`/`PASSWORD` لـ SQLite وهيكل كأنها
> PostgreSQL، Django سيرفض التشغيل. SQLite يقبل `ENGINE` و `NAME` فقط.
> SQLite accepts **only** `ENGINE` and `NAME`. Adding `USER`/`PASSWORD`/`HOST` keys
> makes Django refuse to start.

## 5. Build the Blog model

File: `school/Blog/models.py` — **the only model in the project.**

```python
from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    title       = models.CharField(max_length=255)
    category    = models.CharField(max_length=255)
    description = models.TextField(null=False, blank=False)
    image       = models.ImageField(upload_to='image', null=True, blank=True,
                                    default='images/default.png')
    created_at  = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    default=1, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
```

### Why each field looks like this

| Field | Type | Why these options |
|---|---|---|
| `title` | `CharField(255)` | Short required text |
| `category` | `CharField(255)` | Plain text, **not** a `ForeignKey` — no Category model exists |
| `description` | `TextField` | `null=False, blank=False` = required in the form |
| `image` | `ImageField` | `null=True, blank=True` = optional; `upload_to='image'` → saved into `media/image/` |
| `created_at` | `DateTimeField(auto_now_add=True)` | Stamped **once** at creation, never editable |
| `user` | `ForeignKey(User)` | Links a post to its author |

### The three decisions that matter most

**a) `on_delete=models.SET_NULL`**
Chosen so deleting a user does **not** delete their blog posts — the post survives with
`user = NULL`. The previous behaviour was `CASCADE` (see migration `0002`).

> **فرق مهم:** `CASCADE` = لو مسحت اليوزر، الـ blogs بتتمسح كلها. `SET_NULL` = الـ
> blog بيفضل موجود بس `user` بيبقى `None`. المشروع حالياً على `SET_NULL`.
> `CASCADE` deletes the user's posts too. `SET_NULL` keeps the posts and empties the
> link. The project currently uses `SET_NULL` — changed in migration `0002`.

**b) `default=1, null=True, blank=True`**
`default=1` means "assign to user id 1 (the first/superuser) if none is given". Combined
with `null=True`, a post can exist with no author. This is what makes the site work
*without* a login system — see [Known Issue #3](#known-issue-3--the-crud-write-views-are-unreachable).

> ⚠️ **`default=1` is fragile:** if no user with `id=1` exists, the insert
> fails on the foreign key. Prefer assigning the user in `form_valid()` (which the
> views already do) and dropping the hardcoded `default`.

**c) `class Meta: ordering = ['-created_at']`**
Makes **every** query for `Blog` return newest-first automatically, so views never need
`.order_by()`.

> **ميزة كبيرة:** بمجرد ما تحط `ordering` في الـ `Meta`، كل الاستعلامات ترجع الأحدث
> الأول تلقائياً. لهذا `BlogListView` مش محتاج `ordering = ['-created_at']` جواه.
> Because ordering lives in the model's `Meta`, every queryset is already sorted
> newest-first. This is why `BlogListView` has no `ordering` attribute of its own.

## 6. Make migrations

```bash
python manage.py makemigrations Blog
python manage.py migrate
```

The repo contains two migrations:

| File | Date | What it did |
|---|---|---|
| `0001_initial.py` | 2026-09-02 | Created `Blog` with `user` as `CASCADE` |
| `0002_alter_blog_user.py` | 2026-09-11 | Changed `user` to `SET_NULL` |

```bash
# after editing models.py — always regenerate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser     # to reach /admin/
```

> **نصيحة:** بعد أي تعديل على `models.py` أو `froms.py` أو `views.py`، نفّذ
> `makemigrations` ثم `migrate` قبل التشغيل، وإلا هتلاقي أخطاء `column not found`.
> Never edit a migration file by hand unless you know exactly what you are doing —
> add a new one instead.

## 7. Build the CRUD form

File: `school/Blog/froms.py`

> ⚠️ **The filename is a typo — it is `froms.py`, not `forms.py`.** It is spelled this
> way in the repo, so the import is `from Blog.froms import CRUD_BlogForm`. See
> [Known Issue #5](#known-issue-5--the-forms-file-is-named-fromspy).

```python
from django import forms
from .models import Blog

class CRUD_BlogForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'blog-title'
    }))
    category = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'blog-category'
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'placeholder': 'blog-description'
    }))
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Blog
        fields = '__all__'
```

### How this works

`ModelForm` auto-generates fields from the model. These four declarations only **override
the widget** — label, required state and validation still come from the model.

| Override | Why |
|---|---|
| `title`, `category` | `TextInput` + `form-control` class for Bootstrap styling |
| `description` | Swapped to a `Textarea` — model is text, widget becomes multi-line |
| `image` | `required=False` so a post can be saved without a picture |
| `fields = '__all__'` | Include every model field |

> **`form-control` هو كل اللي بتعمله الـ attrs:** كلاس bootstrap اللي بيحط
> borders و padding و focus ring. لو شفته مش شغال، غالباً الـ CSS نفسه مش محمّل.
> `'class': 'form-control'` is purely the Bootstrap styling hook. If inputs look
> unstyled, Bootstrap CSS is not loading.

> ⚠️ **`fields = '__all__'` includes `user`.** It is a `ModelForm` field that is
> `null=True, blank=True`, so it renders as a user dropdown on the create form — and
> any visitor could pick any author. Consider
> `exclude = ['user']` or `fields = ['title', 'category', 'description', 'image']`.

## 8. Build the views

### 8.1 siteui — one function per page

File: `school/siteui/views.py`

All eleven pages share one helper, `get_section_context()`, so the navbar and footer
always receive the same data:

```python
def get_section_context(title, page_link=None):
    return {
        'section_title': title,
        'page_link': page_link,
        'blogs':           Blog.objects.all(),
        'last_blogs':      Blog.objects.all().order_by('-created_at')[:5],
        'last_three_blogs':Blog.objects.all().order_by('-created_at')[:3],
    }

def index(req):
    return render(req, 'index.html', get_section_context('Home'))
```

Each view is three lines: build context, render template.

> **ليه بنمرر `blogs` لكل صفحة؟** لأن `navbar.html` يحتاج قائمة الـ blogs عشان يعرض
> روابط الـ Blog Details في قائمة الموبايل. يعني كل صفحة بتعمل **3 استعلامات** على
> قاعدة البيانات حتى لو هي صفحة "Pricing" مش محتاجة blogs أصلاً.
>
> **Why pass `blogs` to every page?** Because `navbar.html` iterates `blogs` to build
> the mobile menu's blog links. The side-effect is that **every** page — including
> Pricing and FAQ — runs **3 database queries** on every single request. See
> [Known Issue #7](#known-issue-7--three-blog-queries-run-on-every-page).

### 8.2 Blog — class-based CRUD

File: `school/Blog/views.py`

| View | Base | Template | URL name |
|---|---|---|---|
| `BlogListView` | `ListView` | `blog.html` | `Blog:blog_list` |
| `BlogDetailView` | `DetailView` | `blog_single.html` | `Blog:blog_detail` |
| `BlogCreateView` | `CreateView` | `blog_form.html` | `Blog:blog_create` |
| `BlogUpdateView` | `UpdateView` | `blog_form.html` | `Blog:blog_update` |
| `BlogDeleteView` | `DeleteView` | `blog_confirm_delete.html` | `Blog:blog_delete` |

```python
class BlogListView(ListView):
    model = Blog
    template_name = 'blog.html'
    context_object_name = 'blogs'          # without this it'd be 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_section_context('Blogs', 'Blog:blog_create'))
        return context
```

`get_context_data()` is overridden purely to **merge `get_section_context()` into the
page's own data** — so the shared navbar/footer still get `blogs` and `section_title`.

> **نقطة مهمة:** لو نسيت `context.update(get_section_context(...))` في أي view جديد،
> هتلاقي الصفحة تفتح بس الـ navbar هيبان فاضي. دي أهم نقطة تتفاداها.
> If you forget the `context.update(get_section_context(...))` call in a new view,
> the page renders but the navbar comes out empty. This is the #1 thing to remember.

```python
class BlogCreateView(CreateView):
    model = Blog
    form_class = CRUD_BlogForm
    template_name = 'blog_form.html'
    success_url = reverse_lazy('Blog:blog_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        return super().form_valid(form)
```

**Why the `if self.request.user.is_authenticated` guard?**

This is the fix recorded in the project's `note.md`. A `ForeignKey` to `User` with
`default=1` fails when the database has no user id 1 — the save blows up with an
integrity error. The guard means: attach the real user if someone is logged in,
otherwise leave the model default alone.

> **الدرس المستفاد من `note.md`:** ربط الـ model بـ `User` مع `default=1` بيسبب
> خطأ لو اليوزر مش موجود في الداتابيز. الحل كان يعمل `null=True` ويخلي الـ view
> هو اللي يحط اليوزر لو مسجل دخول.
>
> **The lesson from `note.md`:** tying the model to `User` with `default=1` breaks
> when that user row does not exist. The fix was to make the field nullable and let
> the **view** assign the user only when someone is actually authenticated.

> ⚠️ `LoginRequiredMixin` **is imported at the top of the file but never applied** to
> any view. This means the create/update/delete endpoints are open to anonymous
> visitors. See [Known Issue #4](#known-issue-4--loginrequiredmixin-is-imported-but-never-used).

## 9. Build the URL routing

### 9.1 Root — `school/school/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',      include('siteui.urls')),   # siteui owns the root URL
    path('blog/', include('Blog.urls')),     # blog is mounted under /blog/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Two things to notice:

1. **Order matters.** `siteui.urls` is included at `''` and contains
   `path('', views.index)`. Putting `blog/` first would be safer, but as written the
   blog paths still work because no siteui path swallows `/blog/...`.
2. **`+=` not `==`.** The last line appends media-serving routes to `urlpatterns`.
   Using `==` (a common typo, and it appears in the project's `note.md`) would create
   a *new* list and **silently discard every URL** registered above it.

> **الخطأ اللي في `note.md`:** مكتوب `urlpatterns == static(...)` — لازم `+=`.
> باستخدام `==` هتعمل قائمة جديدة وبتضيّع كل الـ URLs اللي فوق، ومش هتاخد أي
> error واضح.
>
> **The `note.md` typo:** it shows `urlpatterns == static(...)`. It must be `+=`.
> With `==` you build a fresh list and throw away every URL above it — and get no
> useful error message.

### 9.2 siteui — `school/siteui/urls.py`

```python
app_name = 'siteui'          # <-- creates the 'siteui:' namespace
urlpatterns = [
    path('',                          views.index,            name='index'),
    path('index2/',                   views.index2,           name='index2'),
    path('about/',                    views.about,            name='about'),
    path('course/',                   views.course,           name='course'),
    path('course/details/',           views.course_detail,    name='course_detail_page'),
    path('course/<int:course_id>/',   views.course_detail,    name='course_detail'),
    path('contact/',                  views.contact,          name='contact'),
    path('faq/',                      views.faq,              name='faq'),
    path('instructors/',              views.instructor,       name='instructor'),
    path('instructors/details/',      views.instructor_detail, name='instructor_detail'),
    path('pricing/',                  views.pricing,          name='pricing'),
    path('thank-you/',                views.thank_you,        name='thank_you'),
]
```

### 9.3 Blog — `school/Blog/urls.py`

```python
from . import views
from django.urls import path

app_name = 'Blog'             # <-- capital B, this is the namespace
urlpatterns = [
    path('',                 views.BlogListView.as_view(),   name='blog_list'),
    path('details/<int:pk>/',views.BlogDetailView.as_view(), name='blog_detail'),
    path('create/',          views.BlogCreateView.as_view(), name='blog_create'),
    path('update/<int:pk>/', views.BlogUpdateView.as_view(), name='blog_update'),
    path('delete/<int:pk>/', views.BlogDeleteView.as_view(), name='blog_delete'),
]
```

> `app_name` is what makes `{% url 'Blog:blog_list' %}` work. Without it, names would
> be global and could collide between apps.

## 10. Build the templates

### 10.1 The three-layer layout

The project uses **template inheritance plus includes**, in three layers:

```
base.html                    <- full HTML skeleton, {% block content %}
   ├── {% include 'navbar.html' %}      <- header, every page
   ├── {% include 'sectionTop.html' %}  <- page title + breadcrumb
   └── {% block content %}{% endblock %}  <- each page fills this
```

**`base.html`** (in `school/templates/`) holds the `<head>` with all CSS, the preloader,
the navbar include, the section-top include, the big footer, and every `<script>` at the
bottom. Pages only supply their middle content.

```django
{% load static %}
...
{% include 'navbar.html' %}
{% include 'sectionTop.html' %}
{% block content %}{% endblock content %}
... footer ...
```

**`sectionTop.html`** renders the page heading and breadcrumb from two context values:

```django
<h1>{{ section_title }}</h1>
<ul>
  <li><a href="{% url 'siteui:index' %}">Home</a></li>
  {% if page_link %}
    <li>/ <a href="{% url page_link %}">{{ section_title }}</a></li>
  {% else %}
    <li>/ {{ section_title }}</li>
  {% endif %}
</ul>
```

> `{% url page_link %}` takes a **variable** — that is why views pass the link as a
> *string* like `'Blog:blog_create'` rather than building the URL themselves.
> One shared template can then point at any page.

**A page template** then looks like this:

```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
  <section class="blog_area section-padding">
    {% for blog in last_three_blogs %}
      <img src="{{ blog.image.url }}" alt="{{ blog.title }}">
      <h2><a href="{% url 'Blog:blog_detail' pk=blog.pk %}">{{ blog.title }}</a></h2>
    {% empty %}
      <p>No blog posts available yet.</p>
    {% endfor %}
  </section>
{% endblock content %}
```

> **الحلقة `{% for %}...{% empty %}`:** لو مفيش blogs، بيطبع رسالة بدل ما يطلع
> section فاضي. دي حماية مهمة خصوصاً في أول تشغيل للداتابيز.
> The `{% empty %}` branch renders a friendly message when there are no posts —
> important on a fresh database.

> ⚠️ `blog.html` and `blog_single.html` place `{% extends %}` **after** a stray
> `<!DOCTYPE html><html>` pair. Django ignores text outside blocks, so it still
> renders, but the markup is invalid and should be cleaned up.

### 10.2 Where templates live

| Path | Contents | Found via |
|---|---|---|
| `school/templates/` | `base.html`, `navbar.html`, `sectionTop.html` | `DIRS` |
| `school/siteui/templates/` | 12 page templates | `APP_DIRS` |
| `school/Blog/templates/` | 5 blog templates | `APP_DIRS` |

## 11. Add static files

All frontend assets come from the **Eduleb** HTML template and live in
`school/static/assets/`:

| Path | Contents |
|---|---|
| `assets/bootstrap/` | `bootstrap.min.css`, `bootstrap.min.js` |
| `assets/css/` | `style.css` (the theme), `animate.css`, `magnific-popup.css`, `jquery-simple-mobilemenu.css` |
| `assets/fonts/` | Font Awesome 6 + Themify icon fonts |
| `assets/js/` | jQuery 1.12.4, `scripts.js` (theme logic), WOW.js, modernizr, owl-carousel helpers, scrolltop |
| `assets/owlcarousel/` | Carousel CSS/JS |
| `assets/img/` | ~52 images: `logo.png`, hero backgrounds, `blog/`, `course/`, clients |

Load them in `base.html` with `{% static %}`:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'assets/css/style.css' %}">
<script src="{% static 'assets/js/scripts.js' %}"></script>
```

> **`{% static %}` لازم يكون مربوط بـ `{% load static %}` في أول الملف، وإلا
> الـ template مش هيلاقي الفلتر ويطلع error.**
> `{% load static %}` must be the first tag in the template, otherwise the tag is
> unknown and the page 500s.

Theme JS features in use: WOW.js scroll animations (`class="wow fadeInUp" data-wow-delay="0.1s"`),
Owl Carousel, Magnific Popup, simple mobile menu, scroll-to-top.

> ⚠️ `blog_single.html` has ~10 image references written as bare
> `src="assets/img/blog/author.jpg"` **without `{% static %}`** and without
> `{% load static %}`. Those resolve relative to the current URL, so they only work
> by accident. See [Known Issue #6](#known-issue-6--imagetags-in-blog_singlehtml-are-not-wrapped-in--static-).

## 12. Wire up media uploads

Three settings plus one `urls.py` line:

1. `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')` in `settings.py`
2. `MEDIA_URL = '/media/'` in `settings.py`
3. `path('blog/', include('Blog.urls'))` plus the `static()` line in root `urls.py`
4. `enctype="multipart/form-data"` on any `<form>` that uploads files

With those, an `ImageField(upload_to='image')` save writes to
`school/media/image/<random-name>.jpg`, and `{{ blog.image.url }}` renders as
`/media/image/<random-name>.jpg`.

> `enctype="multipart/form-data"` **مطلوب** في الـ form وإلا الصورة مش هتترفع
> خالص. و `blog_form.html` فيه السطر ده بالفعل.
> Without `enctype="multipart/form-data"` the file is silently ignored.
> `blog_form.html` has it correctly.

Existing uploads live in `school/media/image/`.

## 13. Run it

```bash
cd school
source .venv/bin/activate

python manage.py migrate
python manage.py createsuperuser      # optional, for /admin/
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

### Useful URLs while developing

| URL | Page |
|---|---|
| `/` | Home |
| `/about/` · `/course/` · `/contact/` · `/faq/` · `/pricing/` | siteui pages |
| `/blog/` | Blog list |
| `/blog/details/<pk>/` | Blog detail |
| `/admin/` | Django admin (needs a superuser) |

> **نصيحة:** `python manage.py check` بيكشف مشاكل الإعدادات و الـ URLs بسرعة،
> لكن مش هيكتشف أخطاء أسماء ملفات الـ templates — جرّب كل صفحة فعلياً.
> `manage.py check` validates settings and URL names, but it does **not** verify
> that every `render()` target template exists. Walk each page at least once.

---

# Part 2 — Code Reference

## Directory tree

```
school/
├── manage.py                      # CLI entry point
├── db.sqlite3                     # SQLite database
│
├── school/                        # ← project config package (NOT an app)
│   ├── settings.py                # 124 lines — all configuration
│   ├── urls.py                    #  29 lines — root URLconf
│   ├── asgi.py  /  wsgi.py        # ASGI/WSGI servers
│
├── siteui/                        # ← app 1: static pages, no models
│   ├── views.py                   #  68 lines — get_section_context() + 11 views
│   ├── urls.py                    #  17 lines — app_name = 'siteui'
│   ├── models.py                  # empty
│   ├── admin.py                   # empty
│   ├── apps.py  /  tests.py
│   └── templates/                 # 12 templates (~2900 lines)
│       ├── index.html  (599)      index2.html (596)   about.html (267)
│       ├── course_details.html (346)   course.html (109)   contact.html (100)
│       ├── pricing.html (132)     instructor.html (113)  faq.html (91)
│       ├── thank-you.html (67)    ins_details.html (54)  404.html (54)
│
├── Blog/                          # ← app 2: the only app with a model
│   ├── models.py                  #  21 lines — the Blog model
│   ├── froms.py                   #  35 lines — CRUD_BlogForm  (sic: typo)
│   ├── views.py                   #  91 lines — 5 CBVs
│   ├── urls.py                    #   9 lines — app_name = 'Blog'
│   ├── admin.py                   #   4 lines — registers Blog
│   ├── migrations/                # 0001_initial, 0002_alter_blog_user
│   └── templates/
│       ├── blog_form.html (389)   blog_single.html (195)   blog.html (44)
│       ├── blog_confirm_delete.html  ← EMPTY (0 bytes)
│       └── formcopy.html (387)    ← unused scratch copy
│
├── templates/                     # ← project-wide (via settings DIRS)
│   ├── base.html                  # 163 lines — HTML skeleton
│   ├── navbar.html                #  91 lines — header, both menus
│   └── sectionTop.html            #  27 lines — title + breadcrumb
│
├── static/assets/                 # Eduleb theme: bootstrap, css, js, fonts, ~52 images
├── media/image/                   # uploaded blog images
├── .github/workflows/django.yml   # CI (broken — see Known Issue #8)
└── README.md                      # empty
```

## Settings reference

`school/school/settings.py` — only the lines that differ from Django's defaults:

| Setting | Value | Note |
|---|---|---|
| `BASE_DIR` | `Path(...).parent.parent` | folder holding `manage.py` |
| `SECRET_KEY` | hardcoded string | 🔴 move to env var for production |
| `DEBUG` | `True` | 🔴 must be `False` in production |
| `ALLOWED_HOSTS` | `[]` | fine for dev; set real hosts in production |
| `INSTALLED_APPS` | `+ Blog.apps.BlogConfig, siteui.apps.SiteuiConfig` | our two apps |
| `TEMPLATES[0]['DIRS']` | `[BASE_DIR/'templates']` | finds `base.html` & co |
| `DATABASES['default']` | SQLite → `db.sqlite3` | `ENGINE` + `NAME` only |
| `STATIC_URL` | `'/static/'` | Django default |
| `STATICFILES_DIRS` | `[BASE_DIR/'static']` | the theme assets |
| `MEDIA_ROOT` | `BASE_DIR/'media'` | upload destination |
| `MEDIA_URL` | `'/media/'` | public URL prefix |
| `LANGUAGE_CODE` | `'en-us'` | |
| `TIME_ZONE` | `'UTC'` | |
| `AUTH_PASSWORD_VALIDATORS` | all 4 enabled | Django default |

## App: siteui — the UI layer

**Purpose:** serve the 12 Eduleb landing pages. No database models.

**Public helper:**

```python
def get_section_context(title, page_link=None) -> dict
```

| Key | Value | Consumed by |
|---|---|---|
| `section_title` | e.g. `'Course'` | `sectionTop.html` → `<h1>` and breadcrumb |
| `page_link` | e.g. `'Blog:blog_create'` or `None` | `sectionTop.html` → `{% url page_link %}` |
| `blogs` | all posts | `navbar.html` mobile menu |
| `last_blogs` | 5 newest | reserved for a sidebar/section |
| `last_three_blogs` | 3 newest | `blog.html` card grid |

**All 11 views** are identical in shape — a one-liner each:

```python
def about(req):
    return render(req, 'about.html', get_section_context('About'))
```

## App: Blog — the CRUD layer

**Purpose:** the only real data model, with a full class-based CRUD.

| File | Responsibility |
|---|---|
| `models.py` | The `Blog` model + `Meta.ordering` |
| `froms.py` | `CRUD_BlogForm` with Bootstrap widgets |
| `views.py` | 5 CBVs; each merges `get_section_context()` |
| `urls.py` | `app_name = 'Blog'`, 5 named routes |
| `admin.py` | `admin.site.register(Blog)` |

**The `get_context_data()` pattern** — repeated in every Blog view:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)   # page's own data
    context.update(get_section_context('Title', 'Blog:blog_create'))  # shared chrome
    return context
```

> `super()` supplies the page-specific context (`blogs`, `blog`, `form`); the
> `update()` adds the shared navbar/footer data on top.

**`BlogUpdateView.form_valid` calls `super(BlogCreateView, self)`** — it works
because both use the same `ModelFormMixin` implementation, but
`super().form_valid(form)` is correct and clearer.

## Complete URL map

### siteui (namespace `siteui:`)

| URL | Name | View | Template |
|---|---|---|---|
| `/` | `siteui:index` | `index` | `index.html` |
| `/index2/` | `siteui:index2` | `index2` | `index2.html` |
| `/about/` | `siteui:about` | `about` | `about.html` |
| `/course/` | `siteui:course` | `course` | `course.html` |
| `/course/details/` | `siteui:course_detail_page` | `course_detail` | 🔴 `course_detail.html` **(missing)** |
| `/course/<id>/` | `siteui:course_detail` | `course_detail` | 🔴 same |
| `/contact/` | `siteui:contact` | `contact` | `contact.html` |
| `/faq/` | `siteui:faq` | `faq` | `faq.html` |
| `/instructors/` | `siteui:instructor` | `instructor` | `instructor.html` |
| `/instructors/details/` | `siteui:instructor_detail` | `instructor_detail` | `ins_details.html` |
| `/pricing/` | `siteui:pricing` | `pricing` | `pricing.html` |
| `/thank-you/` | `siteui:thank_you` | `thank_you` | `thank-you.html` |

`404.html` exists but has **no URL** — it is only linked as a literal `404.html`.

### Blog (namespace `Blog:`)

| URL | Name | View | Template |
|---|---|---|---|
| `/blog/` | `Blog:blog_list` | `BlogListView` | `blog.html` |
| `/blog/details/<pk>/` | `Blog:blog_detail` | `BlogDetailView` | `blog_single.html` |
| `/blog/create/` | `Blog:blog_create` | `BlogCreateView` | `blog_form.html` |
| `/blog/update/<pk>/` | `Blog:blog_update` | `BlogUpdateView` | `blog_form.html` |
| `/blog/delete/<pk>/` | `Blog:blog_delete` | `BlogDeleteView` | 🔴 empty template |

### Admin

| URL | Name |
|---|---|
| `/admin/` | `admin.site.urls` |

## Model schema (Blog)

```
Blog
├── id          BigAutoField        PK, auto
├── title       CharField(255)      required
├── category    CharField(255)      required
├── description TextField           required
├── image       ImageField          nullable, upload_to='image',
│                                   default='images/default.png'
├── created_at  DateTimeField       auto_now_add → set once on insert
└── user        FK → auth.User      SET_NULL, default=1, nullable

Meta.ordering = ['-created_at']     ← newest first, for every query
```

## Template architecture

```
┌─────────────────────────────────────────────────────────┐
│ base.html                        school/templates/      │
│  <head> + all {% static %} CSS                          │
│  preloader                                          │
│  {% include navbar.html %}          ┐                   │
│  {% include sectionTop.html %}      ├─ shared chrome   │
│  {% block content %}{% endblock %}  ┘   ← pages fill   │
│  footer (4 columns + copyright)                         │
│  all <script> at the bottom                             │
└─────────────────────────────────────────────────────────┘
          ▲                    ▲                    ▲
          │ extends            │ extends            │ extends
   ┌──────┴──────┐     ┌───────┴───────┐    ┌───────┴────────┐
   │ index.html  │     │  blog.html    │    │ blog_form.html │
   │ about.html  │     │ blog_single   │    │ (create+update)│
   │ course.html │     │ course.html   │    └────────────────┘
   │ ... 12 total│     │ ... 5 total   │
   └─────────────┘     └───────────────┘
```

**What each layer owns**

| Layer | File | Owns |
|---|---|---|
| Skeleton | `base.html` | `<head>`, all CSS/JS, footer, the content `{% block %}` |
| Header | `navbar.html` | logo, desktop dropdown menu, mobile menu (iterates `blogs`) |
| Title | `sectionTop.html` | `{{ section_title }}` + breadcrumb from `page_link` |
| Page | app templates | the `{% block content %}` body |

## Context flow

```
request
   │
   ▼
siteui.views.index(req)
   │  get_section_context('Home')
   │    ├─ section_title       = 'Home'
   │    ├─ page_link           = None
   │    ├─ blogs               = Blog.objects.all()
   │    ├─ last_blogs          = 5 newest
   │    └─ last_three_blogs    = 3 newest
   ▼
render(req, 'index.html', context)
   │
   ├─ base.html  ── includes ──► navbar.html      needs: blogs
   │              ── includes ──► sectionTop.html  needs: section_title, page_link
   │              ── renders ──► {% block content %}   the page body
   ▼
HTTP response
```

The same shape applies to `BlogListView`, except `super().get_context_data()`
contributes the page's own data first, then `get_section_context()` is merged in.

## Request lifecycle — worked example: `GET /blog/`

1. `manage.py` / WSGI server → `school.urls`
2. `path('blog/', include('Blog.urls'))` matches
3. `Blog.urls` matches `path('', BlogListView.as_view(), name='blog_list')`
4. `BlogListView.get()` → `self.object_list = Blog.objects.all()`
   → newest-first automatically, from `Meta.ordering`
5. Template resolved as `blog.html` (app template dir)
6. `get_context_data()` runs: `super()` → `{'blogs': [...], 'blog_list': [...]}`
   then `context.update(get_section_context('Blogs', 'Blog:blog_create'))`
7. `blog.html` `{% extends 'base.html' %}` → base renders chrome
8. `{% for blog in last_three_blogs %}` prints 3 cards
9. `{{ blog.image.url }}` → `/media/image/<name>.jpg`
10. Response sent

---

# Part 3 — Known Issues

Every item below was **verified against the running code**, not guessed.
Nothing here has been changed — this section is documentation only.

## Known Issue #1 — `BlogDeleteView` points at a wrong URL namespace

**Severity: high — deleting a post 500s**

```python
# Blog/views.py
class BlogDeleteView(DeleteView):
    success_url = reverse_lazy('blog:blog_list')   # <-- lowercase
```

But `Blog/urls.py` declares `app_name = 'Blog'` (capital `B`). Django namespaces are
case-sensitive, so `'blog:blog_list'` does not exist.

```text
reverse('Blog:blog_list')  ->  /blog/     OK
reverse('blog:blog_list')  ->  NoReverseMatch
```

Because `success_url` is `reverse_lazy`, the failure is deferred until after the
record is deleted — so the post is destroyed and *then* the page errors.

**Fix:** change it to `reverse_lazy('Blog:blog_list')`.

## Known Issue #2 — `blog_confirm_delete.html` is an empty file

**Severity: high**

`Blog/templates/blog_confirm_delete.html` is **0 bytes**. `DeleteView` renders it and
returns an HTTP 200 with an empty body — no confirmation UI, no `{% csrf_token %}`,
no way to actually reach the delete URL from the page.

**Fix:** write the template. It should `{% extends 'base.html' %}`, show the post
title, and wrap a POST form:

```django
{% extends 'base.html' %}
{% block content %}
<form method="post">{% csrf_token %}
  <h2>Delete "{{ blog.title }}"?</h2>
  <button type="submit">Yes, delete</button>
</form>
{% endblock %}
```

## Known Issue #3 — the CRUD write views are unreachable

**Severity: high (functional gap)**

`blog_create`, `blog_update` and `blog_delete` are defined in `urls.py` but **no
template links to them**. A grep for `blog_create|blog_update|blog_delete` across all
templates returns nothing.

The only blog URLs reachable from the UI are the list and the detail page. The
create/update/delete pages can only be opened by typing the URL by hand.

**Fix:** add buttons, e.g. in `blog.html` and `blog_single.html`:

```django
<a href="{% url 'Blog:blog_create' %}">New post</a>
<a href="{% url 'Blog:blog_update' blog.pk %}">Edit</a>
<a href="{% url 'Blog:blog_delete' blog.pk %}">Delete</a>
```

## Known Issue #4 — `LoginRequiredMixin` is imported but never used

**Severity: high (security)**

```python
from django.contrib.auth.mixins import LoginRequiredMixin   # imported

class BlogCreateView(CreateView):        # not applied
class BlogUpdateView(UpdateView):        # not applied
class BlogDeleteView(DeleteView):        # not applied
```

The comments in the code say *"delete LoginRequiredMixin if you want to allow anyone
to create a blog post"* — but it was never actually added, so the mixin is dead
import and all three write views are open to anonymous visitors.

**Fix:** apply it — it must come **first** in the bases list:

```python
class BlogCreateView(LoginRequiredMixin, CreateView):
```

## Known Issue #5 — the forms file is named `froms.py`

**Severity: low (cosmetic, but a real typo)**

The file is `Blog/froms.py`, not `forms.py`, and the import matches the typo:
`from Blog.froms import CRUD_BlogForm`. It works, but it will mislead anyone reading
the code, and it is a frequent copy/paste accident.

**Fix:** `git mv Blog/froms.py Blog/forms.py` and update the single import in
`Blog/views.py`.

## Known Issue #6 — `<img>` tags in `blog_single.html` are not wrapped in `{% static %}`

**Severity: medium**

The template has `{% load static %}` at the top, but ~10 image tags use bare relative
paths:

```html
<img src="assets/img/blog/author.jpg" alt="" />
<img src="assets/img/blog/banner.jpg" class="img-fluid" alt="" />
```

Browsers resolve these against the **current URL**. On `/blog/` they would request
`/blog/assets/img/blog/author.jpg` → 404. Images appear only on pages where the
relative path happens to line up.

**Fix:** `{% static 'assets/img/blog/author.jpg' %}`.

## Known Issue #7 — three blog queries run on every page

**Severity: medium (performance)**

`get_section_context()` calls `Blog.objects.all()` three times, and **every** view in
both apps calls it. So `/pricing/`, `/faq/` and `/thank-you/` — pages that need no
blog data at all — each run three queries per request. `last_blogs` is never rendered
anywhere; it appears only inside a `{# ... #}` comment in `blog.html`.

**Fix:** drop `last_blogs` (unused), and fetch once:

```python
blogs = list(Blog.objects.all())
return {
    'section_title': title,
    'page_link': page_link,
    'blogs': blogs,
    'last_three_blogs': blogs[:3],
}
```

## Known Issue #8 — the CI workflow cannot pass

**Severity: medium (infrastructure)**

`.github/workflows/django.yml` has three independent problems:

| Problem | Detail |
|---|---|
| Python matrix too old | `3.7, 3.8, 3.9` — Django 6.0 requires **3.12+**, so `pip install` fails |
| Missing `requirements.txt` | the workflow runs `pip install -r requirements.txt`, but the file does not exist in the repo |
| Wrong branch | triggers on `master`, but the repo's branch is `main` |

**Fix:** set the matrix to `["3.12", "3.13"]`, add a `requirements.txt`, and change the
branch to `main`.

## Known Issue #9 — `course_detail` renders a template that does not exist

**Severity: medium**

```python
# siteui/views.py
def course_detail(req, course_id=None):
    return render(req, 'course_detail.html', context)
```

The file on disk is `course_details.html` (**`s` after `detail`**). Verified:

```text
BROKEN course_detail -> course_detail.html | TemplateDoesNotExist
```

So `/course/details/` and `/course/<id>/` both raise `TemplateDoesNotExist`.
`manage.py check` does **not** catch this — only visiting the page does.

**Fix:** rename the file to `course_detail.html`, or change the view to
`'course_details.html'`.

## Known Issue #10 — `formcopy.html` is a broken scratch copy

**Severity: low**

`Blog/templates/formcopy.html` is a 387-line duplicate of `blog_form.html` **missing
the `{% extends 'base.html' %}` line**. It therefore contains `{% block %}` tags
outside any parent template and fails to load:

```text
BROKEN blog: formcopy.html
```

It is dead weight. **Fix:** delete it.

## Known Issue #11 — 63 hardcoded `.html` links bypass the URLconf

**Severity: medium**

The project's own `file req.txt` says: *"Do NOT hardcode URLs such as
`<a href="/accounts/profile/">` when a Django named URL exists."* Yet **63**
hardcoded links remain, in 8 files:

| File | Count |
|---|---|
| `siteui/templates/index.html` | 18 |
| `siteui/templates/index2.html` | 17 |
| `Blog/templates/blog_single.html` | 10 |
| `siteui/templates/course.html` | 6 |
| `templates/navbar.html` | 6 |
| `templates/base.html` | 3 |
| `siteui/templates/404.html` | 2 |
| `siteui/templates/about.html` | 1 |

Examples: `href="course.html"`, `href="index.html"`, `href="single_blog.html"`.
These produce 404s, and they are the direct cause of the navbar's mobile menu linking
to `index.html` / `about.html` instead of real URLs.

**Fix:** replace each with `{% url 'siteui:...' %}`.

## Known Issue #12 — the mobile menu renders one link per blog post

**Severity: low (cosmetic)**

`navbar.html` loops over `blogs` to build the mobile menu:

```django
{% for blog in blogs %}
  <li><a href="{% url 'Blog:blog_detail' pk=blog.pk %}">Blog Detail</a></li>
{% endfor %}
```

With N posts you get N menu items **all labelled "Blog Detail"**. As posts accumulate
the menu grows without limit.

**Fix:** keep only the newest, or move the list out of the navbar into a proper
"Recent posts" sidebar on the blog pages.

## Known Issue #13 — `__pycache__` and `db.sqlite3` are tracked by git

`school/` has **no `.gitignore`**, and `git status` shows modified
`__pycache__/*.pyc` files and `db.sqlite3`. Committed bytecode causes noisy diffs and
merge conflicts between Python versions (both `cpython-312` and `cpython-314` appear).

**Fix:** add a `.gitignore` with `__pycache__/`, `*.pyc`, `db.sqlite3`, `media/`,
`.venv/`, then `git rm -r --cached` those paths.

## Known Issue #14 — `LoginRequiredMixin` guard is weaker than it looks

`form_valid` only assigns the user when authenticated, and the model has
`default=1`. If no user with `id=1` exists in the database, anonymous creation still
raises a foreign-key integrity error. Creating a superuser (id 1) masks this by
accident.

**Fix:** drop `default=1` from the model, set `null=True`, and rely on the view guard
plus `LoginRequiredMixin`.

---

# Part 4 — How to extend

## Add a static page (the common case)

This is the pattern the whole `siteui` app follows. Four edits:

**1.** `siteui/views.py`

```python
def testimonials(req):
    return render(req, 'testimonials.html', get_section_context('Testimonials'))
```

**2.** `siteui/urls.py`

```python
path('testimonials/', views.testimonials, name='testimonials'),
```

**3.** `siteui/templates/testimonials.html`

```django
{% extends 'base.html' %}
{% load static %}
{% block content %}
  <section class="section-padding"><div class="container">
    <h2>What our students say</h2>
  </div></section>
{% endblock content %}
```

**4.** `siteui/templates/navbar.html` — add a menu item:

```django
<li><a href="{% url 'siteui:testimonials' %}">Testimonials</a></li>
```

> **الخطوات الأربعة دايماً مع بعض.** لو نسيت خطوة، هتلاقي `NoReverseMatch` أو
> الصفحة مش ظاهرة في القائمة.
> All four steps go together — skip one and you get a `NoReverseMatch` or a page
> missing from the menu.

## Add a model field

```python
# 1. Blog/models.py
class Blog(models.Model):
    ...
    slug = models.SlugField(unique=True, blank=True)

# 2. regenerate + apply
python manage.py makemigrations Blog
python manage.py migrate

# 3. if it must be editable, add a widget override in froms.py
slug = forms.CharField(required=False, widget=forms.TextInput(attrs={
    'class': 'form-control', 'placeholder': 'blog-slug'
}))
```

## Add a comment model under Blog

```python
# Blog/models.py
class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

```bash
python manage.py makemigrations Blog && python manage.py migrate
```

Note: `blog_single.html` already has hardcoded comment markup — that static block is
where a `{% for comment in blog.comments.all %}` loop belongs.

## Fix the whole known-issues list in order

1. `blog:blog_list` → `Blog:blog_list` (one-word fix, unblocks deletes)
2. Write `blog_confirm_delete.html`
3. Add `LoginRequiredMixin` to the three write views
4. Rename `course_details.html` → `course_detail.html`
5. Link create/update/delete from the templates
6. `{% static %}` the images in `blog_single.html`
7. Replace the 63 hardcoded links
8. Delete `formcopy.html`, add `.gitignore`
9. Fix the CI matrix, branch and `requirements.txt`

---

# Part 5 — Cheat sheet

## Commands

```bash
cd school
source .venv/bin/activate

python manage.py runserver              # start on :8000
python manage.py check                  # validate settings + URL names
python manage.py makemigrations Blog    # generate migrations
python manage.py migrate                # apply migrations
python manage.py createsuperuser        # admin account
python manage.py shell                  # interactive ORM
python manage.py test                   # run tests
```

## Daily commands

```python
# in manage.py shell
from Blog.models import Blog
Blog.objects.count()                     # how many posts
Blog.objects.all()                       # newest first (Meta.ordering)
Blog.objects.create(title='T', category='C', description='D')
b = Blog.objects.first(); b.delete()
```

## Project conventions

| Convention | Rule |
|---|---|
| URL namespaces | `app_name = 'Blog'` and `'siteui'` — **case matters** |
| Referencing URLs | Always `{% url 'Blog:blog_detail' pk=blog.pk %}`, never a literal path |
| Referencing files | Always `{% static 'assets/...' %}`, with `{% load static %}` at the top |
| Page templates | Must `{% extends 'base.html' %}` and fill `{% block content %}` |
| New page views | Must call `get_section_context(title)` or the navbar renders empty |
| Forms | Bootstrap via `'class': 'form-control'`; images need `enctype="multipart/form-data"` |
| Models | Ordering belongs in `class Meta`, not in each view |

## Where things are

| I want to… | Edit |
|---|---|
| Add a page | `siteui/views.py` + `siteui/urls.py` + template + `navbar.html` |
| Change a page's title | the string passed to `get_section_context()` in the view |
| Change the blog card grid | `Blog/templates/blog.html` |
| Change blog data rules | `Blog/models.py`, then `makemigrations` + `migrate` |
| Change form styling | `Blog/froms.py` widget `attrs` |
| Change theme colours/fonts | `school/static/assets/css/style.css` |
| Add a navbar item | `school/templates/navbar.html` (**both** menus) |
| Change upload location | `MEDIA_ROOT` in `settings.py` |
| Register a model in admin | `Blog/admin.py` |

## Documentation gaps worth filling

- `school/README.md` is **empty** — this file is intended to fill that role
- No `requirements.txt` exists, but CI references one
- No `.gitignore` in `school/`, so `__pycache__` and `db.sqlite3` are tracked
- No tests exist — `tests.py` in both apps is an untouched stub, and
  `Blog/views.py` imports `LoginRequiredMixin` without using it
