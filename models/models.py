from types import Model
import base

__all__ = [
    "Model",
    "MODELS",
    "get_model"
]

MODELS = {
    Model.RANDOM:
        ('RandomFailureModel'),
    Model.GRAPH:
        ('GraphFailureModel'),
    Model.NETWORK_OUTAGE:
        ('NetworkFailureModel'),
    Model.KILL_PROCESSES:
        ('ProcessesFailureModel')
}

def get_model(model):
    return getattr(base, MODELS[model])
