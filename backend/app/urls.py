from django.urls import path
from .views import RegisterUser, LoginUser, DashboardView, LogoutUser

urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="login"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("logout/",  LogoutUser.as_view(), name="logout"),
]
