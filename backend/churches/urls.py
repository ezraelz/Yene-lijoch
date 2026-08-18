from django.urls import path
from .views import (
    ChurchListCreateAPIView,
    ChurchDetailAPIView,
)

urlpatterns = [
    path(
        'churches/',
        ChurchListCreateAPIView.as_view(),
        name='church-list-create'
    ),

    path(
        'churches/<int:pk>/',
        ChurchDetailAPIView.as_view(),
        name='church-detail'
    ),
]