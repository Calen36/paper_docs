import datetime

from django.contrib import admin
from django.contrib.admin import SimpleListFilter, DateFieldListFilter
from django.contrib.admin.widgets import AutocompleteSelectMultiple

from django.db.models import Q, F
from django.forms import CheckboxSelectMultiple, TextInput, Textarea
from django.forms.models import BaseInlineFormSet
from mptt.admin import MPTTModelAdmin

from rangefilter.filters import DateRangeFilter

from .models import *

admin.site.site_title = 'Служебная Переписка'
admin.site.site_header = 'Служебная Переписка'
admin.site.index_title = ' '


"""___________________________АДМИНКИ КАТЕГОРИЙ___________________________"""


class AbsMultiCatAdmin(MPTTModelAdmin):
    """Абстрактный класс админки для MPTT моделей"""
    autocomplete_fields = ('parent',)
    search_fields = ('name',)
    list_display = ('name',)
    mptt_level_indent = 40

    def get_actions(self, request):
        return []

    class Meta:
        abstract = True


class AbstractInline(admin.TabularInline):
    """Абстрактный инлайн для всех типов инлайнов у MTTP Моделей.
    У объекта-родителя в инлайне отображаются дочерние объекты"""
    fk_name = 'parent'
    extra = 0
    verbose_name_plural = 'Подкатегории'
    readonly_fields = ('get_link_name',)
    fields = ('get_link_name',)
    # show_change_link = True

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False

    class Meta:
        abstract = True


class GeoInline(AbstractInline):
    """Инлайн для вложенных объектов Географической привязки"""
    model = GeoTag


