from programs.programs.co.weatherization_assistance.calculator import WeatherizationAssistance


class EnergyCalculatorWeatherizationAssistance(WeatherizationAssistance):
    dependencies = [*WeatherizationAssistance.dependencies, "energy_calculator"]
    electric_providers = [
        "co-xcel-energy",
        "co-black-hills-energy",
        "co-holy-cross-energy",
    ]
    gas_providers = [
        "co-xcel-energy",
        "co-atmos-energy",
        "co-colorado-natural-gas",
        "co-black-hills-energy",
    ]

    def _has_expenses(self):
        return True

    def _has_utility_provider(self):
        return self.screen.energy_calculator.has_utility_provider(self.electric_providers + self.gas_providers)
