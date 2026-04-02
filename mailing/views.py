from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Mailing, MailingAttempt, Message


def manager_required(view_func):
    """Декоратор для проверки, что пользователь менеджер"""

    def wrapper(request, *args, **kwargs):
        if (
            request.user.groups.filter(name="Менеджеры").exists()
            or request.user.is_superuser
        ):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied

    return wrapper


def home(request):
    """Главная страница со статистикой с кешированием"""
    cache_key = "home_stats"
    cached_data = cache.get(cache_key)

    if cached_data is not None:
        total_mailings, active_mailings, unique_clients = cached_data
    else:
        total_mailings = Mailing.objects.count()
        now = timezone.now()
        active_mailings = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now
        ).count()
        unique_clients = Client.objects.distinct().count()
        cache.set(cache_key, (total_mailings, active_mailings, unique_clients), 300)

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_clients": unique_clients,
    }
    return render(request, "mailing/home.html", context)


# КЛИЕНТЫ
@login_required
def client_list(request):
    """Список клиентов: менеджеры видят всех, пользователи - только своих"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        clients = Client.objects.all().order_by("full_name")  # Менеджеры видят всех
    else:
        clients = Client.objects.filter(owner=request.user).order_by(
            "full_name"
        )  # Пользователи - только своих

    return render(request, "mailing/client_list.html", {"clients": clients})


@login_required
def client_detail(request, pk):
    """Детальная информация о клиенте"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        client = get_object_or_404(Client, pk=pk)  # Менеджеры видят всех
    else:
        client = get_object_or_404(
            Client, pk=pk, owner=request.user
        )  # Пользователи - только своих

    return render(request, "mailing/client_detail.html", {"client": client})


@login_required
def client_create(request):
    """Создание нового клиента"""
    if request.method == "POST":
        form = ClientForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("mailing:client_list")
    else:
        form = ClientForm(user=request.user)

    return render(
        request,
        "mailing/client_form.html",
        {"form": form, "title": "Создание нового клиента"},
    )


