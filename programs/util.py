class Dependencies(set):
    def has(self, *iter):
        for dependency in iter:
            if dependency in self:
                return True

        return False


class DependencyError(Exception):
    def __init__(self):
        super().__init__("Missing at least dependency")


class ProgramConfigurationError(Exception):
    """A program's database configuration cannot serve a calculation.

    Distinct from `DependencyError`, which means the *screen* is missing a field the user
    never answered. This one is about *us*: a row is configured in a way its calculator
    cannot work with (today: no `FederalPoveryLimit`, so there is no period to ask
    PolicyEngine about). Typed so the guard reads as the programmer error it is rather than
    as a bare `Exception`, and so a misconfigured program is distinguishable from an
    unexpected failure in Sentry."""
