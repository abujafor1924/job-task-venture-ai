from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from shortuuid.django_fields import ShortUUIDField



# Create your models here.
class User(AbstractUser):
     username = models.CharField(max_length=100)
     email = models.EmailField(unique=True)
     full_name = models.CharField(max_length=100, blank=True, null=True)
     phone=models.CharField(max_length=100, blank=True, null=True)
     otp=models.CharField(max_length=100, blank=True, null=True)
     
     USERNAME_FIELD = 'email'
     REQUIRED_FIELDS = ['username']
     
     def __str__(self):
         return self.email
    
     def save(self, *args, **kwargs):
       email_username,mobail=self.email.split('@')
       if self.full_name=="" or self.full_name==None:
         self.full_name=email_username
       if self.username=="" or self.username==None:
         self.username=email_username
       super(User, self).save(*args, **kwargs)
       
       
class Profile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE)
     image=models.FileField(default='default/default.webp',upload_to='profile_pics',blank=True,null=True)
     full_name=models.CharField(max_length=100,blank=True,null=True)
     about=models.TextField(max_length=500,blank=True,null=True)
     gender=models.CharField(max_length=100,blank=True,null=True)
     state=models.CharField(max_length=100,blank=True,null=True)
     country=models.CharField(max_length=100,blank=True,null=True)
     city=models.CharField(max_length=100,blank=True,null=True)
     address=models.TextField(max_length=500,blank=True,null=True)
     date=models.DateTimeField(auto_now_add=True)
     pid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefgh')
     
     def __str__(self):
       if self.full_name:
         return str(self.full_name)
       else:
         return str(self.user.full_name)
       
     def save(self, *args, **kwargs):
       if self.full_name=="" or self.full_name==None:
         self.full_name=self.user.full_name
       super(Profile, self).save(*args, **kwargs)
     
     

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()
  
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
     
     