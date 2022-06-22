from .models_cats import *
from .models_ctrp import *
from django.utils.safestring import mark_safe


def get_upload_path(instance, filename):
    return f"{instance.sign_date.year}/{instance.type.folder}/{filename}"


class BaseLetter(MPTTModel):
    type = models.ForeignKey('LetterType', on_delete=models.CASCADE, blank=True, null=True, )
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

    tiff_file = models.FileField(blank=True, null=True, upload_to=f"OUT", verbose_name='Файл TIFF')
    pdf_file = models.FileField(blank=True, null=True, upload_to=get_upload_path, verbose_name='Файл PDF')
    pagemaker_file = models.FileField(blank=True, null=True, upload_to=f"OUT", verbose_name='Файл Pagemaker')

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


    def get_link_name(self):
        return mark_safe(f"<a href={self.get_extension_url()}>{self.get_full_name()}</a>")


    def __str__(self):
        if self.type:
            return self.get_full_name()
        return self.number

    def get_extension_url(self):
        url = f"/admin/letters/{self.type.url}/{self.pk}"
        return url

    class MPTTMeta:
        order_insertion_by = ['-sign_date']

    def save(self, *args, recurse=True, **kwargs):
        """ Применяет некоторые настройки ко всей ветке писем"""
        print(self.pdf_file)

        super(BaseLetter, self).save()
        if recurse:
            family = BaseLetter.objects.get(pk=self.pk).get_family()
            for relative in family:
                if relative.pk != self.pk and relative.completed != self.completed:
                    relative.completed = self.completed
                    relative.save(recurse=False)


class OutEcoLetter(BaseLetter):
    """ ИСХОДЯЩИЕ """

    class Meta:
        proxy = True
        verbose_name = 'Исходящее письмо (экология)'
        verbose_name_plural = f'       {my_indent}📨 Исходящие (эко)'

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=2)
        super(OutEcoLetter, self).save()


class IncomingLetter(BaseLetter):
    """ ВХОДЯЩИЕ """
    class Meta:
        proxy = True
        verbose_name = 'Входящее письмо'
        verbose_name_plural = f'       {my_indent}📩 Входящие'

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=1)
        super(IncomingLetter, self).save()


class OmittedRedirect(BaseLetter):
    """ Неприсланное перенаправление """
    class Meta:
        proxy = True
        verbose_name = 'Неприсланный пересыл'
        verbose_name_plural = f'       {my_indent}🗰 Перенаправление'

    def save(self, *args, **kwargs):
        self.type = LetterType.objects.get(pk=3)
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
    description = models.TextField(blank=True, verbose_name='Описание')
    attached_to = models.ForeignKey('BaseLetter', on_delete=models.PROTECT, verbose_name='Письмо, к которому относится данное приложение')
    file = models.FileField(upload_to='ATTACHMENTS', verbose_name='Файл приложения')

    def __str__(self):
        return ''

    class Meta:
        verbose_name = 'Прикрепленный документ'
        verbose_name_plural = 'Прикрепленные документы'

