from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Blog(models.Model):
    title= models.CharField(max_length=255)
    category=models.CharField(max_length=255)
    description=models.TextField(null=False,blank=False)
    image=models.ImageField(upload_to='image',null=True,blank=True ,default='images/default.png')
    created_at=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,default=1,null=True,blank=True)
    # user is exit by default in django auth module. It is used to create a relationship between the blog and the user who created it.
    # on_delete=models.CASCADE that weak reationship between the blog and the user.
    #  If the user is deleted, the blog will also be deleted.
    def __str__(self):
        return self.title
    class Meta:
        '''
        more data you need add to class
        '''
        ordering=['-created_at']
        # that means the latest blog will be shown first.