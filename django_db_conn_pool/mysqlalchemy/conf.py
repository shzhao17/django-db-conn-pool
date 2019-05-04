
import copy

import six
import sqlalchemy.pool

from .pool import DjangoQueuePool


class DjangoPoolParams(object):

    _slow_and_safe = {

        'django_pool_class': sqlalchemy.pool.QueuePool,                     # sqlalchemy's builtin queue pool class
        'django_pre_ping': True,                                            # pre ping by django if dialect is None
        'django_reset_on_return': False,                                    # use sqlalchemy's reset on conn return

        'pool_size': 5,                                                     # daily traffic: reuse long connections
        'max_overflow': 0,                                                  # burst traffic: do not overload the db
        'timeout': 30,                                                      # burst traffic: > external api timeout
        'recycle': 120,                                                     # should be smaller than mysql timeout
        'dialect': None,                                                    # sqlalchemy's mysql dialect instance
        'pre_ping': False,                                                  # sqlalchemy pre ping requires dialect
        'use_threadlocal': True,                                            # every thread always get its same conn
        'reset_on_return': 'rollback',                                      # reset on every conn return by rollback
    }

    _fast_and_sane = {

        'django_pool_class': sqlalchemy.pool.QueuePool,                     # sqlalchemy's builtin queue pool class
        'django_pre_ping': False,                                           # no pre ping due to long mysql timeout
        'django_reset_on_return': True,                                     # reset by rollback only when necessary

        'pool_size': 5,                                                     # daily traffic: reuse long connections
        'max_overflow': 10,                                                 # burst traffic: do not overload the db
        'timeout': 30,                                                      # burst traffic: > external api timeout
        'recycle': 3600,                                                    # to be much smaller than mysql timeout
        'dialect': None,                                                    # sqlalchemy's mysql dialect instance
        'pre_ping': False,                                                  # sqlalchemy pre ping requires dialect
        'use_threadlocal': False,                                           # diff threads share the db connections
        'reset_on_return': None,                                            # do not use sqlalchemy reset on return
    }

    _fast_and_wild = {

        'django_pool_class': DjangoQueuePool,                               # customized from sqlalchemy queue pool
        'django_pre_ping': False,                                           # no pre ping due to long mysql timeout
        'django_reset_on_return': True,                                     # reset by rollback only when necessary
        'django_core_pool_size': 5,                                         # retire no conn if achieving core size
        'django_unload_timeout': 2,                                         # wait some random time before overload
        'django_retire_interval': 5,                                        # retire few non-core conn per interval
        'django_retire_quantity': 1,                                        # retire few non-core conn per interval

        'pool_size': 30,                                                    # daily traffic: recycle or retire conn
        'max_overflow': 0,                                                  # burst traffic: put overflow into pool
        'timeout': 30,                                                      # burst traffic: > external api timeout
        'recycle': 3600,                                                    # to be much smaller than mysql timeout
        'dialect': None,                                                    # sqlalchemy's mysql dialect instance
        'pre_ping': False,                                                  # sqlalchemy pre ping requires dialect
        'use_threadlocal': False,                                           # diff threads share the db connections
        'reset_on_return': None,                                            # do not use sqlalchemy reset on return
    }

    _supported_params = set(six.iterkeys(_fast_and_wild))

    _params_to_kwargs = {
        'django_pool_class': None,
        'django_pre_ping': None,
        'django_reset_on_return': None,
        'django_core_pool_size': 'core_pool_size',
        'django_unload_timeout': 'unload_timeout',
        'django_retire_interval': 'retire_interval',
        'django_retire_quantity': 'retire_quantity',
    }
    if not _supported_params.issuperset(_params_to_kwargs.viewkeys()):
        raise Exception('invalid supported params: %s' % _supported_params)

    def __init__(self, pool_params):
        """
        :type pool_params: dict
        """
        self.pool_params = pool_params

    @classmethod
    def unsupported(cls, params):
        return six.viewkeys(params) - cls._supported_params

    @classmethod
    def new_slow_safe(cls, **updated):
        return cls.new(cls._slow_and_safe, **updated)

    @classmethod
    def new_fast_sane(cls, **updated):
        return cls.new(cls._fast_and_sane, **updated)

    @classmethod
    def new_fast_wild(cls, **updated):
        return cls.new(cls._fast_and_wild, **updated)

    @classmethod
    def new(cls, default, **updated):
        """
        :rtype: dict
        """
        params = dict(default, **updated)
        unsupported = cls.unsupported(params)
        if unsupported:
            raise Exception('unsupported pool params: %s' % unsupported)
        return params

    def get_pool_kwargs(self):
        """
        :rtype: dict
        """
        pool_class = self.django_pool_class
        pool_kwargs = copy.deepcopy(self.pool_params)
        for _k in self._params_to_kwargs:
            pool_kwargs.pop(_k, None)
        if pool_class == DjangoQueuePool:
            for _k, _v in six.iteritems(self._params_to_kwargs):
                if _k is not None and _v is not None:
                    pool_kwargs[_v] = self.pool_params.get(_k, None)
        return pool_kwargs

    @property
    def django_pool_class(self):
        return self.pool_params.get('django_pool_class', None)

    @property
    def django_pre_ping(self):
        return self.pool_params.get('django_pre_ping', None)

    @property
    def django_reset_on_return(self):
        return self.pool_params.get('django_reset_on_return', None)
