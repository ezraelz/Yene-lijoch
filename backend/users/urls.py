from django.urls import path
from . import views
from .views import (CustomTokenObtainPairView ,
                    ProfileView,StaffView,
                    LoginView,ProfileDetailView,
                    LogoutView, UserCreateView)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('users/', views.userView.as_view(), name='users'),
    path('users/create/', UserCreateView.as_view(), name='users'),
    
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('change-password/', views.EnhancedChangePasswordView.as_view(), name='change-password'),
    path('send-reset-code/', views.SendResetCodeView.as_view(), name='send-reset-code'),
    path('verify-reset-code/', views.VerifyResetCodeView.as_view(), name='verify-reset-code'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),

    path('users/me/', ProfileView.as_view(), name='profileView'),
    path('staff-view/', StaffView.as_view(), name='staffView'),

    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile_detail/<int:pk>/', ProfileDetailView.as_view(), name='profileDetailView'),
]