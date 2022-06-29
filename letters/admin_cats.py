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
    model = GeoTag


@admin.register(GeoTag)
class GeoTagAdmin(AbsMultiCatAdmin):
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
    model = Thematics
    verbose_name_plural = 'Подтемы'


@admin.register(Thematics)
class ThematicsAdmin(AbsMultiCatAdmin):
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
    model = Forestry


@admin.register(Forestry)
class ForestryAdmin(AbsMultiCatAdmin):
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
    model = WaterObj


@admin.register(WaterObj)
class WaterObjAdmin(AbsMultiCatAdmin):
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
    search_fields = ('surname', 'name', 'patronimic')
    # inlines = (ExecutorLettersInline,)
    list_per_page = 50

    def get_actions(self, request):
        return []


@admin.register(LetterType)
class LetterTypeAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        return []


@admin.register(OutgoingType)
class OutgoingTypeAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        return []


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }


