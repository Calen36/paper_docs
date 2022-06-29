import re

from django.utils.safestring import mark_safe

from .models_cats import BaseHierarchicalProperty
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField, TreeManager

my_indent = "   "


class CounterpartyType(models.Model):
    index = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=127)
    mini = models.CharField(max_length=16, blank=True)
    url = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип контрагента'
        verbose_name_plural = 'Типы контрагентов'


class Counterparty(BaseHierarchicalProperty):
    type = models.ForeignKey('CounterpartyType', default=3, on_delete=models.CASCADE, blank=True, null=True, )
    name = models.CharField(max_length=255, verbose_name='')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Относится к категории')
    prev_org = TreeForeignKey('Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='renamed', verbose_name='Предыдущее название организации')
    prev_pos = TreeForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True, related_name='relocated', verbose_name='Предыдущая позиция')

    def get_full_name(self):
        if self.parent:
            return f"{self.name} ❱ {self.parent.get_full_name()}"
        if str(self.type) == "Лицо":
            return f"🔥 {self.name}"
        return f"{self.name}"

    def get_list_name(self):
        return f"{self.type.mini} {self.get_full_name()}"

    get_list_name.short_description = 'Контрагенты'

    def __str__(self):
        return self.get_list_name()

    def get_extension_url(self):
        url = f"/admin/letters/{self.type.url}/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.name}</a>")

    get_link_name.short_description = ''

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = '      Контрагенты'

    class MPTTMeta:
        order_insertion_by = ('name',)


class Organization(Counterparty):

    class Meta:
        proxy = True
        verbose_name = 'организацию'
        verbose_name_plural = f'     {my_indent}🏦 Организации'
        # ordering = ('name',)

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=1)
        super(Organization, self).save()
        if re.findall(r'Прокуратура', self.name, flags=re.I):
            Position.objects.create(name='Прокурор', parent=self)
            Position.objects.create(name='И.О. прокурора', parent=self)
            Position.objects.create(name='1й зам. прокурора', parent=self)
            Position.objects.create(name='2й зам. прокурора', parent=self)


class Position(Counterparty):
    class Meta:
        proxy = True
        verbose_name = 'должность'
        verbose_name_plural = f'    {my_indent}💼 Должности'
        # ordering = ('name',)

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=2)
        super(Position, self).save()

    def __str__(self):
        return f"{self.name} ({self.parent.name})"

    # get_full_name.short_description = 'Должностные позиции'


class Person(Counterparty):
    class Meta:
        proxy = True
        verbose_name = 'должностное лицо'
        verbose_name_plural = f'   {my_indent}👤 Лица'
        # ordering = ('name',)


    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=3)
        super(Person, self).save()

    # get_full_name.short_description = 'Должностные лица'

    def __str__(self):
        return self.get_full_name()



