from rest_framework import serializers
from modeltranslation.translator import translator
from core.middleware import get_requested_lang


def make_absolute_url(url, request):
    """Returns an absolute URL for media and image paths."""
    if not url:
        return None
    if hasattr(url, 'url'):
        try:
            url = url.url
        except Exception:
            return None
    url_str = str(url)
    if not url_str:
        return None
    if url_str.startswith(('http://', 'https://')):
        return url_str
    if not url_str.startswith('/'):
        url_str = f"/media/{url_str}"
    if request:
        try:
            return request.build_absolute_uri(url_str)
        except Exception:
            pass
    return f"http://127.0.0.1:8001{url_str}"


def get_bilingual_or_localized(instance, field_name, lang=None):
    """
    Returns either a localized string (when lang is specified)
    or a bilingual dictionary {'en': ..., 'ne': ...}.
    """
    en_val = getattr(instance, f"{field_name}_en", "") or getattr(instance, field_name, "") or ""
    ne_val = getattr(instance, f"{field_name}_ne", "") or ""
    
    if not en_val and not ne_val:
        base_val = getattr(instance, field_name, "")
        if isinstance(base_val, str):
            en_val = base_val
        elif isinstance(base_val, dict):
            en_val = base_val.get('en', '')
            ne_val = base_val.get('ne', '')

    if lang == 'ne':
        return ne_val or en_val
    elif lang == 'en':
        return en_val or ne_val
    else:
        return {'en': en_val, 'ne': ne_val}


class TranslatedAdminSerializerMixin:
    """
    Reusable serializer mixin that:
    1. Returns a single resolved value (e.g. name, description) for public requests using active language.
    2. ONLY when ?lang=all AND request.user.is_staff: includes _en and _ne fields for translatable fields.
    3. If ?lang=all is requested by non-staff/anonymous, ignores it and returns single-language shape.
    4. Write endpoints (create/update) for staff accept _en and _ne fields.
    5. Detail responses include 'lang' ('en'|'ne') and 'translation_missing' (boolean).
    6. Ensures image/media URLs are returned as absolute URLs.
    """

    def get_fields(self):
        fields = super().get_fields()
        model = getattr(getattr(self, 'Meta', None), 'model', None)
        if not model:
            return fields

        try:
            opts = translator.get_options_for_model(model)
        except Exception:
            opts = None

        if opts:
            for tf in opts.fields:
                for lang_code in ('en', 'ne'):
                    fname = f"{tf}_{lang_code}"
                    if fname not in fields:
                        # Register as write_only so default to_representation won't expose it
                        fields[fname] = serializers.CharField(
                            required=False,
                            allow_blank=True,
                            allow_null=True,
                            write_only=True
                        )
        return fields

    def to_internal_value(self, data):
        request = self.context.get('request')
        is_staff = bool(
            request and getattr(request, 'user', None) and
            request.user.is_authenticated and request.user.is_staff
        )

        # If user is not staff, strip any _en or _ne translation fields from input
        if not is_staff and request is not None and isinstance(data, dict):
            model = getattr(getattr(self, 'Meta', None), 'model', None)
            if model:
                try:
                    opts = translator.get_options_for_model(model)
                except Exception:
                    opts = None
                if opts:
                    data = data.copy()
                    for tf in opts.fields:
                        for lang_code in ('en', 'ne'):
                            data.pop(f"{tf}_{lang_code}", None)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        is_staff = bool(
            request and getattr(request, 'user', None) and
            request.user.is_authenticated and request.user.is_staff
        )
        lang_all = bool(
            request and (
                getattr(request, 'lang_all', False) or
                (hasattr(request, 'query_params') and request.query_params.get('lang') == 'all') or
                (hasattr(request, 'GET') and request.GET.get('lang') == 'all')
            )
        )

        model = getattr(getattr(self, 'Meta', None), 'model', None)
        try:
            opts = translator.get_options_for_model(model) if model else None
        except Exception:
            opts = None

        # 1. Staff + ?lang=all gets explicit _en and _ne fields
        if is_staff and lang_all and opts:
            for tf in opts.fields:
                for lang_code in ('en', 'ne'):
                    fname = f"{tf}_{lang_code}"
                    if hasattr(instance, fname):
                        ret[fname] = getattr(instance, fname)

        # 2. Check if this is a top-level detail response
        is_detail = bool(
            self.context.get('is_detail') or
            (self.context.get('view') and getattr(self.context['view'], 'action', None) == 'retrieve') or
            (self.parent is None and not getattr(self, 'many', False))
        )

        if is_detail:
            if request:
                req_lang = get_requested_lang(request)
            else:
                from django.utils import translation
                req_lang = translation.get_language() or 'en'

            if req_lang == 'ne':
                # Check whether the primary text fields have a real Nepali translation
                has_ne = False
                for field_name in ('title_ne', 'name_ne', 'text_ne'):
                    if hasattr(instance, field_name):
                        val = getattr(instance, field_name)
                        if val and str(val).strip():
                            has_ne = True
                            break
                if has_ne:
                    ret['lang'] = 'ne'
                    ret['translation_missing'] = False
                else:
                    ret['lang'] = 'en'
                    ret['translation_missing'] = True
            else:
                ret['lang'] = 'en'
                ret['translation_missing'] = False

            # Fill SEO fields fallback if needed
            if hasattr(instance, 'meta_title'):
                ret['meta_title'] = (
                    getattr(instance, 'meta_title', '') or
                    getattr(instance, 'title', '') or
                    getattr(instance, 'name', '') or ''
                )
            if hasattr(instance, 'meta_description'):
                ret['meta_description'] = (
                    getattr(instance, 'meta_description', '') or
                    getattr(instance, 'excerpt', '') or
                    getattr(instance, 'description', '') or ''
                )

            # Detail og_image
            img_val = getattr(instance, 'featuredImage', None) or getattr(instance, 'heroImage', None)
            if img_val:
                ret['og_image'] = make_absolute_url(img_val, request)

        # Convert image fields to absolute URLs
        for img_field in ('featuredImage', 'heroImage', 'avatar', 'coverImage', 'thumbnail', 'image', 'og_image'):
            if img_field in ret and ret[img_field]:
                ret[img_field] = make_absolute_url(ret[img_field], request)

        return ret
