from rest_framework import serializers
from .models import Church


class ChurchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = [
            'id',
            'name',
            'address',
            'phone',
            'email',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']