@admin.register(GeoTag)
class GeoTagAdmin(AbsMultiCatAdmin):
    """Админка для ГЕОГРАФИЧЕСКОЙ ПРИВЯЗКИ"""
    inlines = (GeoInline,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ПИСЬМА, СВЯЗАННЫЕ С ДАННОЙ ЛОКАЦИЕЙ'
        letters = BaseLetter.objects.none()
        geotags = GeoTag.objects.get(pk=object_id).get_descendants(include_self=True)
        for gt in geotags:
            letters |= BaseLetter.objects.filter(geotag=gt)
        extra_context['letters'] = letters.distinct()
        return super(GeoTagAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


class ThematicsInline(AbstractInline):
    """Инлайн для вложенных тематик"""
    model = Thematics
    verbose_name_plural = 'Подтемы'


@admin.register(Thematics)
class ThematicsAdmin(AbsMultiCatAdmin):
    """Админка для ТЕМАТИК переписки"""
    inlines = (ThematicsInline,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ПИСЬМА ПО ДАННОЙ ТЕМАТИКЕ'
        themes = Thematics.objects.get(pk=object_id).get_descendants(include_self=True)
        letters = BaseLetter.objects.none()
        for t in themes:
            letters |= BaseLetter.objects.filter(thematics=t)
        extra_context['letters'] = letters.distinct()
        return super(ThematicsAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


class ForestryInline(AbstractInline):
    """Инлайн для вложенных объектов лесного фонда"""
    model = Forestry


@admin.register(Forestry)
class ForestryAdmin(AbsMultiCatAdmin):
    """Админка для объектов ЛЕСНОГО ФОНДА"""
    inlines = (ForestryInline,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ПИСЬМА, ОТНОСЯЩИЕСЯ К ДАННОМУ ОБЪЕКТУ ЛЕСНОГО ФОНДА'
        forest_objects = Forestry.objects.get(pk=object_id).get_descendants(include_self=True)
        letters = BaseLetter.objects.none()
        for f in forest_objects:
            letters |= BaseLetter.objects.filter(forestry=f)
        extra_context['letters'] = letters.distinct()
        return super(ForestryAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


class WaterObjInline(AbstractInline):
    """Инлайн для вложенных Водных объектов"""
    model = WaterObj


@admin.register(WaterObj)
class WaterObjAdmin(AbsMultiCatAdmin):
    """Админка для ВОДНЫХ ОБЪЕКТОВ"""
    inlines = (WaterObjInline,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ПИСЬМА, ОТНОСЯЩИЕСЯ К ДАННОМУ ВОДНОМУ ОБЪЕКТУ'
        water_objects = WaterObj.objects.get(pk=object_id).get_descendants(include_self=True)
        letters = BaseLetter.objects.none()
        for wo in water_objects:
            letters |= BaseLetter.objects.filter(waterobj=wo)
        extra_context['letters'] = letters.distinct()
        return super(WaterObjAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


@admin.register(CadNum)
class CadNumAdmin(admin.ModelAdmin):
    """Админка для КАДАСТРОВЫХ НОМЕРОВ"""
    search_fields = ('name',)

    def get_actions(self, request):
        return []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ПИСЬМА, ОТНОСЯЩИЕСЯ К ДАННОМУ КАДАСТРОВОМУ НОМЕРУ'
        cad_num = CadNum.objects.get(pk=object_id)
        letters = BaseLetter.objects.filter(cad_num=cad_num)
        extra_context['letters'] = letters
        return super(CadNumAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


# class WayOfDeliveryLettersInline(AbstractInline):
#     model = BaseLetter
#     fk_name = None
#     verbose_name_plural = 'Письма, доставленные выбранным способом'
#     fields = ('number', 'sign_date', 'counterparty', 'subj')


@admin.register(WayOfDelivery)
class WayOfDeliveryAdmin(admin.ModelAdmin):
    """Админка для СПОСОБОВ ДОСТАВКИ писем"""
    # inlines = (WayOfDeliveryLettersInline,)

    def get_actions(self, request):
        return []


# class ExecutorLettersInline(AbstractInline):
#     model = BaseLetter.executor.through
#     fk_name = None
#     verbose_name_plural = 'Письма, подписанные выбранным исполнителем'
#     readonly_fields = ()
#     fields = ('name',)


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    """Админка для ИСПОЛНИТЕЛЕЙ (в нашей организации)"""
    search_fields = ('surname', 'name', 'patronimic')
    # inlines = (ExecutorLettersInline,)
    list_per_page = 50

    def get_actions(self, request):
        return []


@admin.register(LetterType)
class LetterTypeAdmin(admin.ModelAdmin):
    """Админка для ТИПОВ ПИСЕМ"""
    def get_actions(self, request):
        return []


@admin.register(OutgoingType)
class OutgoingTypeAdmin(admin.ModelAdmin):
    """Админка для ТИПОВ ИСХОДЯЩИХ писем"""
    def get_actions(self, request):
        return []


class AttachmentInline(admin.TabularInline):
    """Инлайн для ДОПОЛНИТЕЛЬНЫХ ДОКУМЕНТОВ"""
    model = Attachment
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


"""___________________________АДМИНКИ КОНТРАГЕНТОВ___________________________"""


@admin.register(CounterpartyType)
class CounterpartyTypeAdmin(admin.ModelAdmin):
    """Админка для ТИПОВ КОНТРАГЕНТОВ"""
    pass


class PositionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PositionInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline


class PositionInline(AbstractInline):
    """Инлайн для ДОЛЖНОСТЕЙ в данной организации"""
    model = Position
    verbose_name_plural = 'Должностные позиции в данной организации'


class PersonInline(AbstractInline):
    """Админка для конкретных должностных ЛИЦ"""
    model = Person
    verbose_name_plural = 'Лица, занимавшие данную позицию'
    # fields = ('name',)


class OrganizationInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(OrganizationInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline


@admin.register(Counterparty)
class CounterpartyAdmin(AbsMultiCatAdmin):
    """Админка для всех КОНТРАГЕНТОВвместе """
    list_display = ('get_list_name',)
    save_on_top = True
    search_fields = ('name',)
    # list_per_page = 40

    def get_queryset(self, request):
        return Counterparty.objects.select_related('type', 'parent', 'parent__parent')

    def has_add_permission(self, request):
        return False


@admin.register(Organization)
class OrganizationAdmin(AbsMultiCatAdmin):
    """Админка для контрагентов-ОРГАНИЗАЦИЙ"""
    list_display = ('get_list_name',)
    inlines = (PositionInline,)
    autocomplete_fields = ('parent', 'prev_org')
    search_fields = ('name',)

    def get_queryset(self, request):
        return Counterparty.objects.filter(type=1).select_related('type')

    def get_exclude(self, request, obj=None):
        return 'type', 'parent', 'prev_pos'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ВСЯ ПЕРЕПИСКА С ДАННОЙ ОРАГНИЗАЦИЕЙ'
        letters = BaseLetter.objects.none()
        counterparties = Counterparty.objects.get(pk=object_id).get_descendants(include_self=True)
        for c in counterparties:
            letters |= BaseLetter.objects.filter(counterparty=c)
        extra_context['letters'] = letters.distinct()
        return super(OrganizationAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


@admin.register(Position)
class PositionAdmin(AbsMultiCatAdmin):
    """Админка для контрагентов-ДОЛЖНОСТНЫХ ПОЗИЦИЙ"""
    list_display = ('get_list_name',)
    inlines = (PersonInline,)
    mptt_level_indent = 0
    search_fields = ('name', 'parent__name',)

    def get_queryset(self, request):
        return Position.objects.filter(type=2).select_related('type', 'parent')

    def get_exclude(self, request, obj=None):
        return 'type', 'prev_pos', 'prev_org'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ВСЯ ПЕРЕПИСКА С ЛИЦАМИ НА ДАННОЙ ДОЛЖНОСТНОЙ ПОЗИЦИИ'
        letters = BaseLetter.objects.none()
        counterparties = Counterparty.objects.get(pk=object_id).get_descendants(include_self=True)
        for c in counterparties:
            letters |= BaseLetter.objects.filter(counterparty=c)
        extra_context['letters'] = letters.distinct()
        return super(PositionAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


@admin.register(Person)
class PersonAdmin(AbsMultiCatAdmin):
    """Админка для контрагентов-конкретных должностных ЛИЦ"""
    list_display = ('get_list_name',)
    search_fields = ('name', 'parent__name', 'parent__parent__name')
    autocomplete_fields = ('parent', 'prev_pos')
    mptt_level_indent = 0

    def get_queryset(self, request):
        return Person.objects.filter(type=3).select_related('type', 'parent', 'parent__parent')

    def get_exclude(self, request, obj=None):
        return 'type', 'prev_org'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].verbose_name = "my verbose name"
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ВСЯ ПЕРЕПИСКА С ДАННЫМ ДОЛЖНОСТНЫМ ЛИЦОМ'
        person = Counterparty.objects.get(pk=object_id)
        letters = BaseLetter.objects.filter(counterparty=person)
        extra_context['letters'] = letters
        return super(PersonAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)


"""___________________________АДМИНКИ ПИСЕМ___________________________"""


class OutDueFilter(SimpleListFilter):
    """ Фильтрует письма, на которые не пришло ответа в течение 30 дней """
    title = 'Нет ответа 30 дней'
    parameter_name = 'due'

    def get_y_qs(self):
        limitday = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        return OutEcoLetter.objects.filter(Q(completed=0) & Q(send_date__lt=limitday) & Q(rght=F('lft') + 1)).select_related('type', 'counterparty')  # если поле rght == lft+1, то значит текущая нода является лепестком дерева

    def lookups(self, request, model_admin):
        x = self.get_y_qs().count()
        if x:
            return (('y', f'Да ({x})'),)
        return None

    def queryset(self, request, queryset):
        if self.value() == 'y':
            return self.get_y_qs()


class BaseCompletedFilter(SimpleListFilter):
    """ Фильтрует завершенные цепочки писем"""
    title = 'Завершено'
    parameter_name = 'completed'

    def lookups(self, request, model_admin):
        return ('y', 'Да'), ('n', 'Нет')

    def queryset(self, request, queryset):
        if self.value() == 'y':
            result = BaseLetter.objects.filter(completed=1).select_related('type', 'counterparty')
            return result

        if self.value() == 'n':
            result = BaseLetter.objects.filter(completed=0).select_related('type', 'counterparty')
            return result


class BaseYearsFilter(SimpleListFilter):
    """Фильтрует письма за Выбранный год"""
    title = 'По годам'
    parameter_name = 'years'

    def lookups(self, request, model_admin):
        curr_year = datetime.datetime.now().year
        years = [(y, y) for y in range(curr_year, 2018, -1)]
        return years

    def queryset(self, request, queryset):

        print(self.value(), type(self.value()))
        if self.value():
            result = BaseLetter.objects.filter(Q(sign_date__gte=f'{self.value()}-01-01') & Q(sign_date__lte=f'{self.value()}-12-31')).select_related('type', 'counterparty')
            return result


class BaseTypeFilter(SimpleListFilter):
    """Фильтрует все письма Письма по типу"""
    title = 'По типам'
    parameter_name = 'out_type'

    def lookups(self, request, model_admin):
        qs = OutgoingType.objects.all()
        return [(t.id, t.name) for t in qs]

    def queryset(self, request, queryset):
        if self.value():
            result = BaseLetter.objects.filter(out_type_id=self.value()).select_related('type', 'counterparty')
            return result


class OutTypeFilter(SimpleListFilter):
    """ Фильтрует исходящие письма по типам"""
    title = 'По типам'
    parameter_name = 'out_type'

    def lookups(self, request, model_admin):
        qs = OutgoingType.objects.all()
        return [(t.id, t.name) for t in qs]

    def queryset(self, request, queryset):
        if self.value():
            result = BaseLetter.objects.filter(Q(type=2) & Q(out_type_id=self.value())).select_related('type', 'counterparty')
            return result


class OutCompletedFilter(SimpleListFilter):
    """ Фильтрует завершенные исходящие письма"""
    title = 'Завершено'
    parameter_name = 'completed'

    def lookups(self, request, model_admin):
        return ('y', 'Да'), ('n', 'Нет')

    def queryset(self, request, queryset):
        if self.value() == 'y':
            result = OutEcoLetter.objects.filter(Q(type=2) & Q(completed=1)).select_related('type', 'counterparty')
            return result

        if self.value() == 'n':
            result = OutEcoLetter.objects.filter(Q(type=2) & Q(completed=0)).select_related('type', 'counterparty')
            return result


class InCompletedFilter(SimpleListFilter):
    """ Фильтрует завершенные входящие письма"""
    title = 'Завершено'
    parameter_name = 'completed'

    def lookups(self, request, model_admin):
        return ('y', 'Да'), ('n', 'Нет')

    def queryset(self, request, queryset):
        if self.value() == 'y':
            result = OutEcoLetter.objects.filter(Q(type=1) & Q(completed=1)).select_related('type', 'counterparty')
            return result

        if self.value() == 'n':
            result = OutEcoLetter.objects.filter(Q(type=1) & Q(completed=0)).select_related('type', 'counterparty')
            return result


class OutInactionFilter(SimpleListFilter):
    """Фильтр для писем с отметкой Бездействие"""
    title = 'Бездействие'
    parameter_name = 'inaction'

    def get_y_qs(self):
        return BaseLetter.objects.filter(Q(type=2) & Q(inaction=True)).select_related('type', 'counterparty')

    def lookups(self, request, model_admin):
        x = self.get_y_qs().count()
        if x:
            return (('y', f'Да ({x})'),)
        return None

    def queryset(self, request, queryset):
        # BaseLetter.tree.rebuild()
        if self.value() == 'y':
            return self.get_y_qs()


class LetterInline(AbstractInline):  # TODO нужность под вопросом
    """Инлайн для всех писем в данной категории"""
    model = BaseLetter
    fields = ('number', 'sign_date', 'counterparty', 'subj', )
    verbose_name_plural = 'Ответы'


class AbstractLetterAdmin(MPTTModelAdmin):
    """Абстрактная админка для всех типов писем"""
    autocomplete_fields = ('parent', 'counterparty', 'geotag', 'thematics', 'cad_num', 'forestry', 'waterobj',)
    list_display = ('get_full_name',)
    # list_display = ("number", "sign_date", "counterparty", "subj")
    search_fields = ('counterparty__name', 'number', 'subj', 'cipher')
    inlines = (AttachmentInline,)
    mptt_level_indent = 40
    save_on_top = True

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '100'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 100})},
    }

    def get_actions(self, request):
        return []

    class Meta:
        abstract = True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['object_id'] = int(object_id)
        extra_context['letters_title'] = 'ЛИНИЯ ПЕРЕПИСКИ'
        extra_context['letters'] = BaseLetter.objects.get(pk=object_id).get_root().get_descendants(include_self=True)
        return super(AbstractLetterAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context,)

    class Media:
        css = {
            'all': ('mystyles.css',)
        }


@admin.register(BaseLetter)
class BaseLetterAdmin(AbstractLetterAdmin):
    """Админка для всех видов писем сразу"""
    # list_display = ("type", "number", "sign_date", "counterparty", "subj")
    list_filter = (BaseTypeFilter, BaseCompletedFilter, OutInactionFilter, OutDueFilter, BaseYearsFilter, ('sign_date', DateRangeFilter),)

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return BaseLetter.objects.select_related('type', 'counterparty')

    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(OutEcoLetter)
class OutEcoLetterAdmin(AbstractLetterAdmin):
    """Админка для ИСХОДЯЩИХ писем"""
    mptt_level_indent = 0
    # form = OutEcoLetterAdminForm
    autocomplete_fields = AbstractLetterAdmin.autocomplete_fields + ('executor',)
    list_filter = (OutTypeFilter, OutCompletedFilter, OutInactionFilter, OutDueFilter, ('sign_date', DateRangeFilter))

    def get_queryset(self, request):
        return BaseLetter.objects.filter(type=2).select_related('type', 'counterparty')

    def get_exclude(self, request, obj=None):
        return 'type', 'outgoing_number', 'signed_by', 'contact', 'tiff_file', 'receive_date',


@admin.register(IncomingLetter)
class IncomingLetterAdmin(AbstractLetterAdmin):
    """Админка для ВХОДЯЩИХ писем"""
    mptt_level_indent = 0
    list_filter = (InCompletedFilter, ('sign_date', DateRangeFilter))

    def get_queryset(self, request):
        return BaseLetter.objects.filter(type=1).select_related('type', 'counterparty')

    def get_exclude(self, request, obj=None):
        return 'type', 'out_type', 'executor', 'pagemaker_file', 'inbound_number', 'inaction', 'send_date',


@admin.register(OmittedRedirect)
class OmittedRedirectAdmin(AbstractLetterAdmin):
    """Админка для скрытых РЕДИРЕКТОВ"""
    mptt_level_indent = 0
    list_filter = (InCompletedFilter, ('sign_date', DateRangeFilter))

    def get_queryset(self, request):
        return BaseLetter.objects.filter(type=3).select_related('type', 'counterparty')

    def get_exclude(self, request, obj=None):
        return 'type', 'out_type', 'subj', 'sign_date', 'way_of_delivery', 'executor', 'inbound_number', 'outgoing_number', 'signed_by', 'contact', 'receive_date', 'send_date', 'thematics', 'geotag', 'cad_num', 'forestry', 'waterobj', 'cipher', 'tiff_file', 'pdf_file', 'pagemaker_file', 'completed', 'inaction',

