class Dependencies(set):
    def has(self, *iter):
        for dependency in iter:
            if dependency in self:
                return True

        return False


class DependencyError(Exception):
    def __init__(self):
        super().__init__("Missing at least dependency")
