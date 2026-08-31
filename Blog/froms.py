from django import forms

from .models import Blog
# Create your forms here. and get your model Blog

class CRUD_BlogForm(forms.ModelForm):


    title= forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control' , 'placeholder':'blog-title'
    }))
    # 'class':'form-control' for bortstrage
    category=forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control' , 'placeholder':'blog-category'
    }))
    description=forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control' , 'placeholder':'blog-description'
    }))
    #  CharField -> Textarea
    # title
    image=forms.ImageField(widget=forms.FileInput(attrs={
        'class':'form-control' , 'placeholder':'blog-image'
    }))
    created_at=forms.DateTimeField(widget=forms.DateTimeInput(attrs={
        'class':'form-control' , 'placeholder':'blog-created_at'
    }))

    
    class Meta:
        model = Blog
        fields = ['title', 'category', 'description', 'image']
    