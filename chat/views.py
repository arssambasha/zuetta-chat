import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import *

#Just a welcome page for unauthenticated users
def welcome(request):
    return render(request, "chat/welcome.html")

#It loads all the Z-Groups where the user was messaged with pagination
@login_required
def home(request):

    group_list = Group.objects.filter(group__user=request.user).distinct()
    paginator = Paginator(group_list, 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "chat/home.html", {"page_obj": page_obj})

@csrf_exempt
@login_required
def chat(request, room_name):

    #checks if the Group with a z_id from the url is exists
    try:
        z_group = Group.objects.get(z_id=room_name)
    except Group.DoesNotExist:
        raise Http404("Z-Group does not exist")

    return render(request, "chat/chat.html", {'room_name' : room_name, 'z_group' : z_group})

#just sends the messages from the requested group according to the starting and ending position
def messages(request):

    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))
    group = request.GET.get("group")

    messages_queryset = Messages.objects.filter(z_group__z_id=group)[start:end + 1]

    data = [
        {"username": message.user.username, "content": message.content, "timestamp": message.timestamp.isoformat()}
        for message in messages_queryset
    ]

    return JsonResponse({
        "messages": data
    })

#Used to create new Z-Group
@login_required
def create(request):

    if request.method == "POST":
        z_name = request.POST["z-name"]
        z_id = request.POST["z-id"]

        user = request.user

        #if the z_id is exists sends a error message
        if Group.objects.filter(z_id=z_id).exists():
            return render(request, "chat/create.html", {
                'error_message': 'Already exists! Please enter different Z-ID'
            })
        #saves the new group
        else:
            group = Group(z_name = z_name, z_id = z_id, creator = user)
            group.save()
            #after that goes to home page
            return HttpResponseRedirect(reverse("home"))

    else:
        return render(request, "chat/create.html")

#searches an existing group either by z_name or z_id
@login_required
def join(request):

    if request.method == "POST":

        group = Group.objects.all()
        res = []

        if request.POST["z-id"] == "":
            z_name = request.POST["z-name"]

            for i in group:
                if (z_name.lower() in i.z_name.lower()):
                    res.append(i)

        
        if request.POST["z-name"] == "":
            z_id = request.POST["z-id"]

            for i in group:
                if (z_id in i.z_id):
                    res.append(i)
            

        return render(request, "chat/join.html", {
                "res": res
            })
        
    else:
        return render(request, "chat/join.html")

#Just login view
def login_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "chat/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "chat/login.html")

#just logout view
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("welcome"))

#User Registration
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "chat/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "chat/register.html", {
                "message": "Username or Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "chat/register.html")