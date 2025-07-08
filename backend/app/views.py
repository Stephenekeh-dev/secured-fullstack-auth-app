
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from .models import CustomUser
from .serializers import UserSerializer
from Crypto.Cipher import Blowfish
import base64
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework.parsers import MultiPartParser
from .models import FailedLoginAttempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication








# Secret key for Blowfish encryption (store in environment variables in production)
BLOWFISH_KEY = b"my_secret_key_1234"  # Replace with a secure key

def encrypt_password(plain_text_password):
    """Encrypt password using Blowfish algorithm."""
    if not plain_text_password:
        raise ValueError("No password provided for encryption.")

    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)

    try:
        plen = Blowfish.block_size - len(plain_text_password) % Blowfish.block_size
        padding = bytes([plen]) * plen  # Add correct padding

        encrypted_bytes = cipher.encrypt(plain_text_password.encode() + padding)
        encrypted_base64 = base64.b64encode(encrypted_bytes).decode()

        if not encrypted_base64:
            raise ValueError("Encryption failed. Empty result.")

        return encrypted_base64

    except Exception as e:
        print(f"Encryption Error: {str(e)}")
        raise ValueError("Encryption process failed.")

def decrypt_password(encrypted_password):
    cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_ECB)
    encrypted_bytes = base64.b64decode(encrypted_password)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)

    padding_length = decrypted_bytes[-1]
    decrypted = decrypted_bytes[:-padding_length].decode()
    return decrypted


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]  # ✅ Enable file upload parsing

    def post(self, request):
        data = request.data.copy()

        if "password" in data:
            print(f"Original Password: {data['password']}")
            encrypted_password = encrypt_password(data["password"])
            print(f"Encrypted Password: {encrypted_password}")
            if not encrypted_password:
                return Response({"error": "Password encryption failed"}, status=500)
            data["password"] = encrypted_password

        data["is_custom_admin"] = False

        # ✅ Don't use `files=...` — only pass `data=...`
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)
    

class LoginUser(APIView):
    permission_classes = [AllowAny]  
    """User login with token generation and fraud detection"""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
            stored_encrypted_password = user.password
            decrypted_password = decrypt_password(stored_encrypted_password)

            if password == decrypted_password:
                login(request, user)  # optional if still using sessions

                # 🔒 Issue token
                token, _ = Token.objects.get_or_create(user=user)

                # ✅ Clear previous failed attempts
                FailedLoginAttempt.objects.filter(email=email).delete()

                # ✅ Save successful login
                FailedLoginAttempt.objects.create(
                    email=email,
                    password=stored_encrypted_password,
                    attempt_count=1,
                    observation="Authentic User"
                )

                return Response({
                    "message": "Login successful",
                    "token": token.key,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "profile_image": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
                }, status=status.HTTP_200_OK)

            else:
                self.log_failed_attempt(email, password)
                return Response({"error": "suspected fraud detected"}, status=status.HTTP_401_UNAUTHORIZED)

        except CustomUser.DoesNotExist:
            self.log_failed_attempt(email, password)
            return Response({"error": "suspected fraud detected"}, status=status.HTTP_404_NOT_FOUND)

    def log_failed_attempt(self, email, password):
        """Logs failed login attempts"""
        failed_attempt, created = FailedLoginAttempt.objects.get_or_create(
            email=email,
            defaults={"attempt_count": 0}
        )

        failed_attempt.attempt_count += 1
        failed_attempt.timestamp = now()

        if failed_attempt.attempt_count >= 2:
            failed_attempt.password = password
            failed_attempt.observation = "Suspected fraud"
        else:
            failed_attempt.password = encrypt_password(password)
            failed_attempt.observation = "Authentic User"

        failed_attempt.save()



class DashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_image': request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
        })

    
class LogoutUser(APIView):
    """User logout and session clearing"""
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can log out

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not logged in"}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)  # Destroy the session
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        
        # Delete session and authentication cookies
        response.delete_cookie("sessionid")
        response.delete_cookie("csrftoken")
        response.delete_cookie("auth_token")  # If using token authentication

        return response

