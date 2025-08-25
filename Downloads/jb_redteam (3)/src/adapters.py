
import os, json, subprocess, shlex
class Target:
    def infer(self, texts): raise NotImplementedError
class LocalDetectorTarget(Target):
    def __init__(self, model_dir):
        from jb_prototype.src.detector_core import Detector
        self.det=Detector(model_dir); self.det.load()
    def infer(self, texts):
        pred, score=self.det.predict(texts); return list(map(int,pred)), list(map(float,score))
