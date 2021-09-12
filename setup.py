from os.path import isfile

from setuptools import setup, find_packages

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    if isfile('README.md'):
        LONG_DESCRIPTION = open('README.md').read()
    else:
        LONG_DESCRIPTION = ''

setup(
    name='django-postgres-views',
    version='0.0.3',
    description='Support for PostgreSQL views in Django',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='bashhack',
    author_email='info@marclaughton.com',
    license='Public Domain',
    packages=find_packages(),
    url='https://github.com/bashhack/django-postgres-views',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
    ]
)
