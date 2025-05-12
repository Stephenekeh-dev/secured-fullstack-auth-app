from rest_framework import serializers
from app.models import CustomUser, FailedLoginAttempt  # Use the same model from app

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password']
    
    def create(self, validated_data):
        validated_data['is_custom_admin'] = True
        validated_data['is_staff'] = True  # Optional: for admin panel access
        user = CustomUser(**validated_data)
        user.save()
        return user

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminFailedLoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailedLoginAttempt
        fields = ['email', 'password', 'attempt_count', 'timestamp', 'observation']
