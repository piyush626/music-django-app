from main.views import get_start
from django.urls import path
from . import views
from django.urls import include

app_name = "main"

urlpatterns = [
    path('', views.index, name="index"),
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('predict', views.predict, name="predict"),
    path('about/', views.about, name="about"),
    path('getstart/', views.get_start, name="getstart"),
    path('under_construction', views.under_construction, name="under_construction"),
]
