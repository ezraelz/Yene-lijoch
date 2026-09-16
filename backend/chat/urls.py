from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConversationViewSet

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")

urlpatterns = [
    path("chat/", include(router.urls)),
]

# Resulting endpoints (once included at the project root — see
# integration_snippets/urls_additions.py):
#   GET  /chat/conversations/
#   GET  /chat/conversations/{id}/
#   GET  /chat/conversations/{id}/messages/
#   POST /chat/conversations/{id}/messages/    { "text": "..." }
#   POST /chat/conversations/{id}/mark_read/   { "role": "teacher" | "parent" }
