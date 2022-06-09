from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from .admin_cats import AbstractInline, AbsMultiCatAdmin
from .models import *


@admin.register(CounterpartyType)
class CounterpartyTypeAdmin(admin.ModelAdmin):
    pass


class CounterpartyInline(AbstractInline):
    model = Counterparty


class PositionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(PositionInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline
        print()
        print("\t\t\t\t\t!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(args)
        print(kwargs)
        print()


class PositionInline(AbstractInline):
    model = Position
    # formset = PositionInlineFormSet
    verbose_name_plural = 'Должностные позиции'
    fields = ('name',)


class PersonInline(AbstractInline):
    model = Person


class OrganizationInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(OrganizationInlineFormSet, self).__init__(*args, **kwargs)        # Now we need to make a queryset to each field of each form inline
        print()
        print("\t\t\t\t\t!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(args)
        print(kwargs)
        print()


class CounterpartyObjLettersInline(AbstractInline):
    model = BaseLetter
    formset = OrganizationInlineFormSet
    fk_name = 'counterparty'
    verbose_name_plural = 'Переписка с данным контрагентом'
    fields = ('number', 'sign_date', 'subj', )


@admin.register(Counterparty)
class CounterpartyAdmin(AbsMultiCatAdmin):
    list_display = ('get_fancy_name',)
    save_on_top = True

    inlines = (CounterpartyInline, CounterpartyObjLettersInline,)

    def has_add_permission(self, request):
        return False


@admin.register(Organization)
class OrganizationAdmin(AbsMultiCatAdmin):
    list_display = ('get_fancy_name',)
    inlines = (PositionInline, CounterpartyObjLettersInline)
    autocomplete_fields = ('parent', 'prev_org')

    def get_queryset(self, request):
        return Counterparty.objects.filter(type=1)

    def get_exclude(self, request, obj=None):
        return 'type', 'parent', 'prev_pos'


@admin.register(Position)
class PositionAdmin(AbsMultiCatAdmin):
    list_display = ('get_full_name',)
    inlines = (PersonInline, CounterpartyObjLettersInline)
    mptt_level_indent = 0

    def get_queryset(self, request):
        return Position.objects.filter(type=2)

    def get_exclude(self, request, obj=None):
        return 'type', 'prev_pos', 'prev_org'


@admin.register(Person)
class PersonAdmin(AbsMultiCatAdmin):
    list_display = ('get_full_name',)
    search_fields = ('name', 'parent__name', 'parent__parent__name')
    inlines = (CounterpartyInline, CounterpartyObjLettersInline)
    autocomplete_fields = ('parent', 'prev_pos')
    mptt_level_indent = 0

    def get_queryset(self, request):
        return Person.objects.filter(type=3)

    def get_exclude(self, request, obj=None):
        return 'type', 'prev_org'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].verbose_name = "my verbose name"
        return form