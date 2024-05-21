from integrations.util.cache import Cache
from decouple import config
import requests


class Sim:
    method = ""

    def __init__(self, data) -> None:
        self.data = data

    def value(self, unit, sub_unit, variable, period):
        """
        Calculate variable at the period
        """
        raise NotImplementedError

    def members(self, unit, sub_unit):
        """
        Return a list of the members in the sub unit
        """
        raise NotImplementedError


class ApiSim(Sim):
    method_name = "Policy Engine API"
    pe_url = "https://api.policyengine.org/us/calculate"

    def __init__(self, data) -> None:
        response = requests.post(self.pe_url, json=data)
        self.data = response.json()["result"]

    def value(self, unit, sub_unit, variable, period):
        return self.data[unit][sub_unit][variable][period]

    def members(self, unit, sub_unit):
        return self.data[unit][sub_unit]["members"]


class PolicyEngineBearerTokenCache(Cache):
    expire_time = 60 * 60 * 24 * 29
    default = ""
    client_id: str = config("POLICY_ENGINE_CLIENT_ID", "")
    client_secret: str = config("POLICY_ENGINE_CLIENT_SECRET", "")
    domain = "https://policyengine.uk.auth0.com"
    endpoint = "/oauth/token"

    def update(self):
        # https://policyengine.org/us/api#fetch_token

        if self.client_id == "" or self.client_secret == "":
            raise Exception("client id or secret not configured")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "audience": "https://household.api.policyengine.org",
        }

        res = requests.post(self.domain + self.endpoint, json=payload)

        return res.json()["access_token"]


class PrivateApiSim(ApiSim):
    method_name = "Private Policy Engine API"
    token = PolicyEngineBearerTokenCache()
    pe_url = "https://household.api.policyengine.org/us/calculate"

    def __init__(self, data) -> None:
        token = self.token.fetch()

        headers = {
            "Authorization": f"Bearer {token}",
        }

        res = requests.post(self.pe_url, json=data, headers=headers)

        self.data = res.json()["result"]


# NOTE: Code to run Policy Engine locally. This is currently too CPU expensive to run in production.
# Requires the Policy Engine package to be installed and imported.
#
# class LocalSim(Sim):
#     method_name = 'local package'
#
#     def __init__(self, data) -> None:
#         self.household = data['household']
#
#         self.entity_map = {}
#         for entity in self.household.keys():
#             group_map = {}
#
#             for i, group in enumerate(self.household[entity].keys()):
#                 group_map[group] = i
#
#             self.entity_map[entity] = group_map
#
#         self.sim = Simulation(situation=self.household)
#
#     def value(self, unit, sub_unit, variable, period):
#         data = self.sim.calculate(variable, period)
#
#         index = self.entity_map[unit][sub_unit]
#
#         return data[index]
#
#     def members(self, unit, sub_unit):
#         return self.household[unit][sub_unit]['members']


pe_engines = [PrivateApiSim, ApiSim]
