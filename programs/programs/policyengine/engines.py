from policyengine_us import Simulation
import requests


class Sim:
    method = ''

    def __init__(self, data) -> None:
        self.data = data

    def value(self, unit, sub_unit, variable, period):
        '''
        Calculate variable at the period
        '''
        raise NotImplementedError

    def members(self, unit, sub_unit):
        '''
        Return a list of the members in the sub unit
        '''
        raise NotImplementedError


class ApiSim(Sim):
    method_name = 'Policy Engine api'

    def __init__(self, data) -> None:
        response = requests.post("https://api.policyengine.org/us/calculate", json=data)
        self.data = response.json()['result']

    def value(self, unit, sub_unit, variable, period):
        return self.data[unit][sub_unit][variable][period]

    def members(self, unit, sub_unit):
        return self.data[unit][sub_unit]['members']


class LocalSim(Sim):
    method_name = 'local package'

    def __init__(self, data) -> None:
        self.household = data['household']

        self.entity_map = {}
        for entity in self.household.keys():
            group_map = {}

            for i, group in enumerate(self.household[entity].keys()):
                group_map[group] = i

            self.entity_map[entity] = group_map

        self.sim = Simulation(situation=self.household)

    def value(self, unit, sub_unit, variable, period):
        data = self.sim.calculate(variable, period)

        index = self.entity_map[unit][sub_unit]

        return data[index]

    def members(self, unit, sub_unit):
        return self.household[unit][sub_unit]['members']


pe_engines = [ApiSim, LocalSim]
