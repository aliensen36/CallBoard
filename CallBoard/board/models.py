from django.contrib.auth.models import AbstractUser
from django.db import models
from board.utilites import get_timestamp_path

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Слать оповещения о новых комментариях?')

    def delete(self, *args, **kwargs):
        for ad in self.ad_set.all():
            ad.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass

class Advert(models.Model):
    category = models.ForeignKey('Category', null=True,
                                 on_delete=models.PROTECT,
                                 verbose_name='Категория')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, default='', on_delete=models.CASCADE,
                               verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']

class AdditionalImage(models.Model):
    ad = models.ForeignKey(Advert, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path,
                              verbose_name='Изображение')

    class Meta:
        verbose_name_plural = 'Дополнительные иллюстрации'
        verbose_name = 'Дополнительная иллюстрация'

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True,
                            db_index=True, verbose_name='Категория')
    # order = models.SmallIntegerField(default=0, db_index=True,
    #                                  verbose_name='Порядок')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'
        ordering = ['name']

class Comment(models.Model):
    ad = models.ForeignKey(Advert, on_delete=models.CASCADE,
                           verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликован')

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ['created_at']
