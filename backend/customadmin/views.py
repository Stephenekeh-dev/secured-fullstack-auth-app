from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.hashers import check_password, make_password
from app.models import FailedLoginAttempt
from app.serializers import FailedLoginAttemptSerializer
from customadmin.serializers import AdminLoginSerializer, AdminUserSerializer  # Must point to shared model
from customadmin.permissions import IsAdminUserCustom
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


User = get_user_model()


class AdminRegistrationAPIView(APIView):
    """Register admin users"""
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        data['is_custom_admin'] = True  # ✅ Ensure admin flag is set
        data['password'] = make_password(data['password'])  # ✅ Hash the password

        serializer = AdminUserSerializer(data=data)

        if serializer.is_valid():
            email = serializer.validated_data['email'].strip()

            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            return Response({"message": "Admin registered successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginAPIView(APIView):
    """Admin login using shared user model"""
    permission_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email'].strip()
            password = serializer.validated_data['password']

            user = User.objects.filter(email__iexact=email, is_custom_admin=True).first()

            if not user:
                return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

            if not check_password(password, user.password):
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            return Response({"message": "Login successful", "email": user.email}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class FailedLoginAttemptsDashboardAPIView(APIView):
    """Dashboard to view failed login attempts"""
    permission_classes = [IsAuthenticated, IsAdminUserCustom]  # Custom permission for admins

    def get(self, request):
        failed_attempts = FailedLoginAttempt.objects.all().order_by("-timestamp")
        serializer = FailedLoginAttemptSerializer(failed_attempts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminLogoutAPIView(APIView):
    """Logout admin"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

