#!/usr/bin/env python

from codecs import open

from setuptools import setup

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='django-db-conn-pool',
    version='1.0.0',
    description='Gevent-Friendly Database Connection Pooling in Django',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author='Patrick Zhao',
    url='https://github.com/shzhao17/django-db-conn-pool',
    packages=['django_db_conn_pool', 'django_db_conn_pool.mysqlalchemy'],
    package_data={'': ['LICENSE', 'NOTICE']},
    include_package_data=True,
    python_requires='>=2.7,<3',
    install_requires=['six', 'typing', 'django', 'sqlalchemy'],
    license='Apache 2.0',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    tests_require=[],
    extras_require={},
)