@login_required
def client_update(request, pk):
    """Редактирование клиента (только своего для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        client = get_object_or_404(Client, pk=pk)  # Менеджеры могут редактировать всех
    else:
        client = get_object_or_404(
            Client, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("mailing:client_detail", pk=client.pk)
    else:
        form = ClientForm(instance=client, user=request.user)

    return render(
        request,
        "mailing/client_form.html",
        {"form": form, "title": f"Редактирование клиента: {client.full_name}"},
    )


@login_required
def client_delete(request, pk):
    """Удаление клиента (только своего для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        client = get_object_or_404(Client, pk=pk)  # Менеджеры могут удалять всех
    else:
        client = get_object_or_404(
            Client, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        client.delete()
        return redirect("mailing:client_list")

    return render(request, "mailing/client_confirm_delete.html", {"client": client})


# СООБЩЕНИЯ
@login_required
def message_list(request):
    """Список сообщений: менеджеры видят все, пользователи - только свои"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        messages = Message.objects.all().order_by("subject")  # Менеджеры видят все
    else:
        messages = Message.objects.filter(owner=request.user).order_by(
            "subject"
        )  # Пользователи - только своих

    return render(request, "mailing/message_list.html", {"messages": messages})


@login_required
def message_detail(request, pk):
    """Детальная информация о сообщении"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        message = get_object_or_404(Message, pk=pk)  # Менеджеры видят все
    else:
        message = get_object_or_404(
            Message, pk=pk, owner=request.user
        )  # Пользователи - только своих

    return render(request, "mailing/message_detail.html", {"message": message})


@login_required
def message_create(request):
    """Создание нового сообщения"""
    if request.method == "POST":
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("message_list")
    else:
        form = MessageForm(user=request.user)

    return render(
        request,
        "mailing/message_form.html",
        {"form": form, "title": "Создание нового сообщения"},
    )


@login_required
def message_update(request, pk):
    """Редактирование сообщения (только своего для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        message = get_object_or_404(Message, pk=pk)  # Менеджеры могут редактировать все
    else:
        message = get_object_or_404(
            Message, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        form = MessageForm(request.POST, instance=message, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("mailing:message_detail", pk=message.pk)
    else:
        form = MessageForm(instance=message, user=request.user)

    return render(
        request,
        "mailing/message_form.html",
        {"form": form, "title": f"Редактирование сообщения: {message.subject}"},
    )


@login_required
def message_delete(request, pk):
    """Удаление сообщения (только своего для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        message = get_object_or_404(Message, pk=pk)  # Менеджеры могут удалять все
    else:
        message = get_object_or_404(
            Message, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        message.delete()
        return redirect("mailing:message_list")

    return render(request, "mailing/message_confirm_delete.html", {"message": message})


# РАССЫЛКИ
@login_required
def mailing_list(request):
    """Список рассылок: менеджеры видят все, пользователи - только свои"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        mailings = Mailing.objects.all().order_by("-start_time")  # Менеджеры видят все
    else:
        mailings = Mailing.objects.filter(owner=request.user).order_by(
            "-start_time"
        )  # Пользователи - только своих

    return render(request, "mailing/mailing_list.html", {"mailings": mailings})


@login_required
def mailing_detail(request, pk):
    """Детальная информация о рассылке"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        mailing = get_object_or_404(Mailing, pk=pk)  # Менеджеры видят все
    else:
        mailing = get_object_or_404(
            Mailing, pk=pk, owner=request.user
        )  # Пользователи - только своих

    return render(request, "mailing/mailing_detail.html", {"mailing": mailing})


@login_required
def mailing_create(request):
    """Создание новой рассылки"""
    if request.method == "POST":
        form = MailingForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("mailing:mailing_list")
    else:
        form = MailingForm(user=request.user)

    return render(
        request,
        "mailing/mailing_form.html",
        {"form": form, "title": "Создание новой рассылки"},
    )


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки (только своей для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        mailing = get_object_or_404(Mailing, pk=pk)  # Менеджеры могут редактировать все
    else:
        mailing = get_object_or_404(
            Mailing, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        form = MailingForm(request.POST, instance=mailing, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("mailing:mailing_detail", pk=mailing.pk)
    else:
        form = MailingForm(instance=mailing, user=request.user)

    return render(
        request,
        "mailing/mailing_form.html",
        {"form": form, "title": f"Редактирование рассылки #{mailing.pk}"},
    )


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки (только своей для пользователей)"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        mailing = get_object_or_404(Mailing, pk=pk)  # Менеджеры могут удалять все
    else:
        mailing = get_object_or_404(
            Mailing, pk=pk, owner=request.user
        )  # Пользователи - только своих

    if request.method == "POST":
        mailing.delete()
        return redirect("mailing:mailing_list")

    return render(request, "mailing/mailing_confirm_delete.html", {"mailing": mailing})


# ОТПРАВКА РАССЫЛКИ
@login_required
def send_mailing_now(request, pk):
    """Ручной запуск рассылки"""
    if (
        request.user.groups.filter(name="Менеджеры").exists()
        or request.user.is_superuser
    ):
        mailing = get_object_or_404(Mailing, pk=pk)  # Менеджеры могут запускать все
    else:
        mailing = get_object_or_404(
            Mailing, pk=pk, owner=request.user
        )  # Пользователи - только свои

    now = timezone.now()
    if mailing.start_time <= now <= mailing.end_time:
        sent_count = 0
        failed_count = 0

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                # Запись успешной попытки
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="success",
                    server_response=f"Успешно отправлено клиенту {client.email}",
                )
                sent_count += 1
            except Exception as e:
                # Запись неудачной попытки
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status="failed",
                    server_response=f"Ошибка: {str(e)}",
                )
                failed_count += 1

        if sent_count > 0:
            messages.success(
                request,
                f"Рассылка отправлена! Успешно: {sent_count}, Неудачно: {failed_count}",
            )
        else:
            messages.warning(
                request, f"Все отправки завершились с ошибкой. Неудачно: {failed_count}"
            )
    else:
        messages.error(
            request, "Рассылка не может быть запущена: время рассылки неактивно"
        )

    return redirect("mailing:mailing_list")


# ОБРАБОТКА ОШИБОК
def custom_permission_denied(request, exception=None):
    """Кастомная страница для ошибки 403 (доступ запрещен)"""
    return render(request, "mailing/access_denied.html", status=403)
