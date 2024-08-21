from programs.admin import FederalPovertyLimitAdmin


class PolicyEngineBearerTokenCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}


    def update(self):
        fpls = FederalPovertyLimitAdmin.objects().all
