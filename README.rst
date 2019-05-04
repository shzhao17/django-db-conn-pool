Gevent-Friendly Database Connection Pooling in Django
=====================================================

Thanks to SQLAlchemy, we can pool the database connections while using the Gevent's monkey patching.

It supports MySQL and has been tested under Python 2.7, Django 1.11, Gevent 1.2, and SQLAlchemy 1.2.

Besides, ``DjangoQueuePool`` is a new queue pool extending the SQLAlchemy's ``QueuePool``:

- Reuse the database connections overflowed by burst traffic;
- Retire the unused database connections gradually over time.

Please remember to close the unusable or obsolete database connections:

- The closed connections are returned to the pool;
- It is recommended to close them once a task is done.
- It is recommended to set ``CONN_MAX_AGE`` as ``0`` if possible;
- The connections would always be obsolete if ``CONN_MAX_AGE`` is ``0``.

.. code-block:: python

    from django.db import connections

    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


Getting Started
---------------

- Install the database connection pool

.. code-block::

    pip install django-db-conn-pool

- Add the pool to the Django database backend

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django_db_conn_pool.mysqlalchemy',
            'CONN_MAX_AGE': 0,
            'POOL': db_conn_pool,
            ...
        }
    }

- Select and tune the connection pool parameters

.. code-block:: python

    from sqlalchemy.pool import QueuePool
    from django_db_conn_pool.mysqlalchemy.pool import DjangoQueuePool


    db_conn_pool = slow_and_safe = {

        'django_pool_class': QueuePool,         # sqlalchemy's builtin queue pool class
        'django_pre_ping': True,                # pre ping by django if dialect is None
        'django_reset_on_return': False,        # use sqlalchemy's reset on conn return

        'pool_size': 5,                         # daily traffic: reuse long connections
        'max_overflow': 0,                      # burst traffic: do not overload the db
        'timeout': 30,                          # burst traffic: > external api timeout
        'recycle': 120,                         # should be smaller than mysql timeout
        'dialect': None,                        # sqlalchemy's mysql dialect instance
        'pre_ping': False,                      # sqlalchemy pre ping requires dialect
        'use_threadlocal': True,                # every thread always get its same conn
        'reset_on_return': 'rollback',          # reset on every conn return by rollback
    }

    db_conn_pool = fast_and_sane = {

        'django_pool_class': QueuePool,         # sqlalchemy's builtin queue pool class
        'django_pre_ping': False,               # no pre ping due to long mysql timeout
        'django_reset_on_return': True,         # reset by rollback only when necessary

        'pool_size': 5,                         # daily traffic: reuse long connections
        'max_overflow': 10,                     # burst traffic: do not overload the db
        'timeout': 30,                          # burst traffic: > external api timeout
        'recycle': 3600,                        # to be much smaller than mysql timeout
        'dialect': None,                        # sqlalchemy's mysql dialect instance
        'pre_ping': False,                      # sqlalchemy pre ping requires dialect
        'use_threadlocal': False,               # diff threads share the db connections
        'reset_on_return': None,                # do not use sqlalchemy reset on return
    }

    db_conn_pool = fast_and_wild = {

        'django_pool_class': DjangoQueuePool,   # customized from sqlalchemy queue pool
        'django_pre_ping': False,               # no pre ping due to long mysql timeout
        'django_reset_on_return': True,         # reset by rollback only when necessary
        'django_core_pool_size': 5,             # retire no conn if achieving core size
        'django_unload_timeout': 2,             # wait some random time before overload
        'django_retire_interval': 5,            # retire few non-core conn per interval
        'django_retire_quantity': 1,            # retire few non-core conn per interval

        'pool_size': 30,                        # daily traffic: recycle or retire conn
        'max_overflow': 0,                      # burst traffic: put overflow into pool
        'timeout': 30,                          # burst traffic: > external api timeout
        'recycle': 3600,                        # to be much smaller than mysql timeout
        'dialect': None,                        # sqlalchemy's mysql dialect instance
        'pre_ping': False,                      # sqlalchemy pre ping requires dialect
        'use_threadlocal': False,               # diff threads share the db connections
        'reset_on_return': None,                # do not use sqlalchemy reset on return
    }
