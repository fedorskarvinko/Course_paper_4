from django.urls import path

from mailing import views
from mailing.apps import MailingConfig

app_name = MailingConfig.name

urlpatterns = [
    path("", views.home, name="home"),
    path("clients/", views.client_list, name="client_list"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:pk>/update/", views.client_update, name="client_update"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/create/", views.message_create, name="message_create"),
    path("messages/<int:pk>/update/", views.message_update, name="message_update"),
    path("messages/<int:pk>/delete/", views.message_delete, name="message_delete"),
    path("mailing/<int:pk>/send/", views.send_mailing_now, name="send_mailing"),
    path("mailing/<int:pk>/send/", views.send_mailing_now, name="send_mailing"),
    path("mailings/", views.mailing_list, name="mailing_list"),
    path("mailings/<int:pk>/", views.mailing_detail, name="mailing_detail"),
    path("mailings/create/", views.mailing_create, name="mailing_create"),
    path("mailings/<int:pk>/update/", views.mailing_update, name="mailing_update"),
    path("mailings/<int:pk>/delete/", views.mailing_delete, name="mailing_delete"),
]
