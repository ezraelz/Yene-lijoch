from django.urls import path
from . import views

urlpatterns = [
    path('role/', views.RoleView.as_view(), name='viewRoles'),
    path('role/<int:pk>/', views.RoleDetailView.as_view(), name='RoleDetail'),
]