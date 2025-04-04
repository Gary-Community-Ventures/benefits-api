from .example_program.calculator import ExampleCalculator
from ..calc import ProgramCalculator

# TODO: add "**ma_calculators," to /programs/programs/__init__.py
ma_calculators: dict[str, type[ProgramCalculator]] = {  # TODO: add state specific calculators
    "ma_example_calculator": ExampleCalculator,
}
