
from flask import Flask, request, jsonify
from .adapters import LocalDetectorTarget
def create_app(model_dir):
    app=Flask(__name__); tgt=LocalDetectorTarget(model_dir)
    @app.post("/infer")
    def infer():
        data=request.get_json(force=True); texts=data.get("texts",[]); preds,scores=tgt.infer(texts); return jsonify({"predictions":preds,"scores":scores})
    return app
