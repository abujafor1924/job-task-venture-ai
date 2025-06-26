from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticated
from account.models import User, Profile
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from account.serializer import MyTokenObtainPairSerializer,RegisterSerializer,UserSerializer,ProfileSerializer
import random
import shortuuid
# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
     serializer_class = MyTokenObtainPairSerializer
     
class RegisterView(generics.CreateAPIView):
     queryset=User.objects.all()
     permission_classes= (AllowAny,)
     serializer_class=RegisterSerializer
     
     
def generate_otp():
     uuid_key=shortuuid.uuid()
     unique_key=uuid_key[:6]
     return unique_key
     
     
class PasswordResetEmailView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get(self, request, email, *args, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.otp = generate_otp()
        user.save()

        uidb64 = user.pk
        otp = user.otp
        reset_link = f'http://localhost:5173/create-new-password?otp={otp}&uidb64={uidb64}'

        # Email subject
        subject = "Password Reset Request"

        # Context data for email template
        context = {
            'user': user,
            'reset_link': reset_link,
        }

        # Email content (HTML)
        html_content = render_to_string('emails/password_reset_email.html', context)
        text_content = f"Hi {user.username},\n\nআপনার পাসওয়ার্ড রিসেট করতে নিচের লিঙ্কে ক্লিক করুন:\n\n{reset_link}\n\nযদি আপনি এই রিকোয়েস্ট না করে থাকেন, তাহলে ইমেইলটি উপেক্ষা করুন।"

        email_message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        email_message.attach_alternative(html_content, "text/html")

        try:
            email_message.send()
        except Exception as e:
            return Response({'message': 'Failed to send email', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Password reset link sent', 'reset_link': reset_link})

        
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data
        otp = payload['otp']
        uidb64 = payload['uidb64']
        password = payload['password']

        if not otp or not uidb64 or not password:
            return Response({'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=uidb64, otp=otp)
            user.set_password(password)
            user.otp = ""
            user.save()

            return Response({'message': 'Password changed successfully'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message': 'Invalid OTP or user ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ProfileView(generics.RetrieveUpdateAPIView):
     serializer_class=ProfileSerializer
     permission_classes=(AllowAny,)
     
     def get_object(self):
        user_id=self.kwargs['user_id']
        user=User.objects.get(id=user_id)
        profile=Profile.objects.get(user=user)
        return profile