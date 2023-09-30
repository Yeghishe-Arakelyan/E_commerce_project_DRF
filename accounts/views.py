from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, status, views
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from .utils import generate_verification_token
from .models import UserProfile
User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        verification_token = generate_verification_token()
        user.email_verification_token = verification_token
        user.save()

        
        UserProfile.objects.update_or_create(user=user, defaults={
            'shipping_address': self.request.data.get('shipping_address'),
            'phone_number': self.request.data.get('phone_number'),
            'delivery_date': self.request.data.get('delivery_date'),
            'delivery_time': self.request.data.get('delivery_time'),
            'special_instructions': self.request.data.get('special_instructions', ''),
        })

       
        subject = 'Verify Your Email Address'
        message = f'Click the following link to verify your email: {verification_token}'
        from_email = 'your_email@gmail.com'  
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

class EmailVerificationView(views.APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)