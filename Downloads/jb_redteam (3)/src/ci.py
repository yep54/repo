
import sys, json
from .adapters import LocalDetectorTarget
from .generator import sample_generate
def run_ci(model_dir, db_txt, budget=200, threshold=0.05):
    tgt=LocalDetectorTarget(model_dir); prompts=sample_generate(db_txt, n=budget, mutate_k=3); preds,_=tgt.infer(prompts)
    fns=sum(1 for p in preds if p==0); fn_rate=fns/len(prompts); print(json.dumps({"budget":budget,"fns":fns,"fn_rate":fn_rate})); return 1 if fn_rate>threshold else 0
