from django.utils import translation
from django.conf import settings

SUPPORTED_LANGUAGES = ('en', 'ne')

def get_requested_lang(request) -> str:
    """
    Returns 'en', 'ne', or 'all' based on the ?lang= query param.
    If missing or invalid, defaults to 'en'.
    """
    lang = request.GET.get('lang', '').strip().lower()
    if lang in SUPPORTED_LANGUAGES or lang == 'all':
        return lang
    return 'en'

class LanguageFromQueryMiddleware:
    """
    Activates language based solely on the ?lang= query parameter.
    Does NOT use Accept-Language, cookies, or IP.
    Sets Content-Language on the response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        requested_lang = get_requested_lang(request)
        request.lang_all = (requested_lang == 'all')

        if requested_lang in SUPPORTED_LANGUAGES:
            active_lang = requested_lang
        else:
            active_lang = settings.LANGUAGE_CODE  # 'en'

        translation.activate(active_lang)
        request.LANGUAGE_CODE = active_lang

        try:
            response = self.get_response(request)
        finally:
            translation.deactivate()

        # Content-Language matches the served language (e.g. if detail response fell back to English)
        served_lang = active_lang
        if hasattr(response, 'data') and isinstance(response.data, dict) and 'lang' in response.data:
            served_lang = response.data['lang']

        response.headers['Content-Language'] = served_lang

        # Add caching headers on public read responses if not already explicitly set
        if request.method in ('GET', 'HEAD') and 'Cache-Control' not in response.headers:
            is_staff = bool(getattr(request, 'user', None) and request.user.is_authenticated and request.user.is_staff)
            if is_staff or requested_lang == 'all':
                response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            else:
                response.headers['Cache-Control'] = 'public, max-age=60, s-maxage=300'

        return response
