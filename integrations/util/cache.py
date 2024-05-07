from sentry_sdk import capture_message
import datetime


class Cache:
    expire_time = 0
    default = 0

    def __init__(self):
        self.data = self.default
        self.last_update = datetime.datetime.now() - datetime.timedelta(seconds=self.expire_time)

    def update(self):
        raise NotImplementedError()

    def _update_cache(self):
        try:
            self.data = self.update()
            self.last_update = datetime.datetime.now()
        except Exception:
            capture_message(f"Failed to update {self.__class__.__name__}", level="warning")

    def should_update(self):
        return datetime.datetime.now() > self.last_update + datetime.timedelta(seconds=self.expire_time)

    def fetch(self):
        if self.should_update():
            self._update_cache()

        return self.data
