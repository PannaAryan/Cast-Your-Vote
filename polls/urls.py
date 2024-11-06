# polls/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from . import views
from .views import CustomLoginView

app_name = 'polls'
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('login/', CustomLoginView.as_view(), name='login'),  # Login page,
    path('logout/', LogoutView.as_view(), name='logout'),
    path("accounts/signup/", views.signup_view, name="signup"),  # Add this line for signup
]

