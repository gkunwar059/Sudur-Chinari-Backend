from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

class BaseTranslatedAdmin(TranslationAdmin):
    """
    Base TranslationAdmin that:
    - Sets English and Nepali translation support.
    - Makes _en fields required (if base field not blank).
    - Makes _ne fields optional.
    - Provides a translation_complete column for list views.
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if field_name.endswith('_en'):
                base_name = field_name[:-3]
                try:
                    base_field = self.model._meta.get_field(base_name)
                    if not getattr(base_field, 'blank', False):
                        field.required = True
                    verbose = base_field.verbose_name.title()
                    field.label = f"{verbose} (English)"
                except Exception:
                    pass
            elif field_name.endswith('_ne'):
                field.required = False
                base_name = field_name[:-3]
                try:
                    base_field = self.model._meta.get_field(base_name)
                    verbose = base_field.verbose_name.title()
                    field.label = f"{verbose} (नेपाली)"
                except Exception:
                    pass
        return form

    @admin.display(description="Nepali Translated", boolean=True)
    def translation_complete(self, obj):
        for attr in ('title_ne', 'name_ne', 'text_ne'):
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                return bool(val and str(val).strip())
        return False
