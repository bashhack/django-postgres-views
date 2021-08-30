# SQL Views for Postgres

[![Circle CI](https://circleci.com/gh/bashhack/django-postgres-views.png)](https://circleci.com/gh/bashhack/django-postgres-views)

Adds first-class support for [PostgreSQL Views](https://www.postgresql.org/docs/9.1/sql-createview.html) in the Django ORM

[pg-views]: http://www.postgresql.org/docs/9.1/static/sql-createview.html


## Installation

Install via pip:

    pip install django-postgres-views

Add to installed applications in settings.py:

```python
INSTALLED_APPS = (
  # ...
  'django_postgres_views',
)
```

## Examples

```python
from django.db import models

from django_postgres_views import view as pg


class Customer(models.Model):
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        app_label = 'myapp'

class PreferredCustomer(pg.View):
    projection = ['myapp.Customer.*',]
    dependencies = ['myapp.OtherView',]
    sql = """SELECT * FROM myapp_customer WHERE is_preferred = TRUE;"""

    class Meta:
      app_label = 'myapp'
      db_table = 'myapp_preferredcustomer'
      managed = False
```

**NOTE** It is important that we include the `managed = False` in the `Meta` so
Django 1.7 migrations don't attempt to create DB tables for this view.

The SQL produced by this might look like:

```postgresql
CREATE VIEW myapp_preferredcustomer AS
SELECT * FROM myapp_customer WHERE is_preferred = TRUE;
```

To create all your views, run ``python manage.py sync_postgres_views``

You can also specify field names, which will map onto fields in your View:

```python
from django_postgres_views import view as pg


VIEW_SQL = """
    SELECT name, post_code FROM myapp_customer WHERE is_preferred = TRUE
"""


class PreferredCustomer(pg.View):
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)

    sql = VIEW_SQL
```

## Usage

To map onto a View, simply extend `pg_views.view.View`, assign SQL to the
`sql` argument and define a `db_table`. You must _always_ set `managed = False`
on the `Meta` class.

Views can be created in a number of ways:

1. Define fields to map onto the VIEW output
2. Define a projection that describes the VIEW fields

### Define Fields

Define the fields as you would with any Django Model:

```python
from django_postgres_views import view as pg


VIEW_SQL = """
    SELECT name, post_code FROM myapp_customer WHERE is_preferred = TRUE
"""


class PreferredCustomer(pg.View):
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)

    sql = VIEW_SQL

    class Meta:
      managed = False
      db_table = 'my_sql_view'
```

### Define Projection

`django-postgres-views` can take a projection to figure out what fields it needs to
map onto for a view. To use this, set the `projection` attribute:

```python
from django_postgres_views import view as pg


class PreferredCustomer(pg.View):
    projection = ['myapp.Customer.*',]
    sql = """SELECT * FROM myapp_customer WHERE is_preferred = TRUE;"""

    class Meta:
      db_table = 'my_sql_view'
      managed = False
```

This will take all fields on `myapp.Customer` and apply them to
`PreferredCustomer`

## Features

### Updating Views

Sometimes your models change and you need your Database Views to reflect the new
data. Updating the View logic is as simple as modifying the underlying SQL and
running:

```
python manage.py sync_postgres_views --force
```

This will forcibly update any views that conflict with your new SQL.

### Migrations

When running migrations, we will automatically sync your new views using a
`postmigration` signal, if at any moment you want to override this functionality
you can supplement your own by adding the full path to `PGVIEW_SYNC_VIEW_PATH`
with your own migration command.

### Dependencies

You can specify other views you depend on. This ensures the other views are
installed beforehand. Using dependencies also ensures that your views get
refreshed correctly when using `sync_postgres_views --force`.

**Note:** Views are synced after the Django application has migrated and adding
models to the dependency list will cause syncing to fail.

Example:

```python
from django_postgres_views import view as pg

class PreferredCustomer(pg.View):
    dependencies = ['myapp.OtherView',]
    sql = """SELECT * FROM myapp_customer WHERE is_preferred = TRUE;"""

    class Meta:
      app_label = 'myapp'
      db_table = 'myapp_preferredcustomer'
      managed = False
```

### Materialized Views

Postgres 9.3 and up supports [materialized views](http://www.postgresql.org/docs/current/static/sql-creatematerializedview.html)
which allow you to cache the results of views, potentially allowing them
to load faster.

However, you do need to manually refresh the view. To do this automatically,
you can attach [signals](https://docs.djangoproject.com/en/1.8/ref/signals/)
and call the refresh function.

Example:

```python
from django_postgres_views import view as pg


VIEW_SQL = """
    SELECT name, post_code FROM myapp_customer WHERE is_preferred = TRUE
"""

class Customer(models.Model):
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)
    is_preferred = models.BooleanField(default=True)


class PreferredCustomer(pg.MaterializedView):
    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)

    sql = VIEW_SQL


@receiver(post_save, sender=Customer)
def customer_saved(sender, action=None, instance=None, **kwargs):
    PreferredCustomer.refresh()
```

Postgres 9.4 and up allow materialized views to be refreshed concurrently, without blocking reads, as long as a
unique index exists on the materialized view. To enable concurrent refresh, specify the name of a column that can be
used as a unique index on the materialized view. Unique index can be defined on more than one column of a materialized
view. Once enabled, passing `concurrently=True` to the model's refresh method will result in postgres performing the
refresh concurrently. (Note that the refresh method itself blocks until the refresh is complete; concurrent refresh is
most useful when materialized views are updated in another process or thread.)

Example:

```python
from django_postgres_views import view as pg


VIEW_SQL = """
    SELECT id, name, post_code FROM myapp_customer WHERE is_preferred = TRUE
"""

class PreferredCustomer(pg.MaterializedView):
    concurrent_index = 'id, post_code'
    sql = VIEW_SQL

    name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)


@receiver(post_save, sender=Customer)
def customer_saved(sender, action=None, instance=None, **kwargs):
    PreferredCustomer.refresh(concurrently=True)
```

### Custom Schema

You can define any table name you wish for your views. They can even live inside your own custom
[PostgreSQL schema](http://www.postgresql.org/docs/current/static/ddl-schemas.html).

```python
from django_postgres_views import view as pg


class PreferredCustomer(pg.View):
    sql = """SELECT * FROM myapp_customer WHERE is_preferred = TRUE;"""

    class Meta:
      db_table = 'my_custom_schema.preferredcustomer'
      managed = False
```

### Sync Listeners

django-postgres-views 0.0.1 adds the ability to listen to when a `post_sync` event has
occurred.

#### `view_synced`

Fired every time a VIEW is synchronised with the database.

Provides args:
* `sender` - View Class
* `update` - Whether the view to be updated
* `force` - Whether `force` was passed
* `status` - The result of creating the view e.g. `EXISTS`, `FORCE_REQUIRED`
* `has_changed` - Whether the view had to change

#### `all_views_synced`

Sent after all Postgres VIEWs are synchronised.

Provides args:
* `sender` - Always `None`