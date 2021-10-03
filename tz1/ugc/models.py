from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID користувача в телеграмі',
        unique=True,
    )
    name = models.TextField(
        verbose_name='Ім`я користувача',
    )

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'


class Questionnaire(models.Model):
    chat_id = models.TextField(
        verbose_name='ID telegram',
    )
    login_telegram = models.TextField(
        verbose_name='Telegram логин пользователя',
    )
    reply_1 = models.TextField(
        verbose_name='Имя пользователь',
    )
    reply_2 = models.TextField(
        verbose_name='Номер телефона',
    )
    reply_3 = models.TextField(
        verbose_name='Ответ',
    )

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкети'
