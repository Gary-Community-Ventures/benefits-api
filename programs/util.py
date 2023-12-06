class Dependencies(set):
    def has(self, *iter):
        for dependency in iter:
            if dependency in self:
                return True

        return False
