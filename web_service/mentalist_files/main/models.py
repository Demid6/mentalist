from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Агент"
        verbose_name_plural = "Агенты"

    def __str__(self):
        return self.username


class Comment(models.Model):
    username = models.CharField("Позывной", max_length=150)
    text = models.TextField("Версия", max_length=500)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "text": self.text,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M"),
        }

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Версия"
        verbose_name_plural = "Версии"
