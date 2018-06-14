from middlewared.schema import Any, Str, accepts, Datetime
from middlewared.service import Service, private
from datetime import datetime, timezone


class CacheService(Service):

    class Config:
        private = True

    def __init__(self, *args, **kwargs):
        super(CacheService, self).__init__(*args, **kwargs)
        self.__cache = {}

    @accepts(Str('key'))
    def has_key(self, key):
        """
        Check if given `key` is in cache.
        """
        return key in self.__cache

    @accepts(Str('key'))
    def get(self, key):
        """
        Get `key` from cache.

        Raises:
            KeyError: not found in the cache
        """
        if isinstance(self.__cache[key][-1], datetime):
            self.get_timeout(key)
            return self.__cache[key][0]

        return self.__cache[key]

    @accepts(Str('key'), Any('value'), Datetime('timeout', required=False))
    def put(self, key, value, timeout):
        """
        Put `key` of `value` in the cache.
        """
        if timeout is not None:
            self.__cache[key] = [value, timeout]
        else:
            self.__cache[key] = value

    @accepts(Str('key'))
    def pop(self, key):
        """
        Removes and returns `key` from cache.
        """
        return self.__cache.pop(key, None)

    @private
    def get_timeout(self, key):
        now = datetime.now(timezone.utc)
        value, timeout = self.__cache[key]

        if now >= timeout:
            # Bust the cache
            del self.__cache[key]

            raise KeyError(f'Key has expired at {timeout.ctime()}')
