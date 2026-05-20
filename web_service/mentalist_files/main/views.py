from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import os
import requests

from .models import Comment

NOTIFICATION_SERVICE_URL = os.environ.get(
    "NOTIFICATION_SERVICE_URL", "http://notification:8002"
)


# ── Страницы ────────────────────────────────────────────────────────────────

def index(request):
    return render(request, "index.html")


def cases(request):
    return render(request, "news.html")


def academy(request):
    if not request.user.is_authenticated:
        return render(request, "academy_locked.html")
    return render(request, "matches.html")


def register(request):
    if request.method == "POST":
        username   = request.POST.get("username", "").strip()
        password   = request.POST.get("password", "")
        password2  = request.POST.get("confirm_password", "")
        first_name = request.POST.get("firstname", "").strip()
        last_name  = request.POST.get("lastname", "").strip()
        email      = request.POST.get("email", "").strip()
        phone      = request.POST.get("phone", "").strip()

        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not username or not password or not first_name or not last_name:
            messages.error(request, "Заполните все обязательные поля")
            return render(request, "register.html")

        if password != password2:
            messages.error(request, "Пароли не совпадают")
            return render(request, "register.html")

        if len(password) < 6:
            messages.error(request, "Пароль должен быть не менее 6 символов")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким логином уже существует")
            return render(request, "register.html")

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone or None,
        )
        login(request, user)
        messages.success(request, f"Добро пожаловать, {first_name}! Доступ открыт.")
        return redirect("academy")

    return render(request, "register.html")


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"С возвращением, {user.first_name or user.username}.")
            return redirect("academy")
        messages.error(request, "Неверный логин или пароль")
    return render(request, "login.html")


def logout_page(request):
    logout(request)
    messages.info(request, "Выход выполнен")
    return redirect("home")


def feedback(request):
    if request.method == "POST":
        messages.success(request, "Сообщение передано в CBI")
        return redirect("feedback")
    return render(request, "feedback.html")


def comments_page(request):
    return render(request, "comments.html")


# ── Устаревшие алиасы ────────────────────────────────────────────────────────

def news(request):       return cases(request)
def operations(request): return academy(request)
def matches(request):    return academy(request)


# ── API: комментарии (polling) ───────────────────────────────────────────────

def api_comments(request):
    comments = [c.to_dict() for c in Comment.objects.order_by("-created_at")[:100]]
    return JsonResponse({"success": True, "comments": comments})


@csrf_exempt
@require_http_methods(["POST"])
def api_add_comment(request):
    try:
        data     = json.loads(request.body)
        username = (data.get("username") or "").strip()[:150]
        text     = (data.get("text") or "").strip()[:500]

        if not username or not text:
            return JsonResponse({"success": False, "message": "Заполните все поля"}, status=400)

        comment = Comment.objects.create(username=username, text=text)
        return JsonResponse({"success": True, "comment": comment.to_dict()})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Неверный формат данных"}, status=400)


# ── API: регистрация / вход (AJAX) ───────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    try:
        data = json.loads(request.body)
        from django.contrib.auth import get_user_model
        User = get_user_model()

        username   = (data.get("username") or "").strip()
        password   = data.get("password", "")
        first_name = (data.get("firstname") or "").strip()
        last_name  = (data.get("lastname") or "").strip()
        email      = (data.get("email") or "").strip()
        phone      = (data.get("phone") or "").strip()

        if not username or not password or not first_name or not last_name:
            return JsonResponse({"success": False, "message": "Заполните все обязательные поля"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "message": "Логин уже занят"}, status=400)

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name,
            email=email, phone=phone or None,
        )
        login(request, user)
        return JsonResponse({"success": True, "message": f"Добро пожаловать, {first_name}!", "redirect_url": "/academy/"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Неверный формат данных"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data     = json.loads(request.body)
        username = (data.get("username") or "").strip()
        password = data.get("password", "")

        if not username or not password:
            return JsonResponse({"success": False, "message": "Введите логин и пароль"}, status=400)

        user = authenticate(request, username=username, password=password)
        if not user:
            return JsonResponse({"success": False, "message": "Неверный логин или пароль"}, status=401)

        login(request, user)
        return JsonResponse({"success": True, "message": f"С возвращением, {user.first_name or user.username}.", "redirect_url": "/academy/"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Неверный формат данных"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_feedback(request):
    try:
        data = json.loads(request.body)
        name    = (data.get("name") or "").strip()
        email   = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()

        if not name or not email or not message:
            return JsonResponse({"success": False, "message": "Заполните все поля"}, status=400)

        try:
            resp = requests.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications",
                json={"name": name, "email": email, "message": message},
                timeout=5,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse(
                {"success": False, "message": f"Сервис уведомлений недоступен: {e}"},
                status=502,
            )

        return JsonResponse({"success": True, "message": "Сообщение передано в CBI"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Неверный формат данных"}, status=400)
