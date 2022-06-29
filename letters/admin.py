import datetime
from copy import copy

from django import forms

from django.contrib.admin import SimpleListFilter, DateFieldListFilter
from django.contrib.admin.widgets import AutocompleteSelectMultiple

from django.db.models import Q, F
from django.forms import CheckboxSelectMultiple, TextInput, Textarea

from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter
from .admin_cats import *
from .admin_ctrp import *


admin.site.site_title = 'EWNC Переписка'
admin.site.site_header = 'EWNC Переписка'
admin.site.index_title = ' '


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
    """ Фильтрует завершенные письма"""
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
    """ Фильтрует завершенные письма"""
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
    """ Фильтрует завершенные письма"""
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
    """ Фильтрует завершенные письма"""
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
    """ Фильтрует завершенные письма"""
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
    """ Фильтрует завершенные письма"""
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
    """ Фильтр для отметки Бездействие """
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
    model = BaseLetter
    fields = ('number', 'sign_date', 'counterparty', 'subj', )
    verbose_name_plural = 'Ответы'


class AbstractLetterAdmin(MPTTModelAdmin):
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
    mptt_level_indent = 0
    list_filter = (InCompletedFilter, ('sign_date', DateRangeFilter))

    def get_queryset(self, request):
        return BaseLetter.objects.filter(type=1).select_related('type', 'counterparty')

    def get_exclude(self, request, obj=None):
        return 'type', 'out_type', 'executor', 'pagemaker_file', 'inbound_number', 'inaction', 'send_date',


@admin.register(OmittedRedirect)
class OmittedRedirectAdmin(AbstractLetterAdmin):
    mptt_level_indent = 0
    list_filter = (InCompletedFilter, ('sign_date', DateRangeFilter))

    def get_queryset(self, request):
        return BaseLetter.objects.filter(type=3).select_related('type', 'counterparty')

    def get_exclude(self, request, obj=None):
        return 'type', 'out_type', 'subj', 'sign_date', 'way_of_delivery', 'executor', 'inbound_number', 'outgoing_number', 'signed_by', 'contact', 'receive_date', 'send_date', 'thematics', 'geotag', 'cad_num', 'forestry', 'waterobj', 'cipher', 'tiff_file', 'pdf_file', 'pagemaker_file', 'completed', 'inaction',

