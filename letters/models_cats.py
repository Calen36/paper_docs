from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField, TreeManager


class WayOfDelivery(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Способ отправки'
        verbose_name_plural = 'Способы отправки'


class Executor(models.Model):
    surname = models.CharField(max_length=64, verbose_name='Фамилия')
    name = models.CharField(max_length=64, verbose_name='Имя')
    patronimic = models.CharField(max_length=64, verbose_name='Отчество')


    def __str__(self):
        n = str(self.name)[0].upper() if str(self.name) else ''
        p = str(self.patronimic)[0].upper() if str(self.patronimic) else ''
        return f"{self.surname} {n}.{p}."

    class Meta:
        verbose_name = 'Подписано/Исполнитель'
        verbose_name_plural = 'Подписано/Исполнители'
        ordering = ('surname', 'name')

class CadNum(models.Model):
    """ Кадастровый номер """
    name = models.CharField(max_length=255, verbose_name='Название', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кадастровый номер'
        verbose_name_plural = 'Кадастровые номера'


class BaseHierarchicalProperty(MPTTModel):
    """Абстрактный класс для создания иерархически вложенных атрибутов писем"""
    name = models.CharField(max_length=255, verbose_name='Название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Относится к категории')

    def __str__(self):
        if self.parent:
            return f"{str(self.parent)} ⊳ {self.name}"
        return self.name

    class Meta:
        abstract = True


class GeoTag(BaseHierarchicalProperty):
    class Meta:
        verbose_name = 'Географическая привязка'
        verbose_name_plural = 'Географическая привязка'


class Thematics(BaseHierarchicalProperty):
    class Meta:
        verbose_name = 'Тематика'
        verbose_name_plural = ' Тематики'


class Forestry(BaseHierarchicalProperty):
    class Meta:
        verbose_name = 'Объект Лесного Фонда'
        verbose_name_plural = 'Объекты Лесного Фонда'


class WaterObj(BaseHierarchicalProperty):
    class Meta:
        verbose_name = 'Водный объект'
        verbose_name_plural = 'Водные объекты'
