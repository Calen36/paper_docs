from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from .admin_cats import AbstractInline, AbsMultiCatAdmin
from .models import *


@admin.register(CounterpartyType)
class CounterpartyTypeAdmin(admin.ModelAdmin):
    pass


class PositionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PositionInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline


class PositionInline(AbstractInline):
    model = Position
    verbose_name_plural = 'Должностные позиции в данной организации'


class PersonInline(AbstractInline):
    model = Person
    verbose_name_plural = 'Лица, занимавшие данную позицию'
    # fields = ('name',)


class OrganizationInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(OrganizationInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline


@admin.register(Counterparty)
class CounterpartyAdmin(AbsMultiCatAdmin):
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
