from .base import BasePredictor


def get_predictor(name: str, **kwargs) -> BasePredictor:
    if name == "dummy":
        from .dummy import DummyPredictor
        return DummyPredictor(**kwargs)
    if name == "qwen_vl":
        from .qwen_vl import QwenVLPredictor
        kwargs.setdefault("model_id", "Qwen/Qwen2.5-VL-7B-Instruct")
        return QwenVLPredictor(**kwargs)
    if name == "qwen_vl_tiny":
        from .qwen_vl import QwenVLPredictor
        kwargs.setdefault("model_id", "Qwen/Qwen2.5-VL-3B-Instruct")
        return QwenVLPredictor(**kwargs)
    raise ValueError(
        f"Unknown predictor '{name}'. Available: dummy, qwen_vl, qwen_vl_tiny"
    )
