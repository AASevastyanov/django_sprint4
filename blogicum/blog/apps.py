from django.apps import AppConfig
from django.db.utils import ProgrammingError, OperationalError, IntegrityError

class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = 'Блог'
    def ready(self):
        try:
            from .models import Category
            if not Category.objects.exists():
                Category.objects.get_or_create(
                    slug='zzz-default',
                    defaults={
                        'title': 'zzz Default',
                        'description': 'Default category',
                        'is_published': True,
                    }
                )
        except (ProgrammingError, OperationalError, IntegrityError):
            pass
