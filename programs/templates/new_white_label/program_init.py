from .example_program.calculator import ExampleCalculator
from ..calc import ProgramCalculator

# TODO: add "**{{code}}_calculators," to /programs/programs/__init__.py
{{code}}_calculators: dict[str, type[ProgramCalculator]] = {  # TODO: add state specific calculators
    "{{code}}_example_calculator": ExampleCalculator,
}
