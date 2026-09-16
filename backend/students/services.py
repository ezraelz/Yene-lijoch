from .models import Student
from events.models import Event
from lessons.models import Lesson

class AdminStats:
    def get_total(organization):
        return { 
            "total_students": Student.objects.count(),
            "total_lessons": Student.objects.count(),
            "total_events": Student.objects.count(),
        }