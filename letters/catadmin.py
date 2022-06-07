from django.contrib import admin
from django.forms import Textarea
from mptt.admin import MPTTModelAdmin
from mptt.querysets import TreeQuerySet
from .models import *


class AbsMultiCatAdmin(MPTTModelAdmin):
    autocomplete_fields = ('parent',)
    search_fields = ('name',)
    list_display = ('name',)
    mptt_level_indent = 40

    def get_actions(self, request):
        return []


class AbstractInline(admin.TabularInline):
    fk_name = 'parent'
    extra = 0
    verbose_name_plural = 'Подкатегории'
    show_change_link = True

    def has_add_permission(*args, **kwargs):
        return False

    def has_change_permission(*args, **kwargs):
        return False

    def has_delete_permission(*args, **kwargs):
        return False

    class Meta:
        abstract = True





class GeoInline(AbstractInline):
    model = GeoTag


class GeoLettersInline(AbstractInline):
    model = BaseLetter.geotag.through
    fk_name = 'geotag'
    verbose_name_plural = 'Письма, относящиеся к данной локации'


@admin.register(GeoTag)
class GeoTagAdmin(AbsMultiCatAdmin):
    inlines = (GeoInline, GeoLettersInline)


class ThematicsInline(AbstractInline):
    model = Thematics


class ThematicsLettersInline(AbstractInline):
    model = BaseLetter.thematics.through
    fk_name = 'thematics'
    verbose_name_plural = 'Письма по данной тематике'


@admin.register(Thematics)
class ThematicsAdmin(AbsMultiCatAdmin):
    inlines = (ThematicsInline, ThematicsLettersInline)


class ForestryInline(AbstractInline):
    model = Forestry


class ForestryLettersInline(AbstractInline):
    model = BaseLetter.forestry.through
    fk_name = 'forestry'
    verbose_name_plural = 'Письма, относящиеся к данному объекту'


@admin.register(Forestry)
class ForestryAdmin(AbsMultiCatAdmin):
    inlines = (ForestryInline, ForestryLettersInline)


class WaterObjInline(AbstractInline):
    model = WaterObj


class WaterObjLettersInline(AbstractInline):
    model = BaseLetter.waterobj.through
    fk_name = 'waterobj'
    verbose_name_plural = 'Письма, относящиеся к данному объекту'


@admin.register(WaterObj)
class WaterObjAdmin(AbsMultiCatAdmin):
    inlines = (WaterObjInline, WaterObjLettersInline)


class CounterpartyInline(AbstractInline):
    model = Counterparty


class CounterpartyObjLettersInline(AbstractInline):
    model = BaseLetter
    fk_name = 'counterparty'
    verbose_name_plural = 'Переписка с данным контрагентом'
    fields = ('number', 'sign_date', 'subj', )


@admin.register(Counterparty)
class CounterpartyAdmin(AbsMultiCatAdmin):
    inlines = (CounterpartyInline, CounterpartyObjLettersInline)


class CadNumLettersInline(AbstractInline):
    model = BaseLetter.cad_num.through
    fk_name = None
    verbose_name_plural = 'Письма, относящиеся к данному участку'



@admin.register(CadNum)
class CadNumAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = (CadNumLettersInline,)

    def get_actions(self, request):
        return []


class WayOfDeliveryLettersInline(AbstractInline):
    model = BaseLetter
    fk_name = None
    verbose_name_plural = 'Письма, доставленные выбранным способом'
    fields = ('number', 'sign_date', 'counterparty', 'subj')


@admin.register(WayOfDelivery)
class WayOfDeliveryAdmin(admin.ModelAdmin):
    inlines = (WayOfDeliveryLettersInline,)

    def get_actions(self, request):
        return []


class ExecutorLettersInline(AbstractInline):
    model = BaseLetter.executor.through
    fk_name = None
    verbose_name_plural = 'Письма, подписанные выбранным исполнителем'


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    search_fields = ('surname', 'name', 'patronimic')
    inlines = (ExecutorLettersInline,)
    list_per_page = 50

    def get_actions(self, request):
        return []


@admin.register(LetterType)
class LetterTypeAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        return []


# @admin.register(Attachment)
# class AttachmentAdmin(admin.ModelAdmin):
#     pass


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }
