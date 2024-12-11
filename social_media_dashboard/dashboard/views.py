from django.shortcuts import render
import requests

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegisterForm

from django.contrib.auth.decorators import login_required


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
    return render(request, "login.html")


@login_required
def dashboard_view(request):
    # Fetch the API key and account ID from the logged-in user
    api_key = request.user.api_key  # API key saved during registration
    instagram_account_id = request.user.instagram_user_id
    # Replace with the actual account ID

    posts = []
    user_profile = {}
    if api_key:
        try:
            # Fetch user profile for username and profile picture
            user_profile_url = (
                f"https://graph.facebook.com/v17.0/{instagram_account_id}"
            )
            user_profile_params = {
                "fields": "username,profile_picture_url",
                "access_token": api_key,
            }
            user_profile_response = requests.get(
                user_profile_url, params=user_profile_params
            )
            if user_profile_response.status_code == 200:
                user_profile = user_profile_response.json()
            else:
                user_profile = {"username": "Unknown", "profile_picture_url": ""}

            # Fetch posts from the Instagram API
            url = f"https://graph.facebook.com/v17.0/{instagram_account_id}/media"
            params = {
                "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count",
                "access_token": api_key,
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", [])
                for post in posts:
                    # Ensure each post has a 'caption' and 'media_url' (or 'thumbnail_url')
                    post["caption"] = post.get("caption", "No caption available")
                    post["media_url"] = post.get(
                        "media_url", post.get("thumbnail_url", "")
                    )
                    post["like_count"] = post.get("like_count", 0)
                    post["comments_count"] = post.get("comments_count", 0)

                    # Fetch comments for the post
                    comments_url = f"https://graph.facebook.com/v17.0/{post['id']}/comments"
                    comments_params = {
                        "fields": "id,text,username,timestamp",
                        "access_token": api_key,
                    }
                    comments_response = requests.get(
                        comments_url, params=comments_params
                    )
                    if comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        post["comments"] = comments_data.get("data", [])
                    else:
                        post["comments"] = [
                            {"id": "", "text": "Error fetching comments"}
                        ]
            else:
                posts = [
                    {
                        "id": "",
                        "caption": "Error fetching posts",
                        "media_url": "",
                        "timestamp": "",
                        "media_type": "",
                        "like_count": 0,
                        "comments_count": 0,
                        "comments": [],
                    }
                ]
        except requests.exceptions.RequestException as e:
            posts = [
                {
                    "id": "",
                    "caption": f"Request exception occurred: {str(e)}",
                    "media_url": "",
                    "timestamp": "",
                    "media_type": "",
                    "like_count": 0,
                    "comments_count": 0,
                    "comments": [],
                }
            ]
    else:
        posts = [
            {
                "id": "",
                "caption": "API key is not available.",
                "media_url": "",
                "timestamp": "",
                "media_type": "",
                "like_count": 0,
                "comments_count": 0,
                "comments": [],
            }
        ]

    return render(
        request,
        "dashboard.html",
        {
            "posts": posts,
            "user_profile": user_profile,  # Pass user profile info to the template
        },
    )

@login_required
def profile_view(request):
    if request.method == "POST":
        api_key = request.POST.get("api_key")
        instagram_user_id = request.POST.get("instagram_user_id")
        request.user.api_key = api_key
        request.user.instagram_user_id = instagram_user_id
        request.user.save()
        return redirect("profile")  # Redirect to the profile page after update

    return render(
        request,
        "profile.html",
        {
            "user": request.user,  # Pass the user object to the template
        },
    )

@login_required
def update_api_key(request):
    if request.method == "POST":
        api_key = request.POST.get('api_key')
        request.user.api_key = api_key
        request.user.save()
        return redirect('dashboard')  # Redirect to the dashboard or desired page
    return render(request, 'update_api_key.html')

from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect("login")