
from django.urls import path

from . import views

#urls for the site
urlpatterns = [

    path("chat/<str:room_name>/", views.chat, name="chat"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("", views.home, name="home"),
    path("welcome", views.welcome, name="welcome"),
    path("create", views.create, name="create"),
    path("join", views.join, name="join"),

    path("messages", views.messages, name="messages")

]