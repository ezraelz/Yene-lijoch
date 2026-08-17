from django.db import models
from django.contrib.postgres.fields import ArrayField

class Course(models.Model):
    course_name = models.CharField(verbose_name='Course Name', max_length=50)
    course_code = models.CharField(max_length=100,unique=True, blank=True, null=True)
    credit_hours = models.PositiveIntegerField(default=0, blank=True, null=True)
    description = models.CharField(verbose_name="Discription", max_length=150)
    created_at = models.DateTimeField(("Created at"), auto_now=False, auto_now_add=True, blank=True, null=True)
    frequency = models.PositiveIntegerField(default=0)
    is_recess_activity = models.BooleanField(default=False)
    min_sessions_per_week = models.PositiveIntegerField(default=1, blank=True, null=True)  # curriculum rule
    max_sessions_per_week = models.PositiveIntegerField(default=5, blank=True, null=True)  # balance
    requires_double_period = models.BooleanField(default=False, blank=True)     # lab/art/music
    preferred_days = models.JSONField(default=list, blank=True) 
    room_type = models.CharField(
        max_length=50,
        choices=[("CLASSROOM", "Classroom"), ("LAB", "Laboratory"), ("GYM", "Gym")],
        default="CLASSROOM", blank=True, null=True
    )
    avoid_last_period = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.course_name
