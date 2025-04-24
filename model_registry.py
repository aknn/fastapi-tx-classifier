from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Type
from models import TransactionCategory

# --- Model Interface Definition ---


class ModelInterface(ABC):
    @abstractmethod
    async def classify(self, text: str, amount: float) -> Tuple[TransactionCategory, float, str]:
        """
        Classify a transaction description and amount.
        Returns a tuple of (category, confidence, hit_type).
        """
        pass


# --- Model Registry ---
_model_registry: Dict[str, ModelInterface] = {}


def register_model(name: str):
    """
    Decorator to register a model class under a given name.
    Instantiates and stores the model in the registry.
    """
    def decorator(model_cls: Type[ModelInterface]) -> Type[ModelInterface]:
        instance = model_cls()
        _model_registry[name] = instance
        return model_cls
    return decorator


def get_model(name: str) -> ModelInterface:
    """
    Retrieve a registered model by name.
    """
    return _model_registry[name]


def list_models() -> List[str]:
    """
    List all registered model names.
    """
    return list(_model_registry.keys())
