from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Client, Mailing, Message


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@mail.com"}
            ),
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Иванов Иван Иванович"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Дополнительная информация",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "email": "Email адрес",
            "full_name": "ФИО",
            "comment": "Комментарий",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]
        # Проверяем, есть ли уже клиент с таким email (кроме текущего)
        if self.instance.pk:  # если это редактирование существующего
            if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Клиент с таким email уже существует")
        else:  # если это создание нового
            if Client.objects.filter(email=email).exists():
                raise ValidationError("Клиент с таким email уже существует")
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
        return instance


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Тема письма"}
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Текст письма",
                    "rows": 5,
                }
            ),
        }
        labels = {
            "subject": "Тема письма",
            "body": "Текст письма",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if len(subject) < 5:
            raise ValidationError("Тема письма должна быть не менее 5 символов")
        return subject

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
        return instance


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "clients"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "message": forms.Select(attrs={"class": "form-control"}),
            "clients": forms.SelectMultiple(attrs={"class": "form-control"}),
        }
        labels = {
            "start_time": "Время начала рассылки",
            "end_time": "Время окончания рассылки",
            "message": "Сообщение для отправки",
            "clients": "Получатели (клиенты)",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Фильтруем сообщения и клиентов только текущего пользователя
        if self.user:
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)
            self.fields["clients"].queryset = Client.objects.filter(owner=self.user)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError(
                    "Время начала должно быть раньше времени окончания"
                )

            if start_time < timezone.now():
                raise ValidationError("Время начала не может быть в прошлом")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner = self.user
        if commit:
            instance.save()
            self.save_m2m()  # Важно для ManyToMany поля clients
        return instance
