from .base import BasePredictor


class DummyPredictor(BasePredictor):
    def __init__(self, **_):
        pass

    def predict(self, image, language):
        return ""
