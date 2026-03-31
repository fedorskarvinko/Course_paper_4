from django.db import models

class Recipient(models.Model):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    mailing = models.ForeignKey('mailing.Mailing', on_delete=models.CASCADE, related_name='recipients')

class Message(models.Model):
    subject = models.CharField(max_length=100)
    message = models.TextField()


class Mailing(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(choices=[('Created', 'Создана'),('Started', 'Запущена'), ('Finished', 'Завершена')], default='Created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)


class Attempt(models.Model):
    attempt_time = models.DateTimeField()
    status = models.CharField(choices=[('Success','Успешно'),('Fail','Не успешно')])
    server_response = models.TextField()
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)