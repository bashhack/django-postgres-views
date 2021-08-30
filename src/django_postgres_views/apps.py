import logging

from .settings import PGVIEW_SYNC_VIEW_PATH

from django import apps
from django.db.models import signals
from django.utils.module_loading import import_string

logger = logging.getLogger('django_postgres_views.sync_postgres_views')


class ViewSyncLauncher(object):
    counter = 0

    @classmethod
    def sync_postgres_views(cls, sender, app_config, **kwargs):
        """Forcibly sync the views.
        """
        cls.counter = cls.counter + 1
        total = len([a for a in apps.apps.get_app_configs() if a.models_module is not None])

        if cls.counter == total:
            logger.info('All applications have migrated, time to sync')
            # Import here otherwise Django doesn't start properly
            # (models in app init are not allowed)
            from .models import ViewSyncer
            vs = ViewSyncer()
            vs.run(force=True, update=True)

sync_postgres_views = ViewSyncLauncher.sync_postgres_views


class ViewConfig(apps.AppConfig):
    """The base configuration for Django Postgres Views.
    We use this to setup our post_migrate signal handlers.
    """
    name = 'django_postgres_views'
    verbose_name = 'Django Postgres Views'

    def ready(self):
        """Find and setup the apps to set the post_migrate hooks for.
        """
        sync_postgres_views = import_string(PGVIEW_SYNC_VIEW_PATH)
        signals.post_migrate.connect(sync_postgres_views)
