from django.apps import AppConfig

class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.articles'
    label = 'articles'
    verbose_name = 'Articles & Editorial'

    def ready(self):
        import apps.articles.signals  # noqa: F401
