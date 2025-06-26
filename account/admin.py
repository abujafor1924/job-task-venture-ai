from django.contrib import admin
from account.models import User, Profile

# Register your models here.

class UserAdmin(admin.ModelAdmin):
     list_display = ['id','email', 'full_name', 'phone']
    

class ProfileAdmin(admin.ModelAdmin):
     list_display = ['user', 'full_name', 'about', 'gender', 'state', 'country', 'city', 'address']
     search_fields=['email', 'full_name']
     list_filter=['date']
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
