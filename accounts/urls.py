from django.urls import path
from .views import UserRegistrationView, EmailVerificationView

urlpatterns = [
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/verify-email/<str:token>/', EmailVerificationView.as_view(), name='email-verify'),
]