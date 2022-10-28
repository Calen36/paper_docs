import re

from django.db import models
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField


# в боковом меню django-admin индентация пробелами и табами не работает (но при этом влияет на порядок пукнктов меню)
menu_indent = "   "

"""___________________________МОДЕЛИ КАТЕГОРИЙ___________________________"""


class OutgoingType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип исходящего письма'
        verbose_name_plural = 'Типы исходящих писем'


class WayOfDelivery(models.Model):
    """Способ передачи оригинала письма (почта, курьер, лично)"""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Способ отправки'
        verbose_name_plural = 'Способы отправки'


class Executor(models.Model):
    """Исполнитель внутри нашей организации"""
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
    """Кадастровый номер"""
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
    """Георафические объекты. Могут быть вложены один в другой.
    Например: 'Краснодарский край', 'Абинский р-н', 'Нефтегорское г.п.' """
    class Meta:
        verbose_name = 'Географическая привязка'
        verbose_name_plural = 'Географическая привязка'

    def get_extension_url(self):
        url = f"/admin/letters/geotag/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.name}</a>")

    get_link_name.short_description = ''


class Thematics(BaseHierarchicalProperty):
    """Произвольная тематика, которую можно задать для письма. Могут быть древовидно вложены одна в другую.
    Пример: 'Нарушения в Лесном фонде' <- 'Незаконные вырубки' <- 'Вырубка в Шабановском лесничестве' """
    class Meta:
        verbose_name = 'Тематика'
        verbose_name_plural = ' Тематики'

    def get_extension_url(self):
        url = f"/admin/letters/thematics/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.name}</a>")

    get_link_name.short_description = ''


class Forestry(BaseHierarchicalProperty):
    """Объекты лесного фонда. Могут быть иерархически вложены друг в друга."""
    class Meta:
        verbose_name = 'Объект Лесного Фонда'
        verbose_name_plural = 'Объекты Лесного Фонда'

    def get_extension_url(self):
        url = f"/admin/letters/forestry/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.name}</a>")

    get_link_name.short_description = ''


class WaterObj(BaseHierarchicalProperty):
    """Водные объекты. Могут быть иерархически вложены друг в друга."""
    class Meta:
        verbose_name = 'Водный объект'
        verbose_name_plural = 'Водные объекты'

    def get_extension_url(self):
        url = f"/admin/letters/waterobj/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.name}</a>")

    get_link_name.short_description = ''


"""___________________________МОДЕЛИ КОНТРАГЕНТОВ___________________________"""


class CounterpartyType(models.Model):
    """Категория для типов контрагента. Варианты: Организация, Должность, Лицо"""
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
    """Базовая модель контрагента. Контрагенты предполагают вложенность Лицо > Должность > Организация"""
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
    """Модель для контрагентов уровня Организация"""
    class Meta:
        proxy = True
        verbose_name = 'организацию'
        verbose_name_plural = f'     {menu_indent}🏦 Организации'
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
    """Модель для контрагентов уровня Должность"""
    class Meta:
        proxy = True
        verbose_name = 'должность'
        verbose_name_plural = f'    {menu_indent}💼 Должности'
        # ordering = ('name',)

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=2)
        super(Position, self).save()

    def __str__(self):
        return f"{self.name} ({self.parent.name})"

    # get_full_name.short_description = 'Должностные позиции'


class Person(Counterparty):
    """Модель для контрагентов уровня Лицо"""
    class Meta:
        proxy = True
        verbose_name = 'должностное лицо'
        verbose_name_plural = f'   {menu_indent}👤 Лица'
        # ordering = ('name',)

    def save(self, *args, **kwargs):
        self.type = CounterpartyType.objects.get(pk=3)
        super(Person, self).save()

    def __str__(self):
        return self.get_full_name()


"""___________________________МОДЕЛИ ПИСЕМ___________________________"""


def get_upload_path(instance, filename):
    """Формирует путь для сохранения файла скана письма, исходя из года письма и имени подкалогда для данного типа писем"""
    return f"{instance.sign_date.year}/{instance.type.folder}/{filename}"


