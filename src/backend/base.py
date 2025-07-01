from abc import ABC, abstractmethod

class Backend(ABC):
    @abstractmethod
    def load_model(self, model_path: str):
        pass

    @abstractmethod
    def infer(self, input_data):
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
