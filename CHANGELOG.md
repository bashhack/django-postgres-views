# Changelog

## 0.0.4

- Prevent writing views to `test` schema if multi-tenant `schema_name` set on `connection`


## 0.0.3

- Prevent writing views to `public` schema if multi-tenant `schema_name` set on `connection`

## 0.0.2

- Add support for multi-tenancy (i.e, django-tenant-schemas, django-tenant, etc.)

## 0.0.1

- Port of [django-pgviews](https://github.com/mypebble/django-pgviews)
- Additional setup/build tooling
