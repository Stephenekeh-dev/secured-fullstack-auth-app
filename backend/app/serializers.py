from rest_framework import serializers
from .models import CustomUser, FailedLoginAttempt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['is_custom_admin'] = False  # Regular user
        user = CustomUser(**validated_data)
        user.save()
        return user


class FailedLoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedLoginAttempt
        fields = ['email', 'password', 'attempt_count', 'timestamp', 'observation']
