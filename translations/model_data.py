from typing import TypedDict, Generic, TypeVar

T = TypeVar("T")


class ModelDataController(Generic[T]):
    _model_name = ""
    dependencies: list[str] = []

    DataType = TypedDict("DataType", {})

    def __init__(self, instance: T):
        self.instance = instance

    @property
    def model_name(self):
        return self._model_name if self._model_name != "" else self.instance.__class__.__name__

    @property
    def external_name(self):
        return self.instance.external_name

    def to_model_data(self) -> DataType:
        return {}

    def from_model_data(self, data: DataType):
        pass

    @classmethod
    def initialize_instance(cls, external_name: str) -> T:
        raise NotImplemented("initialize_instance must be defined")
