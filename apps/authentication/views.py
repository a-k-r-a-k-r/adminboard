# -*- encoding: utf-8 -*-

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignUpForm


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/adminboard")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'
    context = {"form": form, "msg": msg}
    return render(request, "authentication/login.html", context)


def signup_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            msg = "User created successfully"
            success = True
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    context = {"form": form, "msg": msg, "success": success}
    return render(request, "authentication/signup.html", context)


def logout_view(request):
    logout(request)
    return render(request, "authentication/logout.html")