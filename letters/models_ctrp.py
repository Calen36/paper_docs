from .models_cats import BaseHierarchicalProperty
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField, TreeManager

my_indent = "   "


class CounterpartyType(models.Model):
    index = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=127)
    mini = models.CharField(max_length=16, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип контрагента'
        verbose_name_plural = 'Типы контрагентов'


class Counterparty(BaseHierarchicalProperty):
    type = models.ForeignKey('CounterpartyType', default=3, on_delete=models.CASCADE, blank=True, null=True, )
    name = models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Относится к категории')
    prev_org = TreeForeignKey('Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='renamed', verbose_name='Предыдущее название организации')
    prev_pos = TreeForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True, related_name='relocated', verbose_name='Предыдущая позиция')

    def get_full_name(self):
        if self.parent:
            return f"{str(self.parent)} {self.name}"
        return self.name

    def get_fancy_name(self):
        return f"{self.type.mini}  {self.name}"

    get_fancy_name.short_description = 'Контрагенты'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = '      Контрагенты'


class Organization(Counterparty):

    def get_fancy_name(self):
        return super(Organization, self).get_fancy_name()
    get_fancy_name.short_description = 'Организации'

    class Meta:
        proxy = True
        verbose_name = 'организацию'
        verbose_name_plural = f'     {my_indent}🏦 Организации'

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=1)
        super(Organization, self).save()


class Position(Counterparty):
    class Meta:
        proxy = True
        verbose_name = 'должость'
        verbose_name_plural = f'    {my_indent}Должности'

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=2)
        super(Position, self).save()

    def __str__(self):
        return f"{self.name} ({self.parent.name})"

    def get_full_name(self):
        if self.parent:
                return f"{self.parent.name} ❱ {self.name}"
        return f'🠶 {self.name}'

    get_full_name.short_description = 'Должностные позиции'


class Person(Counterparty):
    class Meta:
        proxy = True
        verbose_name = 'должностное лицо'
        verbose_name_plural = f'   {my_indent}👤 Лица'

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=3)
        super(Person, self).save()

    def get_full_name(self):
        if self.parent:
            if self.parent.parent:
                return f"{self.type.mini} {self.parent.name} {self.name} ({self.parent.parent.name})"
        return f'🠶 {self.name}'

    get_full_name.short_description = 'Должностные лица'



