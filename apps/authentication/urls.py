from django.urls import path
from .views import login_view, signup_user, logout_view

urlpatterns = [
    path('login/', login_view, name="login"),
    path('signup/', signup_user, name="signup"),
    path("logout/", logout_view, name="logout")
]