class BaseLetter(MPTTModel):
    """Модель, содержащая все виды полей, которые встречаются во всех типы писем. Необходима для того, чтобы разные типы
    писем можно было свободно использовать как узлы дерева переписки (библиотека mptt). Отображаемая форма в админке зависит от
    значения поля type (для входящих - одна форма, для исходящих - другая, для редиректов - третья и т.п."""
    type = models.ForeignKey('LetterType', on_delete=models.CASCADE, blank=True, null=True, )
    out_type = models.ForeignKey('OutgoingType', on_delete=models.PROTECT, blank=True, null=True, default=1)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Ответ на')
    number = models.CharField(max_length=64, unique=True, verbose_name='Номер')
    counterparty = TreeForeignKey('Counterparty', on_delete=models.CASCADE, verbose_name='Контрагент')
    subj = models.TextField(null=True, blank=True, verbose_name='Тема письма')
    sign_date = models.DateField(verbose_name='Дата письма')
    way_of_delivery = models.ForeignKey('WayOfDelivery', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Способ отправки')

    executor = models.ManyToManyField('Executor', blank=True, verbose_name='Подписано/Исполнитель')
    inbound_number = models.CharField(max_length=128, blank=True, null=True, verbose_name='Входящий номер')
    outgoing_number = models.CharField(max_length=64, blank=True, null=True, verbose_name='Исходящий номер')
    signed_by = models.CharField(max_length=255, blank=True, null=True, verbose_name='Подписано')
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name='Исполнитель в госоргане')
    receive_date = models.DateField(blank=True, null=True, verbose_name='Дата получения')
    send_date = models.DateField(blank=True, null=True, verbose_name='Дата отправки')

    thematics = TreeManyToManyField('Thematics', blank=True, verbose_name='Тема')
    geotag = TreeManyToManyField('GeoTag', blank=True, verbose_name='Географическая привязка')
    cad_num = models.ManyToManyField('CadNum', blank=True, verbose_name='Кадастровые Номера',)
    forestry = TreeManyToManyField('Forestry', blank=True, verbose_name='Объект Лесного Фонда')
    waterobj = TreeManyToManyField('WaterObj', blank=True, verbose_name='Водный объект')
    cipher = models.CharField(max_length=255, blank=True, null=True, verbose_name='Идентификатор темы')

    tiff_file = models.FileField(blank=True, null=True, upload_to=get_upload_path, verbose_name='Файл TIFF')
    pdf_file = models.FileField(blank=True, null=True, upload_to=get_upload_path, verbose_name='Файл PDF')
    pagemaker_file = models.FileField(blank=True, null=True, upload_to=get_upload_path, verbose_name='Файл Pagemaker')

    completed = models.BooleanField(default=False, verbose_name='Завершено (применяется ко всей ветке переписки)')
    inaction = models.BooleanField(default=False, verbose_name='Бездействие')

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = '        Все письма'

    def get_full_name(self):
        if self.type:
            counterparty = self.counterparty.name[:50] if self.counterparty else ''
            counterparty = counterparty + ("..." if len(self.counterparty.name) > 50 else '')
            subject = self.subj[:80] if self.subj else ''
            subject = subject + ('...' if len(subject) > 80 else '')
            return f"{'📌 ' if self.inaction else ''}{self.type.abbr} {self.number} ❱ {self.sign_date} ❱ {counterparty} ❱ {subject}"
        return self.number

    get_full_name.short_description = 'Письма'

    def __str__(self):
        if self.type:
            return self.get_full_name()
        return self.number

    def get_extension_url(self):
        url = f"/admin/letters/{self.type.url}/{self.pk}"
        return url

    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.get_full_name()}</a>")

    class MPTTMeta:
        order_insertion_by = ['-sign_date']

    def save(self, *args, recurse=True, **kwargs):
        """ Применяет некоторые настройки ко всей ветке писем"""
        super(BaseLetter, self).save()
        if recurse:
            family = BaseLetter.objects.get(pk=self.pk).get_family()
            for relative in family:
                if relative.pk != self.pk:
                    if relative.completed != self.completed:
                        relative.completed = self.completed
                    if self.out_type:
                        relative.out_type = OutgoingType.objects.get(pk=self.out_type_id)
                    relative.save(recurse=False)


class OutEcoLetter(BaseLetter):
    """Модель для ИСХОДЯЩИХ писем"""
    class Meta:
        proxy = True
        verbose_name = 'Исходящее письмо'
        verbose_name_plural = f'       {menu_indent}📨 Исходящие'  # отступ в начале строки в админке не отображается, но влияет на положение пункта при сортировке.

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=2)
        super(OutEcoLetter, self).save()


class IncomingLetter(BaseLetter):
    """Модель для ВХОДЯЩИХ писем"""
    class Meta:
        proxy = True
        verbose_name = 'Входящее письмо'
        verbose_name_plural = f'       {menu_indent}📩 Входящие'  # отступ в начале строки в админке не отображается, но влияет на положение пункта при сортировке.

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=1)
        if self.parent:  # TODO надо, наверное, данный функционал полностью засунуть в BaseLetter
            if self.parent.out_type:
                self.out_type = OutgoingType.objects.get(pk=self.parent.out_type_id)
        super(IncomingLetter, self).save()


class OmittedRedirect(BaseLetter):
    """Случай, когда контрагент не отвечая на письмо пересылает его другому контрагенту (высясняется обычно после того,
     как приходит ответ от второго контрагента."""
    class Meta:
        proxy = True
        verbose_name = 'Неприсланный пересыл'
        verbose_name_plural = f'       {menu_indent}🗰 Перенаправление'

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=3)
        if self.parent:
            if self.parent.out_type:
                self.out_type = OutgoingType.objects.get(pk=self.parent.out_type_id)
        super(IncomingLetter, self).save()


class LetterType(models.Model):
    index = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=127)
    abbr = models.CharField(max_length=8)
    folder = models.CharField(default='TMP', max_length=127)
    url = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип письма'
        verbose_name_plural = 'Типы писем'


class Attachment(models.Model):
    """Иногда к письму требуется приложить еще какой-либо произвольный документ"""
    description = models.TextField(blank=True, verbose_name='Описание')
    attached_to = models.ForeignKey('BaseLetter', on_delete=models.PROTECT, verbose_name='Письмо, к которому относится данное приложение')
    file = models.FileField(upload_to='ATTACHMENTS', verbose_name='Файл приложения')

    def __str__(self):
        return ''

    class Meta:
        verbose_name = 'Прикрепленный документ'
        verbose_name_plural = 'Прикрепленные документы'